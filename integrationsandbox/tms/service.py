import uuid
from typing import Any, Dict, List

from integrationsandbox.broker.models import BrokerEventMessage, BrokerEventType
from integrationsandbox.common.exceptions import NotFoundError, ValidationError
from integrationsandbox.config import get_settings
from integrationsandbox.tms import repository
from integrationsandbox.tms.factories import TmsShipmentFactory
from integrationsandbox.tms.models import (
    CreateTmsShipment,
    CreateTmsShipmentEvent,
    TmsEventType,
    TmsShipment,
    TmsShipmentFilters,
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


def build_shipments(count: int) -> List[TmsShipment]:
    factory = TmsShipmentFactory()
    return [factory.create_shipment() for _ in range(count)]


def create_seed_shipments(count: int) -> List[TmsShipment]:
    settings = get_settings()
    if count <= 0:
        raise ValidationError("Count must be greater than 0")
    elif count > settings.max_bulk_size:
        raise ValidationError(f"Count must be less than {settings.max_bulk_size}")
    shipments = build_shipments(count)
    repository.create_many(shipments)
    return shipments


def list_shipments(filters: TmsShipmentFilters) -> List[TmsShipment]:
    return repository.get_all(filters)


def get_shipment_by_id(id: str) -> TmsShipment:
    shipment = repository.get_by_id(id)
    if not shipment:
        raise NotFoundError(f"Shipment with id {id} not found")
    return shipment


def get_shipments_by_id_list(shipment_ids: List[str]) -> List[TmsShipment]:
    if not shipment_ids:
        return []
    shipments, not_found = repository.get_by_id_list(shipment_ids)
    if not_found:
        raise NotFoundError(f"Shipments not found in database: {shipment_ids}")
    return shipments


def create_shipment(new_shipment: CreateTmsShipment) -> TmsShipment:
    shipment = TmsShipment(id=str(uuid.uuid4()), **new_shipment.model_dump())
    repository.create(shipment)
    return shipment


def create_shipments(shipments: List[TmsShipment]) -> List[TmsShipment]:
    repository.create_many(shipments)
    return shipments
