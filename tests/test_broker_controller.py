from fastapi.testclient import TestClient

from integrationsandbox.broker.service import apply_shipment_mapping_rules
from integrationsandbox.main import app

client = TestClient(app)


def test_create_event_endpoint(mock_events):
    mock_event = mock_events[0]
    event_data = mock_event.model_dump(mode="json", exclude={"id"})

    response = client.post("/api/v1/broker/events/", json=event_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"]  # UUID was generated
    assert data["shipmentId"] == mock_event.shipmentId
    assert data["carrier"] == mock_event.carrier


def test_seed_events_endpoint(persisted_shipments):
    shipment = persisted_shipments[0]
    seed_data = {"event": "ORDER_CREATED", "shipment_ids": [shipment.id]}

    response = client.post("/api/v1/broker/events/seed", json=seed_data)

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["shipmentId"] == shipment.id


def test_get_events_endpoint(persisted_broker_events):
    response = client.get("/api/v1/broker/events/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(persisted_broker_events)


def test_get_events_with_filters(persisted_broker_events):
    response = client.get("/api/v1/broker/events/?event=ORDER_CREATED")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have at least the persisted events since they're all ORDER_CREATED
    assert len(data) >= len(persisted_broker_events)


def test_incoming_order_validation_endpoint(persisted_shipments):
    shipment = persisted_shipments[0]

    mapping = apply_shipment_mapping_rules(shipment)

    broker_order = {
        "meta": {
            "senderId": "TEST_SENDER",
            "messageDate": "2024-01-15T10:00:00",
            "messageReference": "MSG001",
            "messageFunction": mapping["meta_message_function"],
        },
        "shipment": {
            "reference": mapping["shipment_reference"],
            "carrier": mapping["shipment_carrier"],
            "transportMode": mapping["shipment_transportmode"],
            "orders": [
                {
                    "reference": mapping["order_reference"],
                    "pickUp": mapping["order_pickup_details"].model_dump(mode="json"),
                    "consignee": mapping["order_consignee_details"].model_dump(
                        mode="json"
                    ),
                    "goodsDescription": "|".join(mapping["order_goods_description"]),
                    "quantity": mapping["order_quantities"].model_dump(mode="json"),
                    "handlingUnits": [
                        unit.model_dump(mode="json")
                        for unit in mapping["order_handling_units"]
                    ],
                }
            ],
        },
    }

    response = client.post("/api/v1/broker/order/", json=broker_order)

    assert response.status_code == 202


def test_incoming_order_validation_missing_shipment():
    broker_order = {
        "meta": {
            "senderId": "TEST_SENDER",
            "messageDate": "2024-01-15T10:00:00",
            "messageReference": "MSG001",
            "messageFunction": 9,
        },
        "shipment": {
            "reference": "nonexistent-shipment-id",
            "carrier": "Test Carrier",
            "transportMode": "ROAD",
            "orders": [],
        },
    }

    response = client.post("/api/v1/broker/order/", json=broker_order)

    assert response.status_code == 422
    assert "not found" in response.json()["detail"]


def test_build_events_integration(mock_events):
    assert len(mock_events) >= 1
    for event in mock_events:
        assert hasattr(event, "shipmentId")
        assert hasattr(event, "owner")
        assert hasattr(event, "situation")
        assert hasattr(event, "carrier")
        assert event.owner == "Adam's logistics"
        assert event.situation.event.value == "ORDER_CREATED"
