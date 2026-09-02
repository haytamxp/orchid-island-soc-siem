"""
vulnerabilities.py — Detected CVE/vulnerability tracking and virtual patching.
"""
from flask import Blueprint, request, jsonify

from backend.services.db import query_one, query_all, execute

vulnerabilities_bp = Blueprint("vulnerabilities", __name__, url_prefix="/api/vulnerabilities")


@vulnerabilities_bp.route("", methods=["GET"])
def get_vulnerabilities():
    """Filterable list of vulnerabilities, most severe first."""
    status = request.args.get("status", "")
    params = []
    where = ""

    if status and status != "All":
        where = "WHERE status = %s"
        params = [status]

    rows = query_all(
        f"SELECT * FROM vulnerabilities {where} ORDER BY cvss_score DESC",
        tuple(params)
    )
    for r in rows:
        r["cvss_score"] = float(r.get("cvss_score") or 0)
    return jsonify(rows), 200


@vulnerabilities_bp.route("/<vuln_id>", methods=["PUT", "OPTIONS"])
def update_vulnerability(vuln_id: str):
    """Applies a virtual patch: updates a vulnerability's status."""
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json(silent=True) or {}
        new_status = data.get("status", "Patched")

        existing = query_one("SELECT * FROM vulnerabilities WHERE id = %s", (vuln_id,))
        if not existing:
            return jsonify({"error": f"Vulnerability '{vuln_id}' not found."}), 404

        execute("UPDATE vulnerabilities SET status = %s WHERE id = %s", (new_status, vuln_id))

        updated = query_one("SELECT * FROM vulnerabilities WHERE id = %s", (vuln_id,))
        if updated:
            updated["cvss_score"] = float(updated.get("cvss_score") or 0)
        print(f"[VULN] Virtual patch applied: {vuln_id} -> {new_status}")
        return jsonify(updated), 200
    except Exception as e:
        print(f"[VULN UPDATE ERROR] {e}")
        return jsonify({"error": str(e)}), 500