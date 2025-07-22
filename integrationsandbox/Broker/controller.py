from fastapi import APIRouter, HTTPException, status

from integrationsandbox.broker.models import CreateBrokerOrderMessage
from integrationsandbox.broker.service import validate_order

router = APIRouter(prefix="/broker")


@router.post("/order/", status_code=status.HTTP_202_ACCEPTED)
def incoming_order(order: CreateBrokerOrderMessage) -> None:
    result, errors = validate_order(order)
    if not result:
        raise HTTPException(status_code=400, detail=errors)
