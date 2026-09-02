"""
Alerts route tests.
"""


def test_get_alerts(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_post_alert_missing_fields(client):
    response = client.post("/api/alerts", json={"title": "Incomplete"})
    assert response.status_code == 400


def test_post_and_update_alert(client):
    create = client.post("/api/alerts", json={
        "title": "Pytest Test Alert",
        "severity": "Low",
        "description": "Created by automated test",
        "rule_id": "9999",
        "xgboost_probability": 0.1,
    })
    assert create.status_code == 201
    alert_id = create.get_json()["id"]

    update = client.put(f"/api/alerts/{alert_id}/status", json={"status": "Resolved"})
    assert update.status_code == 200
    assert update.get_json()["status"] == "Resolved"