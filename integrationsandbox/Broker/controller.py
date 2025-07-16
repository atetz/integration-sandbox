from fastapi import APIRouter, status

from integrationsandbox.broker.models import CreateBrokerOrderMessage

router = APIRouter(prefix="/broker")


@router.post("/order/", status_code=status.HTTP_202_ACCEPTED)
def create_order(order: CreateBrokerOrderMessage) -> None:
    return None
