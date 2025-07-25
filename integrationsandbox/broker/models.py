from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from integrationsandbox.broker.payload_examples import create_broker_message


class BrokerEventType(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    CANCEL_ORDER = "CANCEL_ORDER"
    DRIVING_TO_LOAD = "DRIVING_TO_LOAD"
    ORDER_LOADED = "ORDER_LOADED"
    ETA_EVENT = "ETA_EVENT"
    ORDER_DELIVERED = "ORDER_DELIVERED"


class BrokerPackagingQualifier(str, Enum):
    BL = "BL"
    BX = "BX"
    CL = "CL"
    CR = "CR"
    CY = "CY"
    DR = "DR"
    OT = "OT"
    PL = "PL"


class BrokerDateQualifier(str, Enum):
    PERIOD_EARLIEST = "PERIOD_EARLIEST"
    PERIOD_LATEST = "PERIOD_LATEST"


class BrokerOrderMeta(BaseModel):
    senderId: str
    messageDate: datetime
    messageReference: str
    messageFunction: int


class BrokerDate(BaseModel):
    qualifier: BrokerDateQualifier
    dateTime: datetime


class BrokerLocation(BaseModel):
    identification: str
    name: str
    address1: str
    address2: str
    country: str
    postalCode: str
    city: str
    latitude: float
    longitude: float
    instructions: str
    dates: List[BrokerDate]


class BrokerQuantity(BaseModel):
    grossWeight: float
    loadingMeters: float | None


class BrokerHandlingUnit(BaseModel):
    packagingQualifier: BrokerPackagingQualifier
    grossWeight: float
    width: float
    length: float
    height: float


class BrokerOder(BaseModel):
    reference: str
    pickUp: BrokerLocation
    consignee: BrokerLocation
    goodsDescription: str
    quantity: BrokerQuantity
    handlingUnits: List[BrokerHandlingUnit]


class CreateBrokerShipment(BaseModel):
    reference: str
    carrier: str
    transportMode: str
    orders: List[BrokerOder]


class CreateBrokerOrderMessage(BaseModel):
    meta: BrokerOrderMeta
    shipment: CreateBrokerShipment

    model_config = create_broker_message


class BrokerShipment(BaseModel):
    id: str
    reference: str
    carrier: str
    transportMode: str
    orders: List[BrokerOder]


class BrokerOrderMessage(BaseModel):
    meta: BrokerOrderMeta
    shipment: BrokerShipment


class BrokerEventOrder(BaseModel):
    reference: str
    eta: datetime | None


class BrokerEventPosition(BaseModel):
    locationReference: str
    latitude: float
    longitude: float


class BrokerEventSituation(BaseModel):
    event: BrokerEventType
    registrationDate: datetime
    actualDate: datetime
    position: BrokerEventPosition | None = None


class BrokerEventMessage(BaseModel):
    id: str
    shipmentId: str
    dateTransmission: datetime
    owner: str
    order: BrokerEventOrder
    situation: BrokerEventSituation
    carrier: str


class BrokerEventSeedRequest(BaseModel):
    event: BrokerEventType = Field(
        description="Type of event to generate for all shipments"
    )
    shipment_ids: List[str] = Field(
        description="List of shipment IDs to generate events for. Supports multiple shipments for bulk testing.",
        max_length=1000,
    )


class EventFilters(BaseModel):
    id: str | None = None
    event: BrokerEventType | None = None
    shipment_id: str | None = None
