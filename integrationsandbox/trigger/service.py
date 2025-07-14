from typing import List

import httpx

from integrationsandbox.tms import repository
from integrationsandbox.tms.factories import TmsShipmentFactory
from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.trigger.models import OrderTrigger


def create_orders_from_factory(count: int) -> List[TmsShipment]:
    factory = TmsShipmentFactory()
    return [factory.create_shipment() for order in range(count)]


def dispatch_orders_to_url(orders: List[TmsShipment], url: str) -> None:
    # model_dump(mode="json") prevents escaped json being sent.
    data = [order.model_dump(mode="json") for order in orders]
    r = httpx.post(url, json=data)
    r.raise_for_status()


def create_and_dispatch_orders(trigger: OrderTrigger):
    orders = create_orders_from_factory(trigger.count)
    repository.create_orders(orders)
    dispatch_orders_to_url(orders, trigger.target_url.encoded_string())
    return orders
