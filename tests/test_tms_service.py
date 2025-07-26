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
)
from integrationsandbox.tms.service import (
    apply_event_mapping_rules,
    build_shipments,
    get_shipments_by_id_list,
    get_transformed_event_data,
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
            locationReference="LOC001",
            latitude=40.7,
            longitude=-74.0
        )
    )
    
    order = BrokerEventOrder(
        reference="SH001",
        eta=None
    )
    
    broker_event = BrokerEventMessage(
        id="EVT001",
        shipmentId="SH001", 
        dateTransmission=datetime(2024, 1, 15, 10, 0),
        owner="Test Owner",
        order=order,
        situation=situation,
        carrier="Test Carrier"
    )
    
    result = apply_event_mapping_rules(broker_event)
    
    assert result["event_type"] == TmsEventType.PICKED_UP
    assert result["created_at"] == datetime(2024, 1, 15, 10, 0)
    assert result["occured_at"] == datetime(2024, 1, 15, 9, 30)
    assert result["source"] == "broker"
    assert result["location_code"] == "LOC001"
    assert result["location_latitude"] == 40.7
    assert result["location_longitude"] == -74.0
