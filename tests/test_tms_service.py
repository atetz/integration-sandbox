from datetime import datetime

from integrationsandbox.broker.models import (
    BrokerEventMessage,
    BrokerEventOrder,
    BrokerEventPosition,
    BrokerEventSituation,
    BrokerEventType,
)
from integrationsandbox.tms.models import (
    CreateTmsShipmentEvent,
    TmsAddress,
    TmsEventType,
    TmsLocation,
    TmsShipment,
    TmsShipmentEvent,
)
from integrationsandbox.tms.service import (
    apply_event_mapping_rules,
    build_shipments,
    get_shipments_by_id_list,
    get_transformed_event_data,
    has_existing_event,
    update_shipment_event,
)


def test_build_shipments():
    shipments = build_shipments(3)

    assert len(shipments) == 3
    assert all(isinstance(s, TmsShipment) for s in shipments)
    assert all(s.id for s in shipments)  # All have IDs


def test_build_shipments_zero_count():
    shipments = build_shipments(0)

    assert len(shipments) == 0
    assert shipments == []


def test_get_shipments_by_id_list_empty():
    result = get_shipments_by_id_list([])

    assert result == []


def test_get_transformed_event_data():
    event = CreateTmsShipmentEvent(
        event_type=TmsEventType.PICKED_UP,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference=None,
        source="broker",
        location=None,
    )

    result = get_transformed_event_data(event)

    assert result["event_type"] == TmsEventType.PICKED_UP
    assert result["created_at"] == datetime(2024, 1, 15, 10, 0)
    assert result["occured_at"] == datetime(2024, 1, 15, 9, 30)
    assert result["source"] == "broker"


def test_get_transformed_event_data_with_location():
    location = TmsLocation(
        code="LOC001",
        name="Test Location",
        address=TmsAddress(
            address="123 Main St", city="Test City", postal_code="12345", country="US"
        ),
        latitude=40.7,
        longitude=-74.0,
    )

    event = CreateTmsShipmentEvent(
        event_type=TmsEventType.DELIVERED,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference=None,
        source="broker",
        location=location,
    )

    result = get_transformed_event_data(event)

    assert result["location_code"] == "LOC001"
    assert result["location_latitude"] == 40.7
    assert result["location_longitude"] == -74.0


def test_apply_event_mapping_rules():
    situation = BrokerEventSituation(
        event=BrokerEventType.ORDER_LOADED,
        registrationDate=datetime(2024, 1, 15, 10, 0),
        actualDate=datetime(2024, 1, 15, 9, 30),
        position=BrokerEventPosition(
            locationReference="LOC001", latitude=40.7, longitude=-74.0
        ),
    )

    order = BrokerEventOrder(reference="SH001", eta=None)

    broker_event = BrokerEventMessage(
        id="EVT001",
        shipmentId="SH001",
        dateTransmission=datetime(2024, 1, 15, 10, 0),
        owner="Test Owner",
        order=order,
        situation=situation,
        carrier="Test Carrier",
    )

    result = apply_event_mapping_rules(broker_event)

    assert result["event_type"] == TmsEventType.PICKED_UP
    assert result["created_at"] == datetime(2024, 1, 15, 10, 0)
    assert result["occured_at"] == datetime(2024, 1, 15, 9, 30)
    assert result["source"] == "broker"
    assert result["location_code"] == "LOC001"
    assert result["location_latitude"] == 40.7
    assert result["location_longitude"] == -74.0


def test_has_existing_event_empty_list():
    events = []
    new_event = TmsShipmentEvent(
        id="evt-1",
        order_external_reference="REF001",
        event_type=TmsEventType.BOOKED,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference="REF001",
        source="broker",
        location=None,
    )

    result = has_existing_event(events, new_event)

    assert result is False


def test_has_existing_event_not_found():
    existing_event = TmsShipmentEvent(
        id="evt-1",
        order_external_reference="REF001",
        event_type=TmsEventType.PICKED_UP,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference="REF001",
        source="broker",
        location=None,
    )
    events = [existing_event]

    new_event = TmsShipmentEvent(
        id="evt-2",
        order_external_reference="REF001",
        event_type=TmsEventType.DELIVERED,  # Different event type
        created_at=datetime(2024, 1, 15, 11, 0),
        occured_at=datetime(2024, 1, 15, 10, 30),
        external_order_reference="REF001",
        source="broker",
        location=None,
    )

    result = has_existing_event(events, new_event)

    assert result is False


def test_has_existing_event_found():
    existing_event = TmsShipmentEvent(
        id="evt-1",
        order_external_reference="REF001",
        event_type=TmsEventType.BOOKED,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference="REF001",
        source="broker",
        location=None,
    )
    events = [existing_event]

    new_event = TmsShipmentEvent(
        id="evt-2",
        order_external_reference="REF001",
        event_type=TmsEventType.BOOKED,  # Same event type
        created_at=datetime(2024, 1, 15, 11, 0),
        occured_at=datetime(2024, 1, 15, 10, 30),
        external_order_reference="REF001",
        source="broker",
        location=None,
    )

    result = has_existing_event(events, new_event)

    assert result is True



def test_update_shipment_event_new_shipment(tms_line_items, tms_stops):
    """Test updating shipment event when shipment has no external reference."""
    from unittest.mock import patch
    from integrationsandbox.tms.models import TmsCustomer
    
    # Create test customer
    customer = TmsCustomer(id="CUST001", name="Test Customer", carrier="Test Carrier")
    
    # Create a shipment without external reference
    shipment = TmsShipment(
        id="ship-123",
        external_reference=None,
        mode="FTL",
        equipment_type="TRUCK_AND_TRAILER",
        loading_meters=10.0,
        customer=customer,
        line_items=tms_line_items,
        stops=tms_stops,
        timeline_events=None,
    )
    
    event_data = CreateTmsShipmentEvent(
        event_type=TmsEventType.BOOKED,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference="EXT001",
        source="broker",
        location=None,
    )
    
    # Mock repository calls
    with patch("integrationsandbox.tms.service.repository.get_by_id", return_value=shipment) as mock_get, \
         patch("integrationsandbox.tms.service.repository.update") as mock_update:
        
        update_shipment_event(event_data, "ship-123")
        
        # Verify repository calls
        mock_get.assert_called_once_with("ship-123")
        mock_update.assert_called_once()
        
        # Verify shipment was updated
        updated_shipment = mock_update.call_args[0][0]
        assert updated_shipment.external_reference == "EXT001"
        assert len(updated_shipment.timeline_events) == 1
        assert updated_shipment.timeline_events[0].event_type == TmsEventType.BOOKED


def test_update_shipment_event_shipment_not_found():
    """Test updating shipment event when shipment doesnt exist."""
    from unittest.mock import patch
    from integrationsandbox.common.exceptions import NotFoundError
    
    event_data = CreateTmsShipmentEvent(
        event_type=TmsEventType.BOOKED,
        created_at=datetime(2024, 1, 15, 10, 0),
        occured_at=datetime(2024, 1, 15, 9, 30),
        external_order_reference="EXT001",
        source="broker",
        location=None,
    )
    
    # Mock repository to return None (shipment not found)
    with patch("integrationsandbox.tms.service.repository.get_by_id", return_value=None):
        try:
            update_shipment_event(event_data, "nonexistent-id")
            assert False, "Should have raised NotFoundError"
        except NotFoundError as e:
            assert "not found in database" in str(e)

