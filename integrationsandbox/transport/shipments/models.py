from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel

from integrationsandbox.transport.events.models import TmsShipmentEvent


class TmsCustomer(BaseModel):
    id: int
    name: str
    carrier: str


class TmsLineItem(BaseModel):
    package_type: Optional[str]
    stackable: bool
    height: Optional[int]
    length: Optional[int]
    width: Optional[int]
    length_unit: str
    package_weight: float
    weight_unit: str
    description: str
    total_packages: int


class TmsAddress(BaseModel):
    address: str
    city: str
    state_province: str
    postal_code: str
    country: str


class TmsLocation(BaseModel):
    name: str
    address: TmsAddress


class TmsStop(BaseModel):
    type: str
    location: TmsLocation
    planned_date: date
    planned_time_window_start: time
    planned_time_window_end: time


class TmsOrder(BaseModel):
    id: str
    external_reference: str
    mode: str
    equipment_type: str
    customer: TmsCustomer
    line_items: List[TmsLineItem]
    stops: List[TmsStop]
    timeline_events: List[TmsShipmentEvent]
