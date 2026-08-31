"""
agents.py — Monitored agent fleet management (Wazuh nodes).
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.services.db import query_one, query_all, execute

agents_bp = Blueprint("agents", __name__, url_prefix="/api/agents")


# TODO: import notify_agent_offline once Haytam's response/telegram/telegram_service.py exists
# from backend.response.telegram.telegram_service import notify_agent_offline


@agents_bp.route("", methods=["GET"])
def get_agents():
    """List all monitored agents, online ones first."""
    rows = query_all("SELECT * FROM agents ORDER BY status DESC, name")
    for r in rows:
        if isinstance(r.get("last_keep_alive"), datetime):
            r["last_keep_alive"] = r["last_keep_alive"].isoformat()
        r["cpu_usage"] = float(r.get("cpu_usage") or 0)
        r["ram_usage"] = float(r.get("ram_usage") or 0)
    return jsonify(rows), 200


@agents_bp.route("/<string:agent_id>/status", methods=["PUT", "OPTIONS"])
@agents_bp.route("/<string:agent_id>", methods=["PUT", "OPTIONS"])
def update_agent_status(agent_id: str):
    """Update an agent's status (Online/Offline)."""
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    status = data.get("status", "Online")
    last_keep_alive = data.get("last_keep_alive")

    agent = query_one("SELECT * FROM agents WHERE id = %s", (agent_id,))
    if not agent:
        return jsonify({"error": f"Agent '{agent_id}' not found."}), 404

    if last_keep_alive:
        execute(
            "UPDATE agents SET status = %s, last_keep_alive = NOW() WHERE id = %s",
            (status, agent_id)
        )
    else:
        execute(
            "UPDATE agents SET status = %s WHERE id = %s",
            (status, agent_id)
        )

    updated = query_one("SELECT * FROM agents WHERE id = %s", (agent_id,))
    if isinstance(updated.get("last_keep_alive"), datetime):
        updated["last_keep_alive"] = updated["last_keep_alive"].isoformat()

    if status == "Offline":
        # TODO: notify_agent_offline(agent["name"], agent["ip_address"])
        print(f"[AGENT OFFLINE] {agent['name']} ({agent['ip_address']}) — notification TODO")

    print(f"[AGENT UPDATE] {agent_id} -> Status: {status}")
    return jsonify(updated), 200