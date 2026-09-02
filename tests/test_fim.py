"""
FIM route tests.
"""


def test_get_fim(client):
    response = client.get("/api/fim")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)