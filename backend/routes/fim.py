"""
fim.py — File Integrity Monitoring events.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.services.db import query_all

fim_bp = Blueprint("fim", __name__, url_prefix="/api/fim")


@fim_bp.route("", methods=["GET"])
def get_fim():
    """List FIM events, optionally filtered by hostname, capped at 200 rows."""
    hostname = request.args.get("hostname", "")
    params = []
    where = ""

    if hostname:
        where = "WHERE hostname = %s"
        params = [hostname]

    rows = query_all(
        f"SELECT * FROM fim_events {where} ORDER BY timestamp DESC LIMIT 200",
        tuple(params)
    )
    for r in rows:
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()
    return jsonify(rows), 200