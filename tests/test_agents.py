"""
Agents route tests.
"""


def test_get_agents(client):
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_update_nonexistent_agent(client):
    response = client.put("/api/agents/agt-does-not-exist/status",
                           json={"status": "Offline"})
    assert response.status_code == 404