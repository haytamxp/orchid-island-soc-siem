"""
iocs.py — Threat Intelligence: Indicators of Compromise (IOCs).
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.services.db import query_one, query_all, execute

iocs_bp = Blueprint("iocs", __name__, url_prefix="/api/iocs")


@iocs_bp.route("", methods=["GET"])
def get_iocs():
    """Filterable list of IOCs, newest first."""
    ioc_type = request.args.get("type", "")
    params = []
    where = ""

    if ioc_type and ioc_type != "All":
        where = "WHERE type = %s"
        params = [ioc_type]

    rows = query_all(
        f"SELECT * FROM threat_intel_iocs {where} ORDER BY date_added DESC",
        tuple(params)
    )
    for r in rows:
        if isinstance(r.get("date_added"), datetime):
            r["date_added"] = r["date_added"].isoformat()
    return jsonify(rows), 200


@iocs_bp.route("", methods=["POST"])
def add_ioc():
    """Registers a new IOC."""
    data = request.get_json(silent=True) or {}
    if not data.get("value") or not data.get("type"):
        return jsonify({"error": "value and type are required"}), 400

    ioc_id = f"ioc-{int(datetime.now().timestamp() * 1000)}"
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    execute("""
        INSERT INTO threat_intel_iocs (id, value, type, threat_actor, description, date_added)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (
        ioc_id,
        data["value"],
        data["type"],
        data.get("threat_actor", "Unknown"),
        data.get("description", "")
    ))

    new_ioc = {
        "id": ioc_id,
        "value": data["value"],
        "type": data["type"],
        "threat_actor": data.get("threat_actor", "Unknown"),
        "description": data.get("description", ""),
        "date_added": now_str,
    }
    print(f"[IOC] Saved: {ioc_id} ({data.get('value')})")
    return jsonify(new_ioc), 201


@iocs_bp.route("/<ioc_id>", methods=["DELETE", "OPTIONS"])
def delete_ioc(ioc_id: str):
    """Deletes an IOC."""
    if request.method == "OPTIONS":
        return "", 200

    existing = query_one("SELECT id FROM threat_intel_iocs WHERE id = %s", (ioc_id,))
    if not existing:
        return jsonify({"error": f"IOC '{ioc_id}' not found."}), 404

    execute("DELETE FROM threat_intel_iocs WHERE id = %s", (ioc_id,))
    print(f"[IOC] Deleted: {ioc_id}")
    return jsonify({"status": "deleted", "id": ioc_id}), 200