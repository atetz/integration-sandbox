from fastapi.testclient import TestClient

from integrationsandbox.main import app

client = TestClient(app)


def test_nuke(persisted_shipments, persisted_broker_events):
    assert len(persisted_shipments) > 0
    assert len(persisted_broker_events) > 0

    response = client.delete("/api/v1/nuke")

    assert response.status_code == 204

    get_shipments_response = client.get("/api/v1/tms/shipments/")
    assert get_shipments_response.status_code == 200
    assert get_shipments_response.json() is None

    get_events_response = client.get("/api/v1/broker/events/")
    assert get_events_response.status_code == 200
    assert get_events_response.json() is None


def test_nuke_requires_auth():
    app.dependency_overrides.clear()

    response = client.delete("/api/v1/nuke")

    assert response.status_code == 401
