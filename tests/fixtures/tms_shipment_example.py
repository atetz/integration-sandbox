from datetime import date, time

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

customer = TmsCustomer(
    id="75831ed4-7d29-44a6-953f-066c2e3cd609",
    name="Clark-Acosta",
    carrier="Cole Ltd Transport",
)

line_items = [
    TmsLineItem(
        package_type=PackageType.BALE,
        stackable=False,
        height=115.15,
        length=138.51,
        width=20.88,
        length_unit="CM",
        package_weight=7069.62,
        weight_unit="KG",
        description="Commercial grade floor mats for high-traffic areas",
        total_packages=4,
    ),
    TmsLineItem(
        package_type=PackageType.CYLINDER,
        stackable=True,
        height=31.16,
        length=71.51,
        width=162.91,
        length_unit="CM",
        package_weight=2336.24,
        weight_unit="KG",
        description="Heavy-duty truck tires, new and retreaded options",
        total_packages=1,
    ),
    TmsLineItem(
        package_type=PackageType.CYLINDER,
        stackable=False,
        height=66.97,
        length=111.34,
        width=95.14,
        length_unit="CM",
        package_weight=890.43,
        weight_unit="KG",
        description="Industrial conveyor belt sections",
        total_packages=3,
    ),
]

pickup_address = TmsAddress(
    address="Borgo Buonauro, 27 Piano 6",
    city="Riva",
    postal_code="81046",
    country="IT",
)

pickup_location = TmsLocation(
    code="LOC-9973",
    name="Scamarcio e figli",
    address=pickup_address,
    latitude=9.223782,
    longitude=123.12346,
)

pickup_stop = TmsStop(
    type=StopType.PICKUP,
    location=pickup_location,
    planned_date=date(2025, 7, 22),
    planned_time_window_start=time(6, 0),
    planned_time_window_end=time(17, 0),
)

delivery_address = TmsAddress(
    address="Studio 6\nGill courts",
    city="Leonardtown",
    postal_code="WA7 6JT",
    country="GB",
)

delivery_location = TmsLocation(
    code="LOC-8521",
    name="Williams-Patel",
    address=delivery_address,
    latitude=13.042235,
    longitude=-168.601537,
)

delivery_stop = TmsStop(
    type=StopType.DELIVERY,
    location=delivery_location,
    planned_date=date(2025, 7, 24),
    planned_time_window_start=time(6, 0),
    planned_time_window_end=time(17, 0),
)

shipment = TmsShipment(
    id="976eb041-b766-4286-a378-0938c65e7050",
    external_reference=None,
    mode=ModeType.LTL,
    equipment_type=EquipmentType.MOVING_VAN,
    loading_meters=14.8,
    customer=customer,
    line_items=line_items,
    stops=[pickup_stop, delivery_stop],
    timeline_events=None,
)
