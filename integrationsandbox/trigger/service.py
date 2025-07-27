from typing import List

import httpx

from integrationsandbox.broker.models import BrokerEventMessage
from integrationsandbox.broker.service import build_events, create_events
from integrationsandbox.common.exceptions import ValidationError
from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.tms.service import (
    build_shipments,
    create_shipments,
    get_shipments_by_id_list,
)
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger


def dispatch_shipments_to_url(shipments: List[TmsShipment], url: str) -> None:
    # model_dump(mode="json") prevents escaped json being sent.
    data = [shipment.model_dump(mode="json") for shipment in shipments]
    r = httpx.post(url, json=data)
    r.raise_for_status()


def create_and_dispatch_shipments(trigger: ShipmentTrigger):
    shipments = build_shipments(trigger.count)
    create_shipments(shipments)
    dispatch_shipments_to_url(shipments, trigger.target_url.encoded_string())
    return shipments


# dedup later if needed.
def dispatch_events_to_url(events: List[BrokerEventMessage], url: str) -> None:
    data = [event.model_dump(mode="json") for event in events]
    r = httpx.post(url, json=data)
    r.raise_for_status()


def create_and_dispatch_events(trigger: EventTrigger) -> List[BrokerEventMessage]:
    if not trigger.shipment_ids:
        raise ValidationError("No shipment_ids received.")
    shipments = get_shipments_by_id_list(trigger.shipment_ids)
    events = build_events(shipments, trigger.event)
    create_events(events)
    dispatch_events_to_url(events, trigger.target_url.encoded_string())
    return events
