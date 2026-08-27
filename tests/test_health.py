"""
Basic backend health tests.
"""

from backend.app import create_app


def test_health_endpoint():
    """
    The backend health endpoint must return HTTP 200.
    """

    app = create_app()

    app.config.update(
        TESTING=True
    )

    client = app.test_client()

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data is not None
    assert data["status"] == "ok"