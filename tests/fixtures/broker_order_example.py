from datetime import datetime

from integrationsandbox.broker.models import (
    BrokerDate,
    BrokerDateQualifier,
    BrokerHandlingUnit,
    BrokerLocation,
    BrokerOder,
    BrokerOrderMessage,
    BrokerOrderMeta,
    BrokerPackagingQualifier,
    BrokerQuantity,
    BrokerShipment,
)

# Create Meta
meta = BrokerOrderMeta(
    senderId="75831ed4-7d29-44a6-953f-066c2e3cd609",
    messageDate=datetime(2025, 7, 20, 11, 35, 47, 461000),
    messageReference="976eb041-b766-4286-a378-0938c65e7050",
    messageFunction=9,
)

# Create Pickup Location
pickup_dates = [
    BrokerDate(
        qualifier=BrokerDateQualifier.PERIOD_EARLIEST,
        dateTime=datetime(2025, 7, 22, 6, 0),
    ),
    BrokerDate(
        qualifier=BrokerDateQualifier.PERIOD_LATEST,
        dateTime=datetime(2025, 7, 22, 17, 0),
    ),
]

pickup_location = BrokerLocation(
    identification="LOC-9973",
    name="Scamarcio e figli",
    address1="Borgo Buonauro, 27 Piano 6",
    address2="",
    country="IT",
    postalCode="81046",
    city="Riva",
    latitude=9.223782,
    longitude=123.12346,
    instructions="",
    dates=pickup_dates,
)

# Create Delivery Location
delivery_dates = [
    BrokerDate(
        qualifier=BrokerDateQualifier.PERIOD_EARLIEST,
        dateTime=datetime(2025, 7, 24, 6, 0),
    ),
    BrokerDate(
        qualifier=BrokerDateQualifier.PERIOD_LATEST,
        dateTime=datetime(2025, 7, 24, 17, 0),
    ),
]

delivery_location = BrokerLocation(
    identification="LOC-8521",
    name="Williams-Patel",
    address1="Studio 6\nGill courts",
    address2="",
    country="GB",
    postalCode="WA7 6JT",
    city="Leonardtown",
    latitude=13.042235,
    longitude=-168.601537,
    instructions="",
    dates=delivery_dates,
)

# Create Handling Units
handling_units = [
    # BALE units (4x)
    *[
        BrokerHandlingUnit(
            packagingQualifier=BrokerPackagingQualifier.BL,
            grossWeight=7069.62,
            width=20.88,
            length=138.51,
            height=115.15,
        )
        for _ in range(4)
    ],
    # First CYLINDER unit (1x)
    BrokerHandlingUnit(
        packagingQualifier=BrokerPackagingQualifier.CY,
        grossWeight=2336.24,
        width=162.91,
        length=71.51,
        height=31.16,
    ),
    # Second CYLINDER units (3x)
    *[
        BrokerHandlingUnit(
            packagingQualifier=BrokerPackagingQualifier.CY,
            grossWeight=890.43,
            width=95.14,
            length=111.34,
            height=66.97,
        )
        for _ in range(3)
    ],
]

# Create Order
order = BrokerOder(
    reference="976eb041-b766-4286-a378-0938c65e7050",
    pickUp=pickup_location,
    consignee=delivery_location,
    goodsDescription=(
        "Commercial grade floor mats for high-traffic areas|"
        "Heavy-duty truck tires, new and retreaded options|"
        "Industrial conveyor belt sections"
    ),
    quantity=BrokerQuantity(
        grossWeight=33286.01,
        loadingMeters=14.8,
    ),
    handlingUnits=handling_units,
)

# Create Shipment
shipment = BrokerShipment(
    id="976eb041-b766-4286-a378-0938c65e7050",
    reference="976eb041-b766-4286-a378-0938c65e7050",
    carrier="Cole Ltd Transport",
    transportMode="ROAD",
    orders=[order],
)

# Create Complete Message
broker_message = BrokerOrderMessage(
    meta=meta,
    shipment=shipment,
)


print(broker_message.model_dump_json())
