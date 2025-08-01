from datetime import date, datetime, time

import pytest

from integrationsandbox.broker.models import (
    BrokerDateQualifier,
    BrokerLocation,
    BrokerPackagingQualifier,
)
from integrationsandbox.broker.service import (
    apply_shipment_mapping_rules,
    get_stop_dates,
    get_tms_stop_by_type,
    map_address_details,
    map_line_items,
)
from integrationsandbox.tms.models import (
    EquipmentType,
    ModeType,
    PackageType,
    StopType,
    TmsAddress,
    TmsCustomer,
    TmsLineItem,
    TmsLocation,
    TmsShipment,
    TmsStop,
)


def test_get_tms_stop_by_type_found():
    address = TmsAddress(
        address="123 Main St", city="Test City", postal_code="12345", country="US"
    )
    location = TmsLocation(
        code="LOC001",
        name="Test Location",
        address=address,
        latitude=40.7,
        longitude=-74.0,
    )

    stops = [
        TmsStop(
            type=StopType.PICKUP,
            location=location,
            planned_date=date(2024, 1, 15),
            planned_time_window_start=time(9, 0),
            planned_time_window_end=time(17, 0),
        ),
        TmsStop(
            type=StopType.DELIVERY,
            location=location,
            planned_date=date(2024, 1, 16),
            planned_time_window_start=time(8, 0),
            planned_time_window_end=time(16, 0),
        ),
    ]
    result = get_tms_stop_by_type(stops, "PICKUP")
    assert result.type == StopType.PICKUP


def test_get_tms_stop_by_type_not_found():
    address = TmsAddress(
        address="123 Main St", city="Test City", postal_code="12345", country="US"
    )
    location = TmsLocation(
        code="LOC001",
        name="Test Location",
        address=address,
        latitude=40.7,
        longitude=-74.0,
    )

    stops = [
        TmsStop(
            type=StopType.PICKUP,
            location=location,
            planned_date=date(2024, 1, 15),
            planned_time_window_start=time(9, 0),
            planned_time_window_end=time(17, 0),
        ),
    ]
    with pytest.raises(ValueError, match="No stop found with type: DELIVERY"):
        get_tms_stop_by_type(stops, "DELIVERY")


def test_get_stop_dates():
    address = TmsAddress(
        address="123 Main St", city="Test City", postal_code="12345", country="US"
    )
    location = TmsLocation(
        code="LOC001",
        name="Test Location",
        address=address,
        latitude=40.7,
        longitude=-74.0,
    )

    stop = TmsStop(
        type=StopType.PICKUP,
        location=location,
        planned_date=date(2024, 1, 15),
        planned_time_window_start=time(9, 0),
        planned_time_window_end=time(17, 0),
    )

    result = get_stop_dates(stop)

    assert len(result) == 2
    assert result[0].qualifier == BrokerDateQualifier.PERIOD_EARLIEST
    assert result[0].dateTime == datetime(2024, 1, 15, 9, 0)
    assert result[1].qualifier == BrokerDateQualifier.PERIOD_LATEST
    assert result[1].dateTime == datetime(2024, 1, 15, 17, 0)


def test_map_address_details(tms_line_items, tms_stops):
    customer = TmsCustomer(id="CUST001", name="Test Customer", carrier="Test Carrier")
    shipment = TmsShipment(
        id="SH001",
        external_reference=None,
        mode=ModeType.FTL,
        equipment_type=EquipmentType.TRUCK_AND_TRAILER,
        customer=customer,
        loading_meters=10.0,
        stops=tms_stops,
        line_items=tms_line_items,
        timeline_events=None,
    )

    result = map_address_details(shipment, "PICKUP")

    assert result.identification == "PU001"
    assert result.name == "Pickup Location"
    assert result.address1 == "123 Pickup St"
    assert result.city == "Origin City"
    assert result.country == "US"
    assert result.postalCode == "12345"
    assert result.latitude == 40.7128
    assert result.longitude == -74.0060
    assert len(result.dates) == 2


