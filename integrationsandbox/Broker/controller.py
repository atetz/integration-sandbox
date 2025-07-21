from fastapi import APIRouter, status

from integrationsandbox.broker.models import CreateBrokerOrderMessage
from integrationsandbox.broker.service import validate_order

router = APIRouter(prefix="/broker")


@router.post("/order/", status_code=status.HTTP_202_ACCEPTED)
def incoming_order(order: CreateBrokerOrderMessage) -> None:
    validate_order(order)
    return None
