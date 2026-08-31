"""
alerts.py — Security alert management (qualified, risk-scored events).
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.services.db import query_one, query_all, execute

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


# TODO: import notify_alert once Haytam's response/telegram/telegram_service.py exists
# from backend.response.telegram.telegram_service import notify_alert


@alerts_bp.route("", methods=["GET"])
def get_alerts():
    """Filterable list of alerts, ordered by newest first."""
    status = request.args.get("status", "")
    severity = request.args.get("severity", "")

    where_clauses = []
    params = []
    if status and status != "All":
        where_clauses.append("status = %s")
        params.append(status)
    if severity and severity != "All":
        where_clauses.append("severity = %s")
        params.append(severity)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    rows = query_all(
        f"SELECT * FROM alerts {where_sql} ORDER BY timestamp DESC",
        tuple(params)
    )

    for r in rows:
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
        r["xgboost_probability"] = float(r.get("xgboost_probability") or 0)

    return jsonify(rows), 200


@alerts_bp.route("", methods=["POST"])
def post_alert():
    """
    Receives a new alert from the analysis pipeline.
    Should trigger a notification if critical (TODO once notify_alert exists).
    """
    data = request.get_json(force=True)
    required = ["title", "severity", "description", "rule_id", "xgboost_probability"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    ai_content = data.get("ai_report_content")
    ai_report_id = None

    alert_id = execute("""
        INSERT INTO alerts
            (title, severity, description, rule_id, timestamp, xgboost_probability,
             analyst_assigned, status, ai_report_id)
        VALUES (%s, %s, %s, %s, NOW(), %s, 'Auto-Pipeline', 'New', NULL)
    """, (
        data["title"], data["severity"], data["description"],
        data["rule_id"], data["xgboost_probability"]
    ))

    # If the pipeline already generated an AI report, save it and link it
    if ai_content:
        ai_report_id = execute("""
            INSERT INTO ai_reports (alert_id, generated_at, markdown_content)
            VALUES (%s, NOW(), %s)
        """, (alert_id, ai_content))

        execute("UPDATE alerts SET ai_report_id = %s WHERE id = %s",
                (ai_report_id, alert_id))

    # TODO: call notify_alert(alert_data) once Haytam's Telegram service exists
    # alert_data = {
    #     "title": data["title"],
    #     "severity": data["severity"],
    #     "description": data["description"],
    #     "rule_id": data["rule_id"],
    #     "xgboost_probability": data["xgboost_probability"],
    #     "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    # }
    # notify_alert(alert_data)

    return jsonify({"id": alert_id, "ai_report_id": ai_report_id, "status": "created"}), 201


@alerts_bp.route("/<int:alert_id>/status", methods=["PUT"])
def update_alert_status(alert_id: int):
    """Quick status-only update."""
    data = request.get_json(force=True)
    new_status = data.get("status")
    if new_status not in ("New", "Acknowledged", "Resolved"):
        return jsonify({"error": "Invalid status"}), 400

    execute("UPDATE alerts SET status = %s WHERE id = %s", (new_status, alert_id))
    return jsonify({"id": alert_id, "status": new_status}), 200


@alerts_bp.route("/<int:alert_id>", methods=["PUT", "OPTIONS"])
def update_alert(alert_id: int):
    """Fuller update: status + analyst assignment."""
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json(silent=True) or {}
        existing = query_one("SELECT * FROM alerts WHERE id = %s", (alert_id,))
        if not existing:
            return jsonify({"error": f"Alert '{alert_id}' not found."}), 404

        status = data.get("status", existing.get("status", "New"))
        analyst = data.get("analyst_assigned", existing.get("analyst_assigned", "Unassigned"))

        execute(
            "UPDATE alerts SET status = %s, analyst_assigned = %s WHERE id = %s",
            (status, analyst, alert_id)
        )
        updated = query_one("SELECT * FROM alerts WHERE id = %s", (alert_id,))
        if isinstance(updated.get("timestamp"), datetime):
            updated["timestamp"] = updated["timestamp"].isoformat()
        print(f"[ALERT UPDATE] #{alert_id} -> Status: {status}, Analyst: {analyst}")
        return jsonify(updated), 200
    except Exception as e:
        print(f"[ALERT UPDATE ERROR] {e}")
        return jsonify({"error": str(e)}), 500