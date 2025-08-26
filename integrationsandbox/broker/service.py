import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from integrationsandbox.broker import repository
from integrationsandbox.broker.factories import BrokerEventMessageFactory
from integrationsandbox.broker.models import (
    BrokerDate,
    BrokerDateQualifier,
    BrokerEventFilters,
    BrokerEventMessage,
    BrokerEventType,
    BrokerHandlingUnit,
    BrokerLocation,
    BrokerPackagingQualifier,
    BrokerQuantity,
    CreateBrokerEventMessage,
    CreateBrokerOrderMessage,
)
from integrationsandbox.common.exceptions import NotFoundError
from integrationsandbox.tms.models import PackageType, TmsShipment, TmsStop

logger = logging.getLogger(__name__)

PACKAGE_MAP = {
    PackageType.BALE: BrokerPackagingQualifier.BL,
    PackageType.BOX: BrokerPackagingQualifier.BX,
    PackageType.CRATE: BrokerPackagingQualifier.CR,
    PackageType.COIL: BrokerPackagingQualifier.CL,
    PackageType.CYLINDER: BrokerPackagingQualifier.CY,
    PackageType.DRUM: BrokerPackagingQualifier.DR,
    PackageType.OTHER: BrokerPackagingQualifier.OT,
    PackageType.PLT: BrokerPackagingQualifier.PL,
}


NEW_MESSAGE_FUNCTION = 9


def get_tms_stop_by_type(stops: List[TmsStop], location_type: str) -> TmsStop:
    for stop in stops:
        if stop.type == location_type:
            return stop
    raise ValueError(f"No stop found with type: {location_type}")


def get_location_for_event(
    shipment: TmsShipment, event_type: BrokerEventType
) -> str | None:
    if event_type in [BrokerEventType.DRIVING_TO_LOAD, BrokerEventType.ORDER_LOADED]:
        pickup_stop = get_tms_stop_by_type(shipment.stops, "PICKUP")
        return pickup_stop.location.code if pickup_stop else None
    elif event_type in [BrokerEventType.ORDER_DELIVERED, BrokerEventType.ETA_EVENT]:
        delivery_stop = get_tms_stop_by_type(shipment.stops, "DELIVERY")
        return delivery_stop.location.code if delivery_stop else None
    return None


def get_stop_dates(tms_stop: TmsStop) -> List[BrokerDate]:
    planned_date = tms_stop.planned_date
    planned_time_window_start = tms_stop.planned_time_window_start
    planned_time_window_end = tms_stop.planned_time_window_end

    period_earliest = datetime.combine(planned_date, planned_time_window_start)
    period_latest = datetime.combine(planned_date, planned_time_window_end)

    return [
        BrokerDate(
            qualifier=BrokerDateQualifier.PERIOD_EARLIEST, dateTime=period_earliest
        ),
        BrokerDate(qualifier=BrokerDateQualifier.PERIOD_LATEST, dateTime=period_latest),
    ]


def map_address_details(
    tms_shipment: TmsShipment, location_type: str
) -> BrokerLocation:
    tms_stop = get_tms_stop_by_type(tms_shipment.stops, location_type)

    return BrokerLocation(
        identification=tms_stop.location.code,
        name=tms_stop.location.name,
        address1=tms_stop.location.address.address,
        address2="",
        country=tms_stop.location.address.country,
        postalCode=tms_stop.location.address.postal_code,
        city=tms_stop.location.address.city,
        latitude=tms_stop.location.latitude,
        longitude=tms_stop.location.longitude,
        instructions="",
        dates=get_stop_dates(tms_stop),
    )


def map_line_items(tms_shipment: TmsShipment) -> List[BrokerHandlingUnit]:
    units = []
    for item in tms_shipment.line_items:
        for _ in range(item.total_packages):
            units.append(
                BrokerHandlingUnit(
                    packagingQualifier=PACKAGE_MAP[item.package_type],
                    grossWeight=item.package_weight,
                    width=item.width,
                    length=item.length,
                    height=item.height,
                )
            )
    return units