def test_map_line_items(tms_stops):
    line_items = [
        TmsLineItem(
            package_type=PackageType.BOX,
            stackable=True,
            height=1.5,
            length=2.0,
            width=1.0,
            length_unit="m",
            package_weight=10.5,
            weight_unit="kg",
            description="Item 1",
            total_packages=2,
        ),
        TmsLineItem(
            package_type=PackageType.PLT,
            stackable=False,
            height=1.8,
            length=0.8,
            width=1.2,
            length_unit="m",
            package_weight=25.0,
            weight_unit="kg",
            description="Item 2",
            total_packages=1,
        ),
    ]
    customer = TmsCustomer(id="CUST001", name="Test Customer", carrier="Test Carrier")
    shipment = TmsShipment(
        id="SH001",
        external_reference=None,
        mode=ModeType.FTL,
        equipment_type=EquipmentType.TRUCK_AND_TRAILER,
        customer=customer,
        loading_meters=10.0,
        stops=tms_stops,
        line_items=line_items,
        timeline_events=None,
    )

    result = map_line_items(shipment)

    assert len(result) == 3  # 2 boxes + 1 pallet
    assert result[0].packagingQualifier == BrokerPackagingQualifier.BX
    assert result[0].grossWeight == 10.5
    assert result[1].packagingQualifier == BrokerPackagingQualifier.BX
    assert result[2].packagingQualifier == BrokerPackagingQualifier.PL
    assert result[2].grossWeight == 25.0


def test_apply_shipment_mapping_rules():
    address = TmsAddress(
        address="123 Main St", city="Anytown", postal_code="12345", country="US"
    )
    pickup_location = TmsLocation(
        code="PU001",
        name="Pickup Location",
        address=address,
        latitude=40.7,
        longitude=-74.0,
    )
    delivery_location = TmsLocation(
        code="DEL001",
        name="Delivery Location",
        address=address,
        latitude=40.8,
        longitude=-74.1,
    )

    pickup_stop = TmsStop(
        type=StopType.PICKUP,
        location=pickup_location,
        planned_date=date(2024, 1, 15),
        planned_time_window_start=time(9, 0),
        planned_time_window_end=time(17, 0),
    )
    delivery_stop = TmsStop(
        type=StopType.DELIVERY,
        location=delivery_location,
        planned_date=date(2024, 1, 16),
        planned_time_window_start=time(8, 0),
        planned_time_window_end=time(16, 0),
    )

    line_item = TmsLineItem(
        package_type=PackageType.BOX,
        stackable=True,
        height=1.0,
        length=1.0,
        width=1.0,
        length_unit="m",
        package_weight=10.0,
        weight_unit="kg",
        description="Test Item",
        total_packages=1,
    )

    customer = TmsCustomer(id="CUST001", name="Test Customer", carrier="Test Carrier")

    shipment = TmsShipment(
        id="SH001",
        external_reference=None,
        mode=ModeType.FTL,
        equipment_type=EquipmentType.TRUCK_AND_TRAILER,
        customer=customer,
        loading_meters=5.0,
        stops=[pickup_stop, delivery_stop],
        line_items=[line_item],
        timeline_events=None,
    )

    result = apply_shipment_mapping_rules(shipment)

    assert result["meta_message_function"] == 9
    assert result["shipment_reference"] == "SH001"
    assert result["shipment_carrier"] == "Test Carrier"
    assert result["shipment_transportmode"] == "ROAD"
    assert result["order_reference"] == "SH001"
    assert isinstance(result["order_pickup_details"], BrokerLocation)
    assert isinstance(result["order_consignee_details"], BrokerLocation)
    assert result["order_goods_description"] == {"Test Item"}
    assert result["order_quantities"].grossWeight == 10.0
    assert result["order_quantities"].loadingMeters == 5.0
    assert len(result["order_handling_units"]) == 1
