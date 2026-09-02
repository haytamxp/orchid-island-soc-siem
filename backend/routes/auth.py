"""
auth.py — Authentication routes.
"""
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from backend.services.db import query_one

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _client_ip() -> str:
    return request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    """Verify authentication with hashed password and MFA."""
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    mfa_token = data.get("mfa_token", "").strip()
    ip = _client_ip()

    if not username or not password or not mfa_token:
        print(f"[AUTH] LOGIN REJECTED from {ip}: missing fields "
              f"(username={bool(username)}, password={bool(password)}, mfa={bool(mfa_token)})")
        return jsonify({"error": "Missing required security fields."}), 400

    user = query_one("SELECT * FROM users WHERE username = %s", (username,))
    if not user:
        print(f"[AUTH] LOGIN FAILED from {ip}: unknown user {username!r}")
        return jsonify({"error": "AUTH FAILED: invalid credentials or MFA code."}), 401

    if not check_password_hash(user.get("password", ""), password):
        print(f"[AUTH] LOGIN FAILED from {ip}: wrong password for {username!r} "
              f"(received {len(password)} chars)")
        return jsonify({"error": "AUTH FAILED: invalid credentials or MFA code."}), 401

    mfa_hash = hashlib.sha256(mfa_token.encode()).hexdigest()
    stored_mfa = user.get("mfa_token", "")
    if stored_mfa != mfa_hash and stored_mfa != mfa_token:
        print(f"[AUTH] LOGIN FAILED from {ip}: wrong MFA code for {username!r} "
              f"(received {len(mfa_token)} chars)")
        return jsonify({"error": "AUTH FAILED: invalid MFA code."}), 401

    session_token = f"authenticated_token_{hashlib.sha256((username + str(datetime.now())).encode()).hexdigest()[:32]}"

    print(f"[AUTH] LOGIN OK from {ip}: {username!r} (role {user.get('role', 'admin')})")
    return jsonify({
        "status": "authenticated",
        "session_token": session_token,
        "username": username,
        "role": user.get("role", "admin"),
    }), 200
