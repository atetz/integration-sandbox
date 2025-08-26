from fastapi.testclient import TestClient

from integrationsandbox.main import app
from integrationsandbox.tms.models import TmsShipment

client = TestClient(app)


def test_create_shipment(mock_shipments):
    for shipment in mock_shipments:
        shipment_data = shipment.model_dump(mode="json")
        response = client.post("/api/v1/tms/shipments/", json=shipment_data)

        assert response.status_code == 201
        data = response.json()
        assert data["external_reference"] == shipment.external_reference
        assert data["customer"]["carrier"] == shipment.customer.carrier
        assert len(data["line_items"]) == len(shipment.line_items)


def test_fail_create_multiple_shipment(mock_shipments):
    shipment_data = [shipment.model_dump(mode="json") for shipment in mock_shipments]
    response = client.post("/api/v1/tms/shipments/", json=shipment_data)
    assert response.status_code == 422


def test_seed_shipments():
    seed_data = {"count": 2}

    response = client.post("/api/v1/tms/shipments/seed", json=seed_data)

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert all(shipment["id"] for shipment in data)


def test_get_shipments(persisted_shipments):
    response = client.get("/api/v1/tms/shipments/")

    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert all(
        isinstance(TmsShipment.model_validate(shipment), TmsShipment)
        for shipment in data
    )


def test_get_shipments_by_id(persisted_shipments):
    expected_shipment = persisted_shipments[0]

    response = client.get("/api/v1/tms/shipments/", params={"id": expected_shipment.id})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == expected_shipment.id


def test_get_shipments_by_nonexistent_id():
    response = client.get("/api/v1/tms/shipments/", params={"id": "nonexistent-id"})
    assert response.status_code == 200
    assert response.json() is None


def test_get_shipments_by_limit(persisted_shipments):
    # Ensure we have at least 2 shipments
    expected_count = min(2, len(persisted_shipments))
    response = client.get("/api/v1/tms/shipments/", params={"limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert len(data) == expected_count


def test_get_shipments_by_skip(persisted_shipments):
    total_persisted = len(persisted_shipments)
    
    # Get all shipments with limit equal to persisted count
    response = client.get("/api/v1/tms/shipments/", params={"limit": total_persisted})
    assert response.status_code == 200
    data = response.json()
    count = len(data) if data else 0
    
    # Skip 2 shipments
    skip_count = min(2, total_persisted)  # Don't skip more than we have
    response = client.get("/api/v1/tms/shipments/", params={"skip": skip_count, "limit": total_persisted})
    skipped_data = response.json()
    skipped_count = len(skipped_data) if skipped_data else 0
    
    # Should have skip_count fewer records
    expected_count = max(0, count - skip_count)
    assert expected_count == skipped_count


def test_get_new_shipments(persisted_processed_shipments):
    # Also create some unprocessed shipments
    seed_data = {"count": 2}
    client.post("/api/v1/tms/shipments/seed", json=seed_data)
    
    response = client.get("/api/v1/tms/shipments/new/")

    assert response.status_code == 200
    data = response.json()
    assert data is not None

    processed_ids = {s.id for s in persisted_processed_shipments}
    new_ids = {s["id"] for s in data}

    assert processed_ids.isdisjoint(new_ids)


def test_incoming_event_validation(persisted_shipments, persisted_broker_events):
    shipment = persisted_shipments[0]
    broker_event = persisted_broker_events[0]

    event_data = {
        "event_type": "BOOKED",
        "created_at": broker_event.situation.registrationDate.isoformat(),
        "occured_at": broker_event.situation.actualDate.isoformat(),
        "external_order_reference": broker_event.order.reference,
        "source": "broker",
        "location": None,
    }

    response = client.post(f"/api/v1/tms/event/{shipment.id}", json=event_data)
    print(response.json())
    assert response.status_code == 202


def test_incoming_event_validation_missing_broker_event():
    event_data = {
        "event_type": "BOOKED",
        "created_at": "2024-01-15T10:00:00",
        "occured_at": "2024-01-15T09:30:00",
        "external_order_reference": None,
        "source": "broker",
        "location": None,
    }

    response = client.post("/api/v1/tms/event/nonexistent-id", json=event_data)

    assert response.status_code == 422


def test_seed_shipments_with_custom_count():
    seed_data = {"count": 10}

    response = client.post("/api/v1/tms/shipments/seed", json=seed_data)

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 10
    assert all(shipment["id"] for shipment in data)
    assert all("customer" in shipment for shipment in data)


def test_seed_shipments_invalid_count():
    seed_data = {"count": 0}

    response = client.post("/api/v1/tms/shipments/seed", json=seed_data)

    assert response.status_code == 422


def test_create_shipment_missing_required_fields():
    incomplete_data = {
        "mode": "FTL",
    }

    response = client.post("/api/v1/tms/shipments/", json=incomplete_data)
    assert response.status_code == 422
