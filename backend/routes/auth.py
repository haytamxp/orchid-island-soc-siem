"""
auth.py — Authentication routes.
"""
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from backend.services.db import query_one

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    """Verify authentication with hashed password and MFA."""
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    mfa_token = data.get("mfa_token", "").strip()

    if not username or not password or not mfa_token:
        return jsonify({"error": "Missing required security fields."}), 400

    user = query_one("SELECT * FROM users WHERE username = %s", (username,))
    if not user:
        return jsonify({"error": "AUTH FAILED: invalid credentials or MFA code."}), 401

    if not check_password_hash(user.get("password", ""), password):
        return jsonify({"error": "AUTH FAILED: invalid credentials or MFA code."}), 401

    mfa_hash = hashlib.sha256(mfa_token.encode()).hexdigest()
    stored_mfa = user.get("mfa_token", "")
    if stored_mfa != mfa_hash and stored_mfa != mfa_token:
        return jsonify({"error": "AUTH FAILED: invalid MFA code."}), 401

    session_token = f"authenticated_token_{hashlib.sha256((username + str(datetime.now())).encode()).hexdigest()[:32]}"

    return jsonify({
        "status": "authenticated",
        "session_token": session_token,
        "username": username,
        "role": user.get("role", "admin"),
    }), 200