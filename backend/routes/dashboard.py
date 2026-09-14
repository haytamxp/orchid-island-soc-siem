"""
dashboard.py — Dashboard aggregate stats routes.
"""
from flask import Blueprint, jsonify
import psutil

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
            CAST(SUM(CASE WHEN action_taken IN ('Dropped','Blocked','Killed','detected') THEN 1 ELSE 0 END) AS UNSIGNED) AS blocked,
            CAST(SUM(CASE WHEN action_taken IN ('Allowed','Logged') THEN 1 ELSE 0 END) AS UNSIGNED) AS allowed
        FROM events
        WHERE timestamp >= NOW() - INTERVAL 24 HOUR
        GROUP BY DATE_FORMAT(timestamp, '%H:00')
        ORDER BY hour
    """)
    return jsonify(rows), 200


@dashboard_bp.route("/host-resources", methods=["GET"])
def dashboard_host_resources():
    """Live CPU/RAM usage of the machine this Flask process is running on.

    Reads real system telemetry via psutil — this machine IS the SIEM's
    host, so this reflects the actual box running Suricata/Wazuh/Zeek,
    not a placeholder or a specific agent lookup.
    """
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram_usage = psutil.virtual_memory().percent

    return jsonify({
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
    }), 200


@dashboard_bp.route("/attack-vectors", methods=["GET"])
def dashboard_attack_vectors():
    """Real breakdown of event categories in the last 24h, for the dashboard pie chart.

    Same 24h window as /traffic, so both panels tell a consistent story:
    empty when the pipeline's been idle, populated once real alerts flow in.
    """
    rows = query_all("""
        SELECT category AS name, COUNT(*) AS value
        FROM events
        WHERE timestamp >= NOW() - INTERVAL 24 HOUR
        GROUP BY category
        ORDER BY value DESC
        LIMIT 6
    """)
    return jsonify(rows), 200