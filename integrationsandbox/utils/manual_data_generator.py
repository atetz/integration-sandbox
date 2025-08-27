"""
Manual data generation utilities for testing integration flows.

This module provides utilities for manually generating shipment JSON and transformed
broker orders, useful for debugging and manual testing of integration scenarios.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict

from integrationsandbox.broker.models import (
    BrokerEventType,
    BrokerOder,
    BrokerOrderMeta,
    CreateBrokerOrderMessage,
    CreateBrokerShipment,
)
from integrationsandbox.broker.service import apply_shipment_mapping_rules, build_events
from integrationsandbox.tms.factories import TmsShipmentFactory
from integrationsandbox.tms.models import TmsEventType, TmsShipment, TmsShipmentEvent

# Mapping between broker events and corresponding TMS events
BROKER_TO_TMS_EVENT_MAP = {
    BrokerEventType.ORDER_CREATED: TmsEventType.BOOKED,
    BrokerEventType.ORDER_LOADED: TmsEventType.PICKED_UP,
    BrokerEventType.ORDER_DELIVERED: TmsEventType.DELIVERED,
    BrokerEventType.CANCEL_ORDER: TmsEventType.CANCELLED,
    BrokerEventType.DRIVING_TO_LOAD: TmsEventType.DISPATCHED,
    BrokerEventType.ETA_EVENT: TmsEventType.ETA_CHANGED,
}


def generate_complete_flow(
    event_type: BrokerEventType = BrokerEventType.ORDER_CREATED,
) -> Dict[str, Any]:
    """
    Generate a complete flow using the same shipment for both order and event.

    Args:
        event_type: The type of broker event to generate

    Returns:
        Dict containing all data from the same shipment
    """
    factory = TmsShipmentFactory()
    new_shipment = factory.create_new_shipment()

    # apply_shipment_mapping_rules needs an id
    shipment = TmsShipment(id="REPLACEME", **new_shipment.model_dump())

    # Get the mapping transformation for broker order
    mapping = apply_shipment_mapping_rules(shipment)

    # Build the broker order using proper models
    meta = BrokerOrderMeta(
        senderId="TEST_SENDER",
        messageDate=datetime.now(),
        messageReference="MSG001",
        messageFunction=mapping["meta_message_function"],
    )

    broker_order_data = BrokerOder(
        reference="REPLACEME",
        pickUp=mapping["order_pickup_details"],
        consignee=mapping["order_consignee_details"],
        goodsDescription="|".join(mapping["order_goods_description"]),
        quantity=mapping["order_quantities"],
        handlingUnits=mapping["order_handling_units"],
    )

    broker_shipment = CreateBrokerShipment(
        reference="REPLACEME",
        carrier=mapping["shipment_carrier"],
        transportMode=mapping["shipment_transportmode"],
        orders=[broker_order_data],
    )

    broker_order = CreateBrokerOrderMessage(
        meta=meta,
        shipment=broker_shipment,
    )

    # Generate broker event and TMS event from the same shipment
    events = build_events([shipment], event_type)
    broker_event = events[0] if events else None

    # Generate the corresponding TMS event
    tms_event_type = BROKER_TO_TMS_EVENT_MAP.get(event_type, TmsEventType.BOOKED)
    now = datetime.now()

    tms_event = TmsShipmentEvent(
        id=str(uuid.uuid4()),
        external_order_reference="EXT001",
        created_at=now,
        event_type=tms_event_type,
        occured_at=now,
        source="MANUAL_GENERATION",
        location=shipment.stops[0].location if shipment.stops else None,
    )

    return {
        "shipment": shipment.model_dump(mode="json"),
        "broker_order": broker_order.model_dump(mode="json"),
        "broker_event": broker_event.model_dump(mode="json") if broker_event else None,
        "tms_event": tms_event.model_dump(mode="json"),
    }


def print_complete_flow(event_type: BrokerEventType = BrokerEventType.ORDER_CREATED):
    """Print a formatted complete flow for manual inspection."""
    data = generate_complete_flow(event_type)

    print("=== TMS SHIPMENT ===")
    print(json.dumps(data["shipment"], indent=2))

    print("\n=== TRANSFORMED BROKER ORDER ===")
    print(json.dumps(data["broker_order"], indent=2))

    print("\n=== BROKER EVENT ===")
    print(json.dumps(data["broker_event"], indent=2))

    print("\n=== TMS EVENT ===")
    print(json.dumps(data["tms_event"], indent=2))


if __name__ == "__main__":
    print("Generating complete integration flow...")
    print_complete_flow()
