from typing import List

from fastapi import APIRouter, status

from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger
from integrationsandbox.trigger.service import (
    create_and_dispatch_events,
    create_and_dispatch_shipments,
)

router = APIRouter(prefix="/trigger")


@router.post("/shipments/", status_code=status.HTTP_201_CREATED)
def trigger_shipments(trigger: ShipmentTrigger) -> List[TmsShipment]:
    shipments = create_and_dispatch_shipments(trigger)
    return shipments


@router.post("/events/", status_code=status.HTTP_201_CREATED)
def trigger_events(trigger: EventTrigger) -> None:
    events = create_and_dispatch_events(trigger)
    return events
