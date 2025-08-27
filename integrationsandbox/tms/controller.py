import logging
from typing import List

from fastapi import APIRouter, Depends, status

from integrationsandbox.security.service import get_current_active_user
from integrationsandbox.tms import service as tms_service
from integrationsandbox.tms.models import (
    CreateTmsShipment,
    CreateTmsShipmentEvent,
    TmsShipment,
    TmsShipmentFilters,
    TmsShipmentSeedRequest,
)
from integrationsandbox.validation import service as validation_service

router = APIRouter(
    prefix="/tms", dependencies=[Depends(get_current_active_user)], tags=["TMS"]
)
logger = logging.getLogger(__name__)


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
    logger.info("Received TMS event for shipment: %s", shipment_id)
    logger.debug("Event details: %s", event.model_dump())
    validation_service.validate_tms_event(event, shipment_id)
    logger.info("TMS event validation successful")
    tms_service.update_shipment_event(event, shipment_id)
    logger.info("TMS shipment event update successful")


@router.post(
    "/shipments",
    summary="Create new TMS Shipment",
    description="""
      Receives an TMS shipment message and stores it in the database. 
      """,
    response_description="HTTP 201 with created shipment and id in response.",
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(new_shipment: CreateTmsShipment) -> TmsShipment:
    logger.info("Creating new TMS shipment")
    logger.debug("Shipment details: %s", new_shipment.model_dump())
    shipments = tms_service.create_shipment(new_shipment)
    logger.info("TMS shipment created with ID: %s", shipments.id)
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
    logger.info("Seeding %d TMS shipments", seed_request.count)
    shipments = tms_service.create_seed_shipments(seed_request.count)
    logger.info("Successfully created %d seed shipments", len(shipments))
    return shipments


@router.get(
    "/shipments",
    summary="Get shipments",
    description="""
      Retreives a list of all the shipments.
      """,
    response_description="List of shipments",
    status_code=status.HTTP_200_OK,
)
def get_shipments(filters: TmsShipmentFilters = Depends()) -> List[TmsShipment] | None:
    logger.info("Retrieving TMS shipments with filters")
    logger.debug("Filters: %s", filters.model_dump() if filters else None)
    shipments = tms_service.list_shipments(filters)
    count = len(shipments) if shipments else 0
    logger.info("Retrieved %d TMS shipments", count)
    return shipments


@router.get(
    "/shipments/new",
    summary="Get new shipments",
    description="""
      Retreives a list of all the new shipments.
      """,
    response_description="List of new shipments",
    status_code=status.HTTP_200_OK,
)
def get_new_shipments(
    filters: TmsShipmentFilters = Depends(),
) -> List[TmsShipment] | None:
    logger.info("Retrieving TMS new shipments with filters")
    logger.debug("Filters: %s", filters.model_dump() if filters else None)
    shipments = tms_service.list_new_shipments(filters)
    count = len(shipments) if shipments else 0
    logger.info("Retrieved %d TMS shipments", count)
    return shipments
