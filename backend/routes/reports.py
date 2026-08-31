"""
reports.py — AI-generated incident report listing and saving.

Note: the old repo's `/api/reports/generate` endpoint (a templated
Markdown fallback, no real AI involved) is intentionally NOT ported here.
Real report generation belongs to Haytam's backend/ai/analyzer.py
(Gemini-based). This file only handles listing and saving reports that
were already generated elsewhere.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.services.db import execute, query_all

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports", methods=["GET"])
@reports_bp.route("/api/ai-reports", methods=["GET"])
def get_all_reports():
    """Returns all saved AI reports, newest first."""
    rows = query_all("SELECT * FROM ai_reports ORDER BY id DESC")
    for r in rows:
        if isinstance(r.get("generated_at"), datetime):
            r["generated_at"] = r["generated_at"].isoformat()
    return jsonify(rows), 200


@reports_bp.route("/api/reports", methods=["POST"])
@reports_bp.route("/api/ai-reports", methods=["POST"])
def save_ai_report():
    """Saves an AI-generated report and links it to its alert."""
    data = request.get_json(silent=True) or {}
    alert_id = data.get("alert_id")
    content = data.get("markdown_content")
    if not alert_id or not content:
        return jsonify({"error": "alert_id and markdown_content are required"}), 400

    report_id = execute("""
        INSERT INTO ai_reports (alert_id, generated_at, markdown_content)
        VALUES (%s, NOW(), %s)
    """, (alert_id, content))
    execute("UPDATE alerts SET ai_report_id = %s WHERE id = %s", (report_id, alert_id))
    print(f"[REPORT] AI report #{report_id} linked to alert #{alert_id}")
    return jsonify({
        "id": report_id,
        "alert_id": alert_id,
        "markdown_content": content,
        "status": "saved"
    }), 201