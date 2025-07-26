from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from integrationsandbox.broker.models import (
    BrokerEventFilters,
    BrokerEventMessage,
    BrokerEventSeedRequest,
    CreateBrokerEventMessage,
    CreateBrokerOrderMessage,
)
from integrationsandbox.broker.service import (
    build_events,
    create_event,
    create_events,
    list_events,
)
from integrationsandbox.tms.service import get_shipments_by_id_list
from integrationsandbox.validation.service import validate_broker_order

router = APIRouter(prefix="/broker")


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
    result, errors = validate_broker_order(order)
    if not result:
        raise HTTPException(status_code=400, detail=errors)


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
    event = create_event(new_event)
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
    shipments = get_shipments_by_id_list(seed_request.shipment_ids)
    events = build_events(shipments, seed_request.event)
    create_events(events)
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
    return list_events(filters)
