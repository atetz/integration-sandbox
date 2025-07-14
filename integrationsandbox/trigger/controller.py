from typing import List

from fastapi import APIRouter

from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.trigger.models import OrderTrigger
from integrationsandbox.trigger.service import create_and_dispatch_orders

router = APIRouter(prefix="/trigger")


@router.post("/orders/")
def trigger_orders(trigger: OrderTrigger) -> List[TmsShipment]:
    orders = create_and_dispatch_orders(trigger)
    return orders
