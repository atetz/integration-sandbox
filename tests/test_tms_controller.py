from fastapi.testclient import TestClient

from integrationsandbox.main import app

client = TestClient(app)


def test_create_shipment_endpoint():
    shipment_data = {
        "external_reference": "EXT001",
        "mode": "FTL",
        "equipment_type": "TRUCK_AND_TRAILER",
        "customer": {
            "id": "CUST001",
            "name": "Test Customer",
            "carrier": "Test Carrier",
        },
        "loading_meters": 10.0,
        "stops": [
            {
                "type": "PICKUP",
                "location": {
                    "code": "PU001",
                    "name": "Pickup Location",
                    "address": {
                        "address": "123 Pickup St",
                        "city": "Origin City",
                        "postal_code": "12345",
                        "country": "US",
                    },
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                "planned_date": "2024-01-15",
                "planned_time_window_start": "09:00:00",
                "planned_time_window_end": "17:00:00",
            },
            {
                "type": "DELIVERY",
                "location": {
                    "code": "DEL001",
                    "name": "Delivery Location",
                    "address": {
                        "address": "456 Delivery Ave",
                        "city": "Destination City",
                        "postal_code": "67890",
                        "country": "US",
                    },
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                },
                "planned_date": "2024-01-16",
                "planned_time_window_start": "08:00:00",
                "planned_time_window_end": "16:00:00",
            },
        ],
        "line_items": [
            {
                "package_type": "BOX",
                "stackable": True,
                "height": 1.0,
                "length": 1.0,
                "width": 1.0,
                "length_unit": "m",
                "package_weight": 10.0,
                "weight_unit": "kg",
                "description": "Test Item",
                "total_packages": 1,
            }
        ],
    }

    response = client.post("/api/v1/tms/shipments/", json=shipment_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"]  # UUID was generated
    assert data["external_reference"] == "EXT001"
    assert data["customer"]["carrier"] == "Test Carrier"


def test_seed_shipments_endpoint():
    seed_data = {"count": 2}

    response = client.post("/api/v1/tms/shipments/seed", json=seed_data)

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert all(shipment["id"] for shipment in data)


def test_get_shipments_endpoint():
    response = client.get("/api/v1/tms/shipments/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_incoming_event_validation_endpoint():
    # First create a shipment to validate against
    shipment_data = {
        "external_reference": "EXT001",
        "mode": "FTL",
        "equipment_type": "TRUCK_AND_TRAILER",
        "customer": {
            "id": "CUST001",
            "name": "Test Customer",
            "carrier": "Test Carrier",
        },
        "loading_meters": 10.0,
        "stops": [
            {
                "type": "PICKUP",
                "location": {
                    "code": "PU001",
                    "name": "Pickup Location",
                    "address": {
                        "address": "123 Pickup St",
                        "city": "Origin City",
                        "postal_code": "12345",
                        "country": "US",
                    },
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                "planned_date": "2024-01-15",
                "planned_time_window_start": "09:00:00",
                "planned_time_window_end": "17:00:00",
            },
            {
                "type": "DELIVERY",
                "location": {
                    "code": "DEL001",
                    "name": "Delivery Location",
                    "address": {
                        "address": "456 Delivery Ave",
                        "city": "Destination City",
                        "postal_code": "67890",
                        "country": "US",
                    },
                    "latitude": 41.8781,
                    "longitude": -87.6298,
                },
                "planned_date": "2024-01-16",
                "planned_time_window_start": "08:00:00",
                "planned_time_window_end": "16:00:00",
            },
        ],
        "line_items": [
            {
                "package_type": "BOX",
                "stackable": True,
                "height": 1.0,
                "length": 1.0,
                "width": 1.0,
                "length_unit": "m",
                "package_weight": 10.0,
                "weight_unit": "kg",
                "description": "Test Item",
                "total_packages": 1,
            }
        ],
    }

    shipment_response = client.post("/api/v1/tms/shipments/", json=shipment_data)
    shipment_id = shipment_response.json()["id"]

    # Create a broker event for validation
    broker_event_data = {
        "id": "EVT001",
        "shipmentId": shipment_id,
        "dateTransmission": "2024-01-15T10:00:00",
        "owner": "Test Owner",
        "order": {"reference": shipment_id, "eta": None},
        "situation": {
            "event": "ORDER_CREATED",
            "registrationDate": "2024-01-15T10:00:00",
            "actualDate": "2024-01-15T09:30:00",
            "position": None,
        },
        "carrier": "Test Carrier",
    }

    broker_response = client.post("/api/v1/broker/events/", json=broker_event_data)
    assert broker_response.status_code == 201

    # Now test TMS event validation
    event_data = {
        "event_type": "BOOKED",
        "created_at": "2024-01-15T10:00:00",
        "occured_at": "2024-01-15T09:30:00",
        "source": "broker",
        "location": None,
    }

    response = client.post(f"/api/v1/tms/event/{shipment_id}", json=event_data)

    assert response.status_code == 202


def test_incoming_event_validation_missing_broker_event():
    event_data = {
        "event_type": "BOOKED",
        "created_at": "2024-01-15T10:00:00",
        "occured_at": "2024-01-15T09:30:00",
        "source": "broker",
        "location": None,
    }

    response = client.post("/api/v1/tms/event/nonexistent-id", json=event_data)

    assert response.status_code == 422
    assert "not found" in response.json()["detail"]
