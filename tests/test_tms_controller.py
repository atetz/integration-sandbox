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
            "carrier": "Test Carrier"
        },
        "loading_meters": 10.0,
        "stops": [],
        "line_items": []
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
            "carrier": "Test Carrier"
        },
        "loading_meters": 10.0,
        "stops": [],
        "line_items": []
    }
    
    shipment_response = client.post("/api/v1/tms/shipments/", json=shipment_data)
    shipment_id = shipment_response.json()["id"]
    
    # Create a broker event for validation
    broker_event_data = {
        "id": "EVT001",
        "shipmentId": shipment_id,
        "dateTransmission": "2024-01-15T10:00:00",
        "owner": "Test Owner", 
        "order": {
            "reference": shipment_id,
            "eta": None
        },
        "situation": {
            "event": "ORDER_CREATED",
            "registrationDate": "2024-01-15T10:00:00",
            "actualDate": "2024-01-15T09:30:00",
            "position": None
        },
        "carrier": "Test Carrier"
    }
    
    broker_response = client.post("/api/v1/broker/events/", json=broker_event_data)
    assert broker_response.status_code == 201
    
    # Now test TMS event validation
    event_data = {
        "event_type": "BOOKED",
        "created_at": "2024-01-15T10:00:00",
        "occured_at": "2024-01-15T09:30:00", 
        "source": "broker",
        "location": None
    }
    
    response = client.post(f"/api/v1/tms/event/{shipment_id}", json=event_data)
    
    assert response.status_code == 202


def test_incoming_event_validation_missing_broker_event():
    event_data = {
        "event_type": "BOOKED",
        "created_at": "2024-01-15T10:00:00",
        "occured_at": "2024-01-15T09:30:00",
        "source": "broker", 
        "location": None
    }
    
    response = client.post("/api/v1/tms/event/nonexistent-id", json=event_data)
    
    assert response.status_code == 400
    assert "not found" in response.json()["detail"][0]