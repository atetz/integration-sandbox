import logging
from typing import List

from fastapi import APIRouter, Depends, status

from integrationsandbox.broker.models import BrokerEventMessage
from integrationsandbox.security.service import get_current_active_user
from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger
from integrationsandbox.trigger.service import (
    create_and_dispatch_events,
    create_and_dispatch_shipments,
)

router = APIRouter(
    prefix="/trigger",
    dependencies=[Depends(get_current_active_user)],
    tags=["Trigger"],
)
logger = logging.getLogger(__name__)


@router.post(
    "/shipments",
    summary="Generate a request with multiple new shipments",
    description="""
      Creates and sends multiple new shipments. 
      """,
    response_description="List of generated shipments sent to target URL",
    status_code=status.HTTP_201_CREATED,
)
def trigger_shipments(trigger: ShipmentTrigger) -> List[TmsShipment]:
    logger.info("Received shipments trigger.")
    logger.debug("Trigger: %s", trigger.model_dump())
    shipments = create_and_dispatch_shipments(trigger)
    logger.info(
        "Generated %d shipments and dispatched to %s",
        len(shipments),
        trigger.target_url,
    )
    logger.debug("Returned shipments: %s", shipments)
    return shipments


@router.post(
    "/events",
    summary="Generate tracking events for multiple shipments",
    description="""
      Creates and sends tracking events for multiple existing shipments.
      Supports all broker event types (ORDER_CREATED, DRIVING_TO_LOAD, etc.)
      """,
    response_description="List of generated events sent to target URL",
    status_code=status.HTTP_201_CREATED,
)
def trigger_events(trigger: EventTrigger) -> List[BrokerEventMessage]:
    logger.info("Received Events trigger.")
    logger.debug("Trigger: %s", trigger.model_dump())
    events = create_and_dispatch_events(trigger)
    logger.info(
        "Generated %d events and dispatched to %s", len(events), trigger.target_url
    )
    logger.debug("Returned events: %s", events)
    return events
