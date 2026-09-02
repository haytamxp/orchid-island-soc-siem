"""
Vulnerabilities route tests.
"""


def test_get_vulnerabilities(client):
    response = client.get("/api/vulnerabilities")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_update_nonexistent_vulnerability(client):
    response = client.put("/api/vulnerabilities/vuln-does-not-exist",
                           json={"status": "Patched"})
    assert response.status_code == 404