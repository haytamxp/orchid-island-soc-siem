"""
dashboard.py — Dashboard aggregate stats routes.
"""
from flask import Blueprint, jsonify

from backend.services.db import query_one, query_all

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
def dashboard_stats():
    """Aggregate counts + threat index for the main dashboard cards."""
    total_events = query_one("SELECT COUNT(*) AS n FROM events")["n"]
    total_alerts = query_one("SELECT COUNT(*) AS n FROM alerts")["n"]
    new_alerts = query_one("SELECT COUNT(*) AS n FROM alerts WHERE status='New'")["n"]
    critical_alerts = query_one(
        "SELECT COUNT(*) AS n FROM alerts WHERE severity='Critical'"
    )["n"]
    agents_online = query_one(
        "SELECT COUNT(*) AS n FROM agents WHERE status='Online'"
    )["n"]
    agents_offline = query_one(
        "SELECT COUNT(*) AS n FROM agents WHERE status='Offline'"
    )["n"]

    # Threat Index = average risk score of alerts that aren't Resolved yet
    ti_row = query_one(
        "SELECT AVG(xgboost_probability) AS avg FROM alerts WHERE status != 'Resolved'"
    )
    threat_index = round(ti_row["avg"] or 0, 1)

    return jsonify({
        "total_events": total_events,
        "total_alerts": total_alerts,
        "new_alerts": new_alerts,
        "critical_alerts": critical_alerts,
        "agents_online": agents_online,
        "agents_offline": agents_offline,
        "threat_index": threat_index,
    }), 200


@dashboard_bp.route("/traffic", methods=["GET"])
def dashboard_traffic():
    """Hourly event traffic for the last 24 hours — blocked vs allowed, for the chart."""
    rows = query_all("""
        SELECT
            DATE_FORMAT(timestamp, '%H:00') AS hour,
            COUNT(*) AS total,
            CAST(SUM(CASE WHEN action_taken IN ('Dropped','Blocked','Killed') THEN 1 ELSE 0 END) AS UNSIGNED) AS blocked,
            CAST(SUM(CASE WHEN action_taken IN ('Allowed','Logged') THEN 1 ELSE 0 END) AS UNSIGNED) AS allowed
        FROM events
        WHERE timestamp >= NOW() - INTERVAL 24 HOUR
        GROUP BY DATE_FORMAT(timestamp, '%H:00')
        ORDER BY hour
    """)
    return jsonify(rows), 200