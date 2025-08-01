"""
Created this service because:
    - Broker validates orders against TMS shipments
    - TMS validates events against broker messages
  This creates legitimate circular dependency because both domains need each other.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from deepdiff import DeepDiff

from integrationsandbox.broker.models import (
    BrokerEventFilters,
    CreateBrokerOrderMessage,
)
from integrationsandbox.broker.service import (
    apply_shipment_mapping_rules,
    get_event,
    get_transformed_shipment_data,
)
from integrationsandbox.common.exceptions import ValidationError
from integrationsandbox.config import get_settings
from integrationsandbox.tms.models import CreateTmsShipmentEvent
from integrationsandbox.tms.service import (
    REVERSE_EVENT_TYPE_MAP,
    apply_event_mapping_rules,
    get_shipment_by_id,
    get_transformed_event_data,
)

logger = logging.getLogger(__name__)


def serialize_value(value):
    # Normalizes data structures for deep comparison by converting Pydantic models to dicts
    if hasattr(value, "model_dump"):
        return value.model_dump()
    elif isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat()
    elif isinstance(value, float):
        return round(value, get_settings().float_precision)
    elif isinstance(value, set):
        return list(value)
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    return value


def compare_mappings(tms_data: Dict[str, Any], broker_data: Dict[str, Any]) -> bool:
    logger.info(
        "Comparing %d fields between TMS and broker data",
        len(set(tms_data.keys()) | set(broker_data.keys())),
    )
    errors = []
    all_keys = set(tms_data.keys()) | set(broker_data.keys())

    for key in all_keys:
        if key not in tms_data:
            errors.append({"field": key, "error": "missing in tms_data"})
        elif key not in broker_data:
            errors.append({"field": key, "error": "missing in broker_data"})
        else:
            tms_serialized = serialize_value(tms_data[key])
            broker_serialized = serialize_value(broker_data[key])

            diff = DeepDiff(
                tms_serialized, broker_serialized, ignore_order=True, verbose_level=1
            )

            if diff:
                errors.append(
                    {
                        "field": key,
                        "differences": diff.to_dict(),
                        "expected": tms_serialized,
                        "actual": broker_serialized,
                    }
                )
    if errors:
        logger.warning("Validation failed with %d errors", len(errors))
        logger.debug("Validation errors: %s", errors)
        raise ValidationError(errors)

    logger.info("Validation successful - all fields match")
    return True


def validate_broker_order(
    order: CreateBrokerOrderMessage,
) -> Tuple[bool, List[str | None]]:
    shipment_reference = order.shipment.reference
    logger.info("Validating broker order for shipment: %s", shipment_reference)
    tms_shipment = get_shipment_by_id(shipment_reference)
    expected_data = apply_shipment_mapping_rules(tms_shipment)
    transformed_data = get_transformed_shipment_data(order)
    return compare_mappings(expected_data, transformed_data)


def validate_tms_event(
    event: CreateTmsShipmentEvent, shipment_id: str
) -> Tuple[bool, List[str | None]]:
    event_type = REVERSE_EVENT_TYPE_MAP[event.event_type]
    logger.info("Validating TMS event %s for shipment: %s", event_type, shipment_id)
    event_filter = BrokerEventFilters(shipment_id=shipment_id, event_type=event_type)
    broker_event = get_event(event_filter)
    expected_data = apply_event_mapping_rules(broker_event)
    transformed_data = get_transformed_event_data(event)
    return compare_mappings(expected_data, transformed_data)
