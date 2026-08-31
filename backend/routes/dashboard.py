"""
dashboard.py — Dashboard aggregate stats routes.
"""
from flask import Blueprint, jsonify

from backend.services.db import query_one, query_all

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
def dashboard_stats():
    """Aggregate counts for the main dashboard cards."""
    total_events = query_one("SELECT COUNT(*) as count FROM events")
    total_alerts = query_one("SELECT COUNT(*) as count FROM alerts")
    critical_alerts = query_one(
        "SELECT COUNT(*) as count FROM alerts WHERE severity = 'Critical'"
    )
    agents_online = query_one(
        "SELECT COUNT(*) as count FROM agents WHERE status = 'Online'"
    )
    agents_offline = query_one(
        "SELECT COUNT(*) as count FROM agents WHERE status = 'Offline'"
    )
    open_vulnerabilities = query_one(
        "SELECT COUNT(*) as count FROM vulnerabilities WHERE status = 'Open'"
    )

    return jsonify({
        "total_events": total_events["count"] if total_events else 0,
        "total_alerts": total_alerts["count"] if total_alerts else 0,
        "critical_alerts": critical_alerts["count"] if critical_alerts else 0,
        "agents_online": agents_online["count"] if agents_online else 0,
        "agents_offline": agents_offline["count"] if agents_offline else 0,
        "open_vulnerabilities": open_vulnerabilities["count"] if open_vulnerabilities else 0,
    }), 200


@dashboard_bp.route("/traffic", methods=["GET"])
def dashboard_traffic():
    """Hourly event traffic for the last 24 hours, grouped by action taken."""
    rows = query_all("""
        SELECT
            DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour,
            action_taken,
            COUNT(*) as count
        FROM events
        WHERE timestamp >= NOW() - INTERVAL 24 HOUR
        GROUP BY hour, action_taken
        ORDER BY hour ASC
    """)
    return jsonify(rows), 200