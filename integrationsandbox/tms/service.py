from typing import Any, Dict, List, Tuple

from integrationsandbox.broker.models import BrokerEventMessage, BrokerEventType
from integrationsandbox.broker.repository import get_event
from integrationsandbox.common.validation import compare_mappings
from integrationsandbox.tms.models import (
    CreateTmsShipmentEvent,
    TmsEventType,
    TmsShipment,
)

EVENT_TYPE_MAP = {
    BrokerEventType.ORDER_CREATED: TmsEventType.BOOKED,
    BrokerEventType.CANCEL_ORDER: TmsEventType.CANCELLED,
    BrokerEventType.DRIVING_TO_LOAD: TmsEventType.DISPATCHED,
    BrokerEventType.ORDER_LOADED: TmsEventType.PICKED_UP,
    BrokerEventType.ORDER_DELIVERED: TmsEventType.DELIVERED,
    BrokerEventType.ETA_EVENT: TmsEventType.ETA_CHANGED,
}

REVERSE_EVENT_TYPE_MAP = {v: k for k, v in EVENT_TYPE_MAP.items()}


def get_stop_by_type(stops, location_type: str):
    for stop in stops:
        if stop.type == location_type:
            return stop
    return None


def get_location_for_event(
    shipment: TmsShipment, event_type: BrokerEventType
) -> str | None:
    if event_type in [BrokerEventType.DRIVING_TO_LOAD, BrokerEventType.ORDER_LOADED]:
        pickup_stop = get_stop_by_type(shipment.stops, "PICKUP")
        return pickup_stop.location.code if pickup_stop else None
    elif event_type in [BrokerEventType.ORDER_DELIVERED, BrokerEventType.ETA_EVENT]:
        delivery_stop = get_stop_by_type(shipment.stops, "DELIVERY")
        return delivery_stop.location.code if delivery_stop else None
    return None


def apply_event_mapping_rules(broker_event: BrokerEventMessage) -> Dict[str, Any]:
    result = {}

    result["event_type"] = EVENT_TYPE_MAP[broker_event.situation.event]
    result["created_at"] = broker_event.situation.registrationDate
    result["occured_at"] = broker_event.situation.actualDate
    result["source"] = "broker"
    if broker_event.situation.position:
        result["location_code"] = broker_event.situation.position.locationReference
        result["location_latitude"] = broker_event.situation.position.latitude
        result["location_longitude"] = broker_event.situation.position.longitude

    return result


def get_transformed_event_data(event: CreateTmsShipmentEvent) -> Dict[str, Any]:
    result = {}

    result["event_type"] = event.event_type
    result["created_at"] = event.created_at
    result["occured_at"] = event.occured_at
    result["source"] = "broker"
    if event.location:
        result["location_code"] = event.location.code
        result["location_latitude"] = event.location.latitude
        result["location_longitude"] = event.location.longitude

    return result


def validate_event(
    event: CreateTmsShipmentEvent, shipment_id: str
) -> Tuple[bool, List[str | None]]:
    event_type = REVERSE_EVENT_TYPE_MAP[event.event_type]
    broker_event = get_event(
        {
            "shipment_id__eq": shipment_id,
            "event_type__eq": event_type,
        }
    )
    if not broker_event:
        return False, [
            f"Event with type: {event_type} and shipment_id: {shipment_id} not found"
        ]

    expected_data = apply_event_mapping_rules(broker_event)
    transformed_data = get_transformed_event_data(event)
    return compare_mappings(expected_data, transformed_data)
