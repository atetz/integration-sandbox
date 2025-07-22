from typing import List

from fastapi import APIRouter, status

from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger
from integrationsandbox.trigger.service import (
    create_and_dispatch_events,
    create_and_dispatch_shipments,
)

router = APIRouter(prefix="/trigger")


@router.post(
    "/shipments/",
    summary="Generate a request with multiple new shipments",
    description="""
      Creates and sends multiple new shipments. 
      """,
    response_description="List of generated shipments sent to target URL",
    status_code=status.HTTP_201_CREATED,
)
def trigger_shipments(trigger: ShipmentTrigger) -> List[TmsShipment]:
    shipments = create_and_dispatch_shipments(trigger)
    return shipments


@router.post(
    "/events/",
    summary="Generate tracking events for multiple shipments",
    description="""
      Creates and sends tracking events for multiple existing shipments.
      Supports all broker event types (ORDER_CREATED, DRIVING_TO_LOAD, etc.)
      """,
    response_description="List of generated events sent to target URL",
    status_code=status.HTTP_201_CREATED,
)
def trigger_events(trigger: EventTrigger) -> None:
    events = create_and_dispatch_events(trigger)
    return events
