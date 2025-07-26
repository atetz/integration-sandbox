from datetime import date, datetime, time
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, PositiveInt

from integrationsandbox.tms.payload_examples import tms_shipment_seed


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


class TmsEventType(str, Enum):
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
    package_type: PackageType | None
    stackable: bool
    height: float | None
    length: float | None
    width: float | None
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
    name: str | None = None
    address: TmsAddress | None = None
    latitude: float
    longitude: float


class TmsStop(BaseModel):
    type: StopType
    location: TmsLocation
    planned_date: date
    planned_time_window_start: time
    planned_time_window_end: time


class CreateTmsShipmentEvent(BaseModel):
    created_at: datetime
    event_type: TmsEventType
    occured_at: datetime
    source: str
    location: TmsLocation | None = None


class TmsShipmentEvent(CreateTmsShipmentEvent):
    id: str


class CreateTmsShipment(BaseModel):
    external_reference: str | None
    mode: ModeType
    equipment_type: EquipmentType
    loading_meters: float
    customer: TmsCustomer
    line_items: List[TmsLineItem]
    stops: List[TmsStop]
    timeline_events: List[TmsShipmentEvent] | None = None


# duplicated because I want ID on top
class TmsShipment(CreateTmsShipment):
    id: str
    external_reference: str | None
    mode: ModeType
    equipment_type: EquipmentType
    loading_meters: float
    customer: TmsCustomer
    line_items: List[TmsLineItem]
    stops: List[TmsStop]
    timeline_events: List[TmsShipmentEvent] | None = None


class TmsShipmentSeedRequest(BaseModel):
    count: PositiveInt = Field(
        description="Number of broker events to generate and save.", le=1000
    )
    model_config = tms_shipment_seed


# bit overkill for now but maybe we'll get more filters later. Keeping it the same as broker.
class TmsShipmentFilters(BaseModel):
    id: str | None = None
    start: int | None = 0
    limit: int | None = 50
