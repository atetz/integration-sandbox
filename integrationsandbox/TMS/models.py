from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class PackageType(str, Enum):
    BALE = "BALE"
    BOX = "BOX"
    COIL = "COIL"
    CRATE = "CRATE"
    CYLINDER = "CYLINDER"
    DRUM = "DRUM"
    OTHER = "OTHER"
    PLT = "PLT"


class StopType(str, Enum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class EventType(str, Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    DELIVERED = "DELIVERED"
    DISPATCHED = "DISPATCHED"
    ETA_CHANGED = "ETA_CHANGED"
    PICKED_UP = "PICKED_UP"


class EquipmentType(str, Enum):
    TRUCK_AND_TRAILER = "TRUCK_AND_TRAILER"
    FLATBED_53_FOOT = "FLATBED_53_FOOT"
    MOVING_VAN = "MOVING_VAN"
    CONTAINER = "CONTAINER"


class ModeType(str, Enum):
    FTL = "FTL"
    LTL = "LTL"


class TmsCustomer(BaseModel):
    id: str
    name: str
    carrier: str


class TmsLineItem(BaseModel):
    package_type: Optional[PackageType]
    stackable: bool
    height: Optional[float]
    length: Optional[float]
    width: Optional[float]
    length_unit: str
    package_weight: float
    weight_unit: str
    description: str
    total_packages: int


class TmsAddress(BaseModel):
    address: str
    city: str
    postal_code: str
    country: str


class TmsLocation(BaseModel):
    code: str
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
    external_reference: Optional[str]
    mode: ModeType
    equipment_type: EquipmentType
    customer: TmsCustomer
    line_items: List[TmsLineItem]
    stops: List[TmsStop]
    timeline_events: Optional[List[TmsShipmentEvent]]
