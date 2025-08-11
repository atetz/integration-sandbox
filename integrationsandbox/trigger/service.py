import logging
from typing import List

import httpx

from integrationsandbox.broker.models import BrokerEventMessage
from integrationsandbox.broker.service import build_events, create_events
from integrationsandbox.common.exceptions import ValidationError
from integrationsandbox.config import get_settings
from integrationsandbox.tms.models import TmsShipment
from integrationsandbox.tms.service import (
    build_shipments,
    create_shipments,
    get_shipments_by_id_list,
)
from integrationsandbox.trigger.models import EventTrigger, ShipmentTrigger

logger = logging.getLogger(__name__)


def dispatch_shipments_to_url(shipments: List[TmsShipment], url: str) -> None:
    logger.info("Dispatching %d shipments to %s", len(shipments), url)
    # model_dump(mode="json") prevents escaped json being sent.
    headers = {"X-API-KEY": get_settings().trigger_api_key}
    data = [shipment.model_dump(mode="json") for shipment in shipments]
    r = httpx.post(url, json=data, headers=headers)
    r.raise_for_status()
    logger.info("Successfully dispatched shipments, response status: %d", r.status_code)


def create_and_dispatch_shipments(trigger: ShipmentTrigger):
    logger.info("Creating %d shipments", trigger.count)
    shipments = build_shipments(trigger.count)
    create_shipments(shipments)
    logger.info("Shipments created successfully")
    dispatch_shipments_to_url(shipments, trigger.target_url.encoded_string())
    return shipments


# dedup later if needed.
def dispatch_events_to_url(events: List[BrokerEventMessage], url: str) -> None:
    logger.info("Dispatching %d events to %s", len(events), url)
    headers = {"X-API-KEY": get_settings().trigger_api_key}
    data = [event.model_dump(mode="json") for event in events]
    r = httpx.post(url, json=data, headers=headers)
    r.raise_for_status()
    logger.info("Successfully dispatched events, response status: %d", r.status_code)


def create_and_dispatch_events(trigger: EventTrigger) -> List[BrokerEventMessage]:
    if not trigger.shipment_ids:
        raise ValidationError("No shipment_ids received.")
    logger.info(
        "Creating events for %d shipments with event type: %s",
        len(trigger.shipment_ids),
        trigger.event,
    )
    shipments = get_shipments_by_id_list(trigger.shipment_ids)
    events = build_events(shipments, trigger.event)
    create_events(events)
    logger.info("Events created successfully")
    dispatch_events_to_url(events, trigger.target_url.encoded_string())
    return events