def apply_shipment_mapping_rules(tms_shipment: TmsShipment) -> Dict[str, Any]:
    result = {}
    result["meta_message_function"] = NEW_MESSAGE_FUNCTION
    result["shipment_reference"] = tms_shipment.id
    result["shipment_carrier"] = tms_shipment.customer.carrier
    result["shipment_transportmode"] = "ROAD"
    result["order_reference"] = tms_shipment.id
    result["order_pickup_details"] = map_address_details(tms_shipment, "PICKUP")
    result["order_consignee_details"] = map_address_details(tms_shipment, "DELIVERY")
    result["order_goods_description"] = set(
        item.description for item in tms_shipment.line_items
    )
    result["order_quantities"] = BrokerQuantity(
        loadingMeters=tms_shipment.loading_meters,
        grossWeight=sum(
            item.package_weight * item.total_packages
            for item in tms_shipment.line_items
        ),
    )
    result["order_handling_units"] = map_line_items(tms_shipment)

    return result


def get_transformed_shipment_data(
    broker_order: CreateBrokerOrderMessage,
) -> Dict[str, Any]:
    result = {}
    result["meta_message_function"] = broker_order.meta.messageFunction
    result["shipment_reference"] = broker_order.shipment.reference
    result["shipment_carrier"] = broker_order.shipment.carrier
    result["shipment_transportmode"] = broker_order.shipment.transportMode
    result["order_reference"] = broker_order.shipment.orders[0].reference
    result["order_pickup_details"] = broker_order.shipment.orders[0].pickUp
    result["order_consignee_details"] = broker_order.shipment.orders[0].consignee
    result["order_goods_description"] = set(
        desc.strip()
        for desc in broker_order.shipment.orders[0].goodsDescription.split("|")
    )
    result["order_quantities"] = broker_order.shipment.orders[0].quantity
    result["order_handling_units"] = broker_order.shipment.orders[0].handlingUnits

    return result


def build_events(
    shipments: List[TmsShipment], event: BrokerEventType
) -> List[BrokerEventMessage]:
    logger.info("Building %d broker events of type: %s", len(shipments), event)
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
    logger.info("Successfully built %d events", len(events))
    return events


def list_events(filters: BrokerEventFilters) -> List[BrokerEventMessage]:
    logger.info("Listing broker events with filters")
    logger.debug("Filters: %s", filters.model_dump() if filters else None)
    events = repository.get_all(filters)
    event_count = len(events) if events else 0
    logger.info("Retrieved %d events from database", event_count)

    return events


def get_event(filters: BrokerEventFilters) -> BrokerEventMessage:
    logger.info("Retrieving broker event with filters")
    logger.debug("Filters: %s", filters.model_dump())
    event = repository.get(filters)
    if not event:
        logger.warning("Event not found for filters: %s", filters)
        raise NotFoundError(f"Event not found for filters: {filters}")
    logger.info("Successfully retrieved event: %s", event.id)
    return event


def create_event(new_event: CreateBrokerEventMessage) -> BrokerEventMessage:
    logger.info("Creating new broker event")
    event = BrokerEventMessage(id=str(uuid.uuid4()), **new_event.model_dump())
    repository.create(event)
    logger.info("Successfully created event with ID: %s", event.id)
    return event


def create_events(events: List[BrokerEventMessage]) -> List[BrokerEventMessage]:
    if not events:
        logger.info("Empty events list provided")
        return []
    logger.info("Creating %d broker events", len(events))
    repository.create_many(events)
    logger.info("Successfully created %d events", len(events))
    return events


def create_seed_events(
    shipments: List[TmsShipment], event_type: BrokerEventType
) -> List[BrokerEventMessage]:
    logger.info(
        "Creating seed events for %d shipments with type: %s",
        len(shipments),
        event_type,
    )
    events = build_events(shipments, event_type)
    create_events(events)
    logger.info("Successfully created %d seed events", len(events))
    return events


def list_new_events(filters: BrokerEventFilters) -> List[BrokerEventMessage]:
    logger.info("Listing new broker events with filters")
    logger.debug("Filters: %s", filters.model_dump() if filters else None)
    filters.new = True
    events = repository.get_all(filters)
    event_count = len(events) if events else 0
    logger.info("Retrieved %d events from database", event_count)
    return events


def mark_event_processed(event_id: str) -> bool:
    logger.info("Marking broker event as processed: %s", event_id)
    success = repository.mark_as_processed(event_id)
    if success:
        logger.info("Successfully marked event as processed: %s", event_id)
    else:
        logger.warning("Failed to mark event as processed: %s", event_id)
    return success
