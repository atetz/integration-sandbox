from collections import defaultdict
from typing import List

from integrationsandbox.broker.models import (
    BrokerHandlingUnit,
    BrokerPackagingQualifier,
    CreateBrokerOrderMessage,
)
from integrationsandbox.tms.models import PackageType, TmsLineItem
from integrationsandbox.tms.repository import get_shipment_by_id
from tests.fixtures import broker_order_example, tms_shipment_example

REVERSE_PACKAGE_MAP = {
    BrokerPackagingQualifier.BL: PackageType.BALE,
    BrokerPackagingQualifier.BX: PackageType.BOX,
    BrokerPackagingQualifier.CL: PackageType.COIL,
    BrokerPackagingQualifier.CY: PackageType.CYLINDER,
    BrokerPackagingQualifier.DR: PackageType.DRUM,
    BrokerPackagingQualifier.OT: PackageType.OTHER,
    BrokerPackagingQualifier.PL: PackageType.PLT,
}


def validate_line_items(
    tms_lines: List[TmsLineItem], broker_lines: List[BrokerHandlingUnit]
):
    failures = []

    # Create unique key with values and line count for comparison.
    tms_lines_groups = {}
    for item in tms_lines:
        key = (
            item.package_type,
            item.package_weight,
            item.width,
            item.length,
            item.height,
        )
        tms_lines_groups[key] = item.total_packages

    broker_lines_groups = defaultdict(int)

    for item in broker_lines:
        key = (
            REVERSE_PACKAGE_MAP[item.packagingQualifier],
            item.grossWeight,
            item.width,
            item.length,
            item.height,
        )
        broker_lines_groups[key] += 1

    if tms_lines_groups != broker_lines_groups:
        failures.append("Order lines mismatch:")
        failures.append(f"TMS lines: {tms_lines_groups}")
        failures.append(f"Broker lines: {broker_lines_groups}")

    return len(failures) == 0, failures


def validate_order(broker_order: CreateBrokerOrderMessage) -> None:
    tms_shipment = get_shipment_by_id(broker_order.shipment.reference)

    tms_shipment_lines = tms_shipment.line_items
    broker_order_lines = broker_order.shipment.orders[0].handlingUnits

    validate_line_items(tms_shipment_lines, broker_order_lines)


def main() -> None:
    tms_shipment = tms_shipment_example.shipment
    broker_order = broker_order_example.broker_message

    tms_shipment_lines = tms_shipment.line_items
    broker_order_lines = broker_order.shipment.orders[0].handlingUnits

    result = validate_line_items(tms_shipment_lines, broker_order_lines)
    print(result)


if __name__ == "__main__":
    main()
