"""
events.py — Raw security event ingestion and listing.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.services.db import query_one, query_all, execute

events_bp = Blueprint("events", __name__, url_prefix="/api/events")


@events_bp.route("", methods=["GET"])
def get_events():
    """Paginated, filterable list of raw security events."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    severity = request.args.get("severity", "")
    search = request.args.get("search", "")
    offset = (page - 1) * per_page

    where_clauses = []
    params = []

    if severity and severity != "All":
        where_clauses.append("severity = %s")
        params.append(severity)
    if search:
        where_clauses.append("(hostname LIKE %s OR src_ip LIKE %s OR category LIKE %s)")
        like = f"%{search}%"
        params.extend([like, like, like])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    total = query_one(f"SELECT COUNT(*) AS n FROM events {where_sql}", tuple(params))["n"]
    rows = query_all(
        f"SELECT * FROM events {where_sql} ORDER BY timestamp DESC LIMIT %s OFFSET %s",
        tuple(params) + (per_page, offset)
    )

    # Convert datetime objects to ISO strings for JSON serialization
    for r in rows:
        if isinstance(r.get("timestamp"), datetime):
            r["timestamp"] = r["timestamp"].isoformat()

    return jsonify({"total": total, "page": page, "data": rows}), 200


@events_bp.route("", methods=["POST"])
def post_event():
    """Ingests a new event from an agent (Wazuh/Suricata pipeline)."""
    data = request.get_json(force=True)
    required = ["hostname", "src_ip", "dest_ip", "dest_port",
                "category", "rule_id", "severity", "action_taken"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    event_id = execute("""
        INSERT INTO events
            (timestamp, hostname, src_ip, dest_ip, dest_port, category, rule_id, severity, action_taken)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["hostname"], data["src_ip"], data["dest_ip"],
        data["dest_port"], data["category"], data["rule_id"],
        data["severity"], data["action_taken"]
    ))

    # Auto-register/update the agent that produced this event
    try:
        hostname = data["hostname"]
        src_ip = data["src_ip"]
        agent_id = f"agt-{hostname}"
        execute("""
            INSERT INTO agents (id, name, ip_address, status, os, last_keep_alive, cpu_usage, ram_usage)
            VALUES (%s, %s, %s, 'Online', 'Linux Agent', NOW(), 15.0, 35.0)
            ON DUPLICATE KEY UPDATE status='Online', ip_address=%s, last_keep_alive=NOW()
        """, (agent_id, hostname, src_ip, src_ip))
    except Exception as e:
        print(f"[AGENT AUTO-REGISTER] {e}")

    return jsonify({"id": event_id, "status": "created"}), 201