from typing import List

from pydantic import AnyUrl, BaseModel, PositiveInt

from integrationsandbox.broker.models import BrokerEventType


class ShipmentTrigger(BaseModel):
    target_url: AnyUrl
    count: PositiveInt


class EventTrigger(BaseModel):
    target_url: AnyUrl
    event: BrokerEventType
    shipment_ids: List[str]
