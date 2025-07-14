from typing import List

from pydantic import AnyUrl, BaseModel, PositiveInt


class OrderTrigger(BaseModel):
    target_url: AnyUrl
    count: PositiveInt


class EventTrigger(BaseModel):
    target_url: AnyUrl
    orders: List[str]
