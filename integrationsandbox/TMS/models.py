from datetime import date, datetime, time
from enum import Enum, auto
from typing import List, Optional

from pydantic import BaseModel


class PackageType(Enum):
    BALE = auto()
    BOX = auto()
    COIL = auto()
    CRATE = auto()
    CYLINDER = auto()
    DRUM = auto()
    OTHER = auto()
    PLT = auto()


class StopType(Enum):
    PICKUP = auto()
    DELIVERY = auto()


class EventType(Enum):
    BOOKED = auto()
    CANCELLED = auto()
    DELIVERED = auto()
    DISPATCHED = auto()
    ETA_CHANGED = auto()
    PICKED_UP = auto()


class EquipmentType(Enum):
    TRUCK_AND_TRAILER = auto()
    FLATBED_53_FOOT = auto()
    MOVING_VAN = auto()
    CONTAINER = auto()


class ModeType(Enum):
    FTL = auto()
    LTL = auto()


class TmsCustomer(BaseModel):
    id: str
    name: str
    carrier: str


class TmsLineItem(BaseModel):
    package_type: Optional[PackageType]
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
    address: Optional[TmsAddress]
    latitude: float
    longitude: float


class TmsStop(BaseModel):
    type: StopType
    location: TmsLocation
    planned_date: date
    planned_time_window_start: time
    planned_time_window_end: time


class TmsShipmentEvent(BaseModel):
    id: int
    created_at: datetime
    event_type: EventType
    occured_at: datetime
    source: str
    location: TmsLocation


class TmsShipment(BaseModel):
    id: str
    external_reference: str
    mode: ModeType
    equipment_type: EquipmentType
    customer: TmsCustomer
    line_items: List[TmsLineItem]
    stops: List[TmsStop]
    timeline_events: List[TmsShipmentEvent]
