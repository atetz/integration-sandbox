from typing import List

import httpx

from integrationsandbox.broker.factories import BrokerEventMessageFactory
from integrationsandbox.broker.models import BrokerEventMessage, BrokerEventType
from integrationsandbox.broker.repository import create_events
from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.tms.repository import create_shipments, get_shipments_by_id
from integrationsandbox.tms.service import (
    create_shipments_from_factory,
    get_location_for_event,
)
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger


def dispatch_shipments_to_url(shipments: List[TmsShipment], url: str) -> None:
    # model_dump(mode="json") prevents escaped json being sent.
    data = [shipment.model_dump(mode="json") for shipment in shipments]
    r = httpx.post(url, json=data)
    r.raise_for_status()


def create_and_dispatch_shipments(trigger: ShipmentTrigger):
    shipments = create_shipments_from_factory(trigger.count)
    create_shipments(shipments)
    dispatch_shipments_to_url(shipments, trigger.target_url.encoded_string())
    return shipments


def create_events_from_factory(
    shipments: List[TmsShipment], event: BrokerEventType
) -> List[BrokerEventMessage]:
    factory = BrokerEventMessageFactory()
    events = [
        factory.create_event_message(
            shipment_id=shipment.id,
            owner_name="Adam's logistics",
            reference=shipment.external_reference,
            event_type=event,
            carrier_name=shipment.customer.carrier,
            location_reference=get_location_for_event(shipment, event),
        )
        for shipment in shipments
    ]
    return events


# dedup later if needed.
def dispatch_events_to_url(events: List[BrokerEventMessage], url: str) -> None:
    data = [event.model_dump(mode="json") for event in events]
    r = httpx.post(url, json=data)
    r.raise_for_status()


def create_and_dispatch_events(trigger: EventTrigger) -> List[BrokerEventMessage]:
    shipments = get_shipments_by_id(trigger.shipment_ids)
    events = create_events_from_factory(shipments, trigger.event)
    create_events(events)
    dispatch_events_to_url(events, trigger.target_url.encoded_string())
    return events
