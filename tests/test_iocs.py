"""
IOC route tests.
"""


def test_get_iocs(client):
    response = client.get("/api/iocs")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_ioc_full_cycle(client):
    create = client.post("/api/iocs", json={
        "value": "203.0.113.99",
        "type": "IP",
        "threat_actor": "Pytest",
        "description": "Test IOC",
    })
    assert create.status_code == 201
    ioc_id = create.get_json()["id"]

    delete = client.delete(f"/api/iocs/{ioc_id}")
    assert delete.status_code == 200
    assert delete.get_json()["status"] == "deleted"


def test_delete_nonexistent_ioc(client):
    response = client.delete("/api/iocs/ioc-does-not-exist")
    assert response.status_code == 404