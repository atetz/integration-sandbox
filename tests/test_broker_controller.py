from fastapi.testclient import TestClient

from integrationsandbox.main import app

client = TestClient(app)


def test_create_event_endpoint():
    event_data = {
        "shipmentId": "SH001",
        "dateTransmission": "2024-01-15T10:00:00",
        "owner": "Test Owner",
        "order": {"reference": "SH001", "eta": None},
        "situation": {
            "event": "ORDER_CREATED",
            "registrationDate": "2024-01-15T10:00:00",
            "actualDate": "2024-01-15T09:30:00",
            "position": None,
        },
        "carrier": "Test Carrier",
    }

    response = client.post("/api/v1/broker/events/", json=event_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"]  # UUID was generated
    assert data["shipmentId"] == "SH001"
    assert data["carrier"] == "Test Carrier"


def test_seed_events_endpoint():
    # First create a shipment
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

    # Now seed events for that shipment
    seed_data = {"event": "ORDER_CREATED", "shipment_ids": [shipment_id]}

    response = client.post("/api/v1/broker/events/seed", json=seed_data)

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["shipmentId"] == shipment_id


def test_get_events_endpoint():
    response = client.get("/api/v1/broker/events/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_events_with_filters():
    response = client.get("/api/v1/broker/events/?event=ORDER_CREATED")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_incoming_order_validation_endpoint():
    # First create a TMS shipment to validate against
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
                        "address": "123 Main St",
                        "city": "Test City",
                        "postal_code": "12345",
                        "country": "US",
                    },
                    "latitude": 40.7,
                    "longitude": -74.0,
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
                        "address": "456 Oak Ave",
                        "city": "Test City",
                        "postal_code": "12345",
                        "country": "US",
                    },
                    "latitude": 40.8,
                    "longitude": -74.1,
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

    tms_response = client.post("/api/v1/tms/shipments/", json=shipment_data)
    shipment_id = tms_response.json()["id"]

    # Create a properly formatted broker order message
    broker_order = {
        "meta": {
            "senderId": "TEST_SENDER",
            "messageDate": "2024-01-15T10:00:00",
            "messageReference": "MSG001",
            "messageFunction": 9,
        },
        "shipment": {
            "reference": shipment_id,
            "carrier": "Test Carrier",
            "transportMode": "ROAD",
            "orders": [
                {
                    "reference": shipment_id,
                    "pickUp": {
                        "identification": "PU001",
                        "name": "Pickup Location",
                        "address1": "123 Main St",
                        "address2": "",
                        "country": "US",
                        "postalCode": "12345",
                        "city": "Test City",
                        "latitude": 40.7,
                        "longitude": -74.0,
                        "instructions": "",
                        "dates": [
                            {
                                "qualifier": "PERIOD_EARLIEST",
                                "dateTime": "2024-01-15T09:00:00",
                            },
                            {
                                "qualifier": "PERIOD_LATEST",
                                "dateTime": "2024-01-15T17:00:00",
                            },
                        ],
                    },
                    "consignee": {
                        "identification": "DEL001",
                        "name": "Delivery Location",
                        "address1": "456 Oak Ave",
                        "address2": "",
                        "country": "US",
                        "postalCode": "12345",
                        "city": "Test City",
                        "latitude": 40.8,
                        "longitude": -74.1,
                        "instructions": "",
                        "dates": [
                            {
                                "qualifier": "PERIOD_EARLIEST",
                                "dateTime": "2024-01-16T08:00:00",
                            },
                            {
                                "qualifier": "PERIOD_LATEST",
                                "dateTime": "2024-01-16T16:00:00",
                            },
                        ],
                    },
                    "goodsDescription": "Test Item",
                    "quantity": {"grossWeight": 10.0, "loadingMeters": 10.0},
                    "handlingUnits": [
                        {
                            "packagingQualifier": "BX",
                            "grossWeight": 10.0,
                            "width": 1.0,
                            "length": 1.0,
                            "height": 1.0,
                        }
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
