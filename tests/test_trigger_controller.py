from unittest.mock import patch
from fastapi.testclient import TestClient

from integrationsandbox.main import app

client = TestClient(app)


@patch('integrationsandbox.trigger.service.httpx.post')
def test_trigger_shipments_endpoint(mock_post):
    # Mock the external HTTP call
    mock_post.return_value.raise_for_status.return_value = None
    
    trigger_data = {
        "count": 2,
        "target_url": "https://httpbin.org/post"
    }
    
    response = client.post("/api/v1/trigger/shipments/", json=trigger_data)
    
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert all(shipment["id"] for shipment in data)
    
    # Verify external call was made
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://httpbin.org/post"
    assert "json" in kwargs
    assert len(kwargs["json"]) == 2


@patch('integrationsandbox.trigger.service.httpx.post')
def test_trigger_events_endpoint(mock_post):
    # Mock the external HTTP call
    mock_post.return_value.raise_for_status.return_value = None
    
    # First create some shipments
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
        "stops": [
            {
                "type": "PICKUP",
                "location": {
                    "code": "PU001",
                    "name": "Pickup Location",
                    "address": {
                        "address": "123 Main St",
                        "city": "Test City",
                        "postal_code": "12345",
                        "country": "US"
                    },
                    "latitude": 40.7,
                    "longitude": -74.0
                },
                "planned_date": "2024-01-15",
                "planned_time_window_start": "09:00:00",
                "planned_time_window_end": "17:00:00"
            }
        ],
        "line_items": []
    }
    
    shipment_response = client.post("/api/v1/tms/shipments/", json=shipment_data)
    shipment_id = shipment_response.json()["id"]
    
    # Now trigger events for that shipment
    trigger_data = {
        "event": "ORDER_LOADED",
        "shipment_ids": [shipment_id],
        "target_url": "https://httpbin.org/post" 
    }
    
    response = client.post("/api/v1/trigger/events/", json=trigger_data)
    
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["shipmentId"] == shipment_id
    assert data[0]["situation"]["event"] == "ORDER_LOADED"
    
    # Verify external call was made
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://httpbin.org/post"
    assert "json" in kwargs
    assert len(kwargs["json"]) == 1


@patch('integrationsandbox.trigger.service.httpx.post')
def test_trigger_events_with_nonexistent_shipment(mock_post):
    # Mock the external HTTP call
    mock_post.return_value.raise_for_status.return_value = None
    
    trigger_data = {
        "event": "ORDER_CREATED",
        "shipment_ids": ["nonexistent-id"],
        "target_url": "https://httpbin.org/post"
    }
    
    response = client.post("/api/v1/trigger/events/", json=trigger_data)
    
    # Should succeed but return empty events (resilient behavior for testing tool)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 0
    
    # External call should still be made with empty data
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert len(kwargs["json"]) == 0


@patch('integrationsandbox.trigger.service.httpx.post')
def test_trigger_shipments_zero_count(mock_post):
    trigger_data = {
        "count": 0,
        "target_url": "https://httpbin.org/post"
    }
    
    response = client.post("/api/v1/trigger/shipments/", json=trigger_data)
    
    # Should fail validation because count must be positive integer (>= 1)
    assert response.status_code == 422
    
    # No external call should be made when validation fails
    mock_post.assert_not_called()