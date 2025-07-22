from fastapi import APIRouter, HTTPException, status

from integrationsandbox.broker.models import CreateBrokerOrderMessage
from integrationsandbox.broker.service import validate_order

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
    result, errors = validate_order(order)
    if not result:
        raise HTTPException(status_code=400, detail=errors)
