import logging
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
    TmsShipmentEvent,
    TmsShipmentFilters,
)

logger = logging.getLogger(__name__)

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
    result["external_order_reference"] = broker_event.order.reference
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
    result["external_order_reference"] = event.external_order_reference
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
    logger.info("Building %d TMS shipments", count)
    factory = TmsShipmentFactory()
    shipments = [factory.create_shipment() for _ in range(count)]
    logger.info("Successfully built %d shipments", len(shipments))
    return shipments


def has_existing_event(
    events: List[TmsShipmentEvent], new_event: TmsShipmentEvent
) -> bool:
    if not events:
        return False
    for event in events:
        if event.event_type == new_event.event_type:
            return True
    return False


def create_seed_shipments(count: int) -> List[TmsShipment]:
    logger.info("Creating %d seed shipments", count)
    settings = get_settings()
    if count <= 0:
        raise ValidationError("Count must be greater than 0")
    elif count > settings.max_bulk_size:
        raise ValidationError(f"Count must be less than {settings.max_bulk_size}")
    shipments = build_shipments(count)
    repository.create_many(shipments)
    logger.info("Successfully created %d seed shipments", len(shipments))
    return shipments


def list_shipments(filters: TmsShipmentFilters) -> List[TmsShipment]:
    logger.info("Listing TMS shipments with filters")
    logger.debug("Filters: %s", filters.model_dump() if filters else None)
    shipments = repository.get_all(filters)
    shipment_count = len(shipments) if shipments else 0
    logger.info("Retrieved %d shipments from database", shipment_count)

    return shipments


def list_new_shipments() -> List[TmsShipment]:
    logger.info("Listing TMS new shipments")
    shipments = repository.get_all_new()
    shipment_count = len(shipments) if shipments else 0
    logger.info("Retrieved %d shipments from database", shipment_count)
    return shipments


def get_shipment_by_id(id: str) -> TmsShipment:
    logger.info("Retrieving TMS shipment by ID: %s", id)
    shipment = repository.get_by_id(id)
    if not shipment:
        logger.warning("Shipment not found: %s", id)
        raise NotFoundError(f"Shipment with id {id} not found")
    logger.info("Successfully retrieved shipment: %s", id)
    return shipment


def get_shipments_by_id_list(shipment_ids: List[str]) -> List[TmsShipment]:
    if not shipment_ids:
        logger.info("Empty shipment ID list provided")
        return []
    logger.info("Retrieving %d TMS shipments by ID list", len(shipment_ids))
    logger.debug("Shipment IDs: %s", shipment_ids)
    shipments, not_found = repository.get_by_id_list(shipment_ids)
    if not_found:
        logger.warning("Shipments not found: %s", not_found)
        raise NotFoundError(f"Shipments not found in database: {shipment_ids}")
    logger.info("Successfully retrieved %d shipments", len(shipments))
    return shipments


def create_shipment(new_shipment: CreateTmsShipment) -> TmsShipment:
    logger.info("Creating new TMS shipment")
    shipment = TmsShipment(id=str(uuid.uuid4()), **new_shipment.model_dump())
    repository.create(shipment)
    logger.info("Successfully created shipment with ID: %s", shipment.id)
    return shipment


def update_shipment_event(event: CreateTmsShipmentEvent, shipment_id: str) -> None:
    logger.info("Adding event to Shipment ID: %s", shipment_id)
    shipment = repository.get_by_id(shipment_id)
    if not shipment:
        logger.warning("Shipment not found: %s", shipment_id)
        raise NotFoundError(f"Shipment not found in database: {shipment_id}")

    if shipment.external_reference is None:
        shipment.external_reference = event.external_order_reference

    event = TmsShipmentEvent(id=str(uuid.uuid4()), **event.model_dump())
    if has_existing_event(shipment.timeline_events, event):
        logger.info("Event type already exists. Overwriting %s", event.event_type)
    shipment.update_timeline_events(event)
    repository.update(shipment)
    logger.info("Successfully updated shipment events for Shipment ID: %s", shipment.id)


def create_shipments(shipments: List[TmsShipment]) -> List[TmsShipment]:
    logger.info("Creating %d TMS shipments", len(shipments))
    repository.create_many(shipments)
    logger.info("Successfully created %d shipments", len(shipments))
    return shipments
