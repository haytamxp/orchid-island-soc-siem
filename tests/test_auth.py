"""
Auth route tests.
"""


def test_login_missing_fields(client):
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 400


def test_login_unknown_user(client):
    response = client.post("/api/auth/login", json={
        "username": "nonexistent_user_xyz",
        "password": "whatever",
        "mfa_token": "000000",
    })
    assert response.status_code == 401


def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "definitely_wrong_password",
        "mfa_token": "000000",
    })
    assert response.status_code == 401


def test_login_success(client):
    """Requires the 'admin' / 'admin123' seed user — run
    `python3 -m backend.scripts.seed_users` first if this fails."""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
        "mfa_token": "000000",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "authenticated"
    assert "session_token" in data