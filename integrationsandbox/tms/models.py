from datetime import date, datetime, time
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, PositiveInt

from integrationsandbox.config import get_settings
from integrationsandbox.tms.payload_examples import (
    tms_create_event_example,
    tms_create_shipment_example,
    tms_event_example,
    tms_shipment_example,
    tms_shipment_seed_example,
)


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
    external_order_reference: str | None
    source: str
    location: TmsLocation | None = None

    model_config = tms_create_event_example


# I like ID at top.
class TmsShipmentEvent(BaseModel):
    id: str
    external_order_reference: str | None
    created_at: datetime
    event_type: TmsEventType
    occured_at: datetime
    external_order_reference: str | None
    source: str
    location: TmsLocation | None = None

    model_config = tms_event_example


class CreateTmsShipment(BaseModel):
    external_reference: str | None
    mode: ModeType
    equipment_type: EquipmentType
    loading_meters: float
    customer: TmsCustomer
    line_items: List[TmsLineItem] = Field(min_length=1)
    stops: List[TmsStop] = Field(min_length=2)
    timeline_events: List[TmsShipmentEvent] | None = None

    model_config = tms_create_shipment_example


# duplicated because I want ID on top
class TmsShipment(BaseModel):
    id: str
    external_reference: str | None
    mode: ModeType
    equipment_type: EquipmentType
    loading_meters: float
    customer: TmsCustomer
    line_items: List[TmsLineItem] = Field(min_length=1)
    stops: List[TmsStop] = Field(min_length=2)
    timeline_events: List[TmsShipmentEvent] | None = None

    def update_timeline_events(self, new_event: TmsShipmentEvent) -> None:
        if self.timeline_events is None:
            self.timeline_events = []
        for i, event in enumerate(self.timeline_events):
            if event.event_type == new_event.event_type:
                self.timeline_events[i] = new_event
                return
        self.timeline_events.append(new_event)

    model_config = tms_shipment_example


class TmsShipmentSeedRequest(BaseModel):
    count: PositiveInt = Field(
        description="Number of broker events to generate and save.",
        le=get_settings().max_bulk_size,
    )
    model_config = tms_shipment_seed_example


class TmsShipmentFilters(BaseModel):
    id: str | None = None
    start: int | None = 0
    limit: int | None = 50
