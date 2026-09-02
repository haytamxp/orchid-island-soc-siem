"""
Events route tests.
"""


def test_get_events(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.get_json()
    assert "total" in data
    assert "data" in data


def test_post_event_missing_fields(client):
    response = client.post("/api/events", json={"hostname": "test-host"})
    assert response.status_code == 400


def test_post_event_success(client):
    response = client.post("/api/events", json={
        "hostname": "pytest-host",
        "src_ip": "10.0.0.99",
        "dest_ip": "10.0.0.1",
        "dest_port": 443,
        "category": "Test Event",
        "rule_id": "9999",
        "severity": "Low",
        "action_taken": "Logged",
    })
    assert response.status_code == 201
    assert "id" in response.get_json()