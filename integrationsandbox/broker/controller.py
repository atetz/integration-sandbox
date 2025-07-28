import logging
from typing import List

from fastapi import APIRouter, Depends, status

from integrationsandbox.broker import service as broker_service
from integrationsandbox.broker.models import (
    BrokerEventFilters,
    BrokerEventMessage,
    BrokerEventSeedRequest,
    CreateBrokerEventMessage,
    CreateBrokerOrderMessage,
)
from integrationsandbox.broker.service import list_events
from integrationsandbox.tms.service import get_shipments_by_id_list
from integrationsandbox.validation import service as validation_service

router = APIRouter(prefix="/broker")
logger = logging.getLogger(__name__)


@router.post(
    "/order/",
    summary="Receive and validate broker order.",
    description="""
      Receives an order in broker format and validates the transformations based on the tms shipment data and mapping rules. 
      """,
    response_description="HTTP 202 with no body if validated succesfully.",
    status_code=status.HTTP_202_ACCEPTED,
)
def incoming_order(order: CreateBrokerOrderMessage) -> None:
    logger.info("Received broker order for shipment: %s", order.shipment.reference)
    logger.debug("Order details: %s", order.model_dump())
    validation_service.validate_broker_order(order)
    logger.info("Broker order validation successful")


@router.post(
    "/events/",
    summary="Create new broker event",
    description="""
      Receives a broker event message and stores it in the database. 
      """,
    response_description="HTTP 201 with created event and id in response.",
    status_code=status.HTTP_201_CREATED,
)
def create_event_endpoint(new_event: CreateBrokerEventMessage) -> BrokerEventMessage:
    logger.info("Creating new broker event")
    logger.debug("Event details: %s", new_event.model_dump())
    event = broker_service.create_event(new_event)
    logger.info("Broker event created with ID: %s", event.id)
    return event


@router.post(
    "/events/seed",
    summary="Seed events",
    description="""
      Receives a count and then proceeds to generate and save events for given count. 
      """,
    response_description="List of generated events sent to target URL",
    status_code=status.HTTP_201_CREATED,
)
def seed_events(seed_request: BrokerEventSeedRequest) -> List[BrokerEventMessage]:
    logger.info("Seeding events for %d shipments with event type: %s", len(seed_request.shipment_ids), seed_request.event)
    logger.debug("Shipment IDs: %s", seed_request.shipment_ids)
    shipments = get_shipments_by_id_list(seed_request.shipment_ids)
    events = broker_service.create_seed_events(shipments, seed_request.event)
    logger.info("Successfully created %d seed events", len(events))
    return events


@router.get(
    "/events/",
    summary="Get events",
    description="""
      Retreives a list of all the events.
      """,
    response_description="List of events",
    status_code=status.HTTP_200_OK,
)
def get_events(
    filters: BrokerEventFilters = Depends(),
) -> List[BrokerEventMessage] | None:
    logger.info("Retrieving broker events with filters")
    logger.debug("Filters: %s", filters.model_dump() if filters else None)
    events = list_events(filters)
    count = len(events) if events else 0
    logger.info("Retrieved %d broker events", count)
    return events
