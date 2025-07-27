from typing import List

from fastapi import APIRouter, Depends, status

from integrationsandbox.tms import service as tms_service
from integrationsandbox.tms.models import (
    CreateTmsShipment,
    CreateTmsShipmentEvent,
    TmsShipment,
    TmsShipmentFilters,
    TmsShipmentSeedRequest,
)
from integrationsandbox.validation import service as validation_service

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
    validation_service.validate_tms_event(event, shipment_id)


@router.post(
    "/shipments/",
    summary="Create new TMS Shipment",
    description="""
      Receives an TMS shipment message and stores it in the database. 
      """,
    response_description="HTTP 201 with created shipment and id in response.",
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(new_shipment: CreateTmsShipment) -> TmsShipment:
    shipments = tms_service.create_shipment(new_shipment)
    return shipments


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
    shipments = tms_service.create_seed_shipments(seed_request.count)
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
    return tms_service.list_shipments(filters)
