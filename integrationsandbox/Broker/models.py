from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class BrokerEventType(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    CANCEL_ORDER = "CANCEL_ORDER"
    DRIVING_TO_LOAD = "DRIVING_TO_LOAD"
    ORDER_LOADED = "ORDER_LOADED"
    ETA_EVENT = "ETA_EVENT"
    ORDER_DELIVERED = "ORDER_DELIVERED"


class BrokerOrderMeta(BaseModel):
    senderId: str
    messageDate: datetime
    messageReference: str
    messageFunction: int


class BrokerDate(BaseModel):
    qualifier: str
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
    loadingMeters: float


class BrokerHandlingUnit(BaseModel):
    packagingQualifier: str
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


class BrokerShipment(BaseModel):
    reference: str
    carrier: str
    transportMode: str
    orders: List[BrokerOder]


class BokerOrderMessage(BaseModel):
    meta: BrokerOrderMeta
    shipment: BrokerShipment


class BrokerEventOrder(BaseModel):
    reference: str
    eta: Optional[datetime]


class BrokerEventPosition(BaseModel):
    locationReference: str
    latitude: float
    longitude: float


class BrokerEventSituation(BaseModel):
    event: BrokerEventType
    registrationDate: datetime
    actualDate: datetime
    position: BrokerEventPosition


class BrokerEventMessage(BaseModel):
    id: str
    shipmentId: str
    dateTransmission: datetime
    owner: str
    order: BrokerEventOrder
    situation: BrokerEventSituation
    carrier: str
