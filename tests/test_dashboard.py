"""
Dashboard route tests.
"""


def test_dashboard_stats(client):
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.get_json()
    for key in ("total_events", "total_alerts", "new_alerts",
                "critical_alerts", "agents_online", "agents_offline",
                "threat_index"):
        assert key in data


def test_dashboard_traffic(client):
    response = client.get("/api/dashboard/traffic")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)