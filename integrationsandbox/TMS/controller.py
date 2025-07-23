from fastapi import APIRouter, HTTPException, status

from integrationsandbox.tms.models import CreateTmsShipmentEvent
from integrationsandbox.tms.service import validate_event

router = APIRouter(prefix="/tms")


@router.post(
    "/event/{shipment_id}",
    summary="Receive and validate TMS event for a specific id.",
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
