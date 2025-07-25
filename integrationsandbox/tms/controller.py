from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from integrationsandbox.tms.models import (
    CreateTmsShipmentEvent,
    TmsShipment,
    TmsShipmentFilters,
    TmsShipmentSeedRequest,
)
from integrationsandbox.tms.service import (
    create_seed_shipments,
    list_shipments,
    validate_event,
)

router = APIRouter(prefix="/tms")


@router.post(
    "/event/{shipment_id}",
    summary="Receive and validate TMS event",
    description="""
      Receives an event in TMS format and validates the transformations based on the broker event data and mapping rules. 
      """,
    response_description="HTTP 202 with no body if validated succesfully.",
    status_code=status.HTTP_202_ACCEPTED,
)
def incoming_event(event: CreateTmsShipmentEvent, shipment_id: str) -> None:
    result, errors = validate_event(event, shipment_id)
    if not result:
        raise HTTPException(status_code=400, detail=errors)


@router.post(
    "/shipments/seed",
    summary="Seed shipments",
    description="""
      Receives a count and then proceeds to generate and save shipments for given count. 
      """,
    response_description="List of generated shipments sent to target URL",
    status_code=status.HTTP_201_CREATED,
)
def seed_shipments(seed_request: TmsShipmentSeedRequest) -> List[TmsShipment]:
    shipments = create_seed_shipments(seed_request.count)
    return shipments


@router.get(
    "/shipments/",
    summary="Get shipments",
    description="""
      Retreives a list of all the shipments.
      """,
    response_description="List of shipments",
    status_code=status.HTTP_200_OK,
)
def get_events(filters: TmsShipmentFilters = Depends()) -> List[TmsShipment] | None:
    return list_shipments(filters)
