import os
from datetime import date, time
from typing import List

import pytest

os.environ["DATABASE_PATH"] = "tests/test.db"


from integrationsandbox.broker.models import (
    BrokerHandlingUnit,
    BrokerPackagingQualifier,
)
from integrationsandbox.infrastructure import database
from integrationsandbox.main import app
from integrationsandbox.tms.models import (
    PackageType,
    StopType,
    TmsAddress,
    TmsLineItem,
    TmsLocation,
    TmsStop,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensure database is set up before any tests run."""
    database.setup()
    yield
    # Cleanup: remove test database file
    if os.path.exists("tests/test.db"):
        os.remove("tests/test.db")


@pytest.fixture
def tms_line_items() -> List[TmsLineItem]:
    lines = []
    lines.append(
        TmsLineItem(
            package_type=PackageType.BALE,
            stackable=False,
            height=120.5,
            length=120.5,
            width=120.5,
            length_unit="CM",
            package_weight=120,
            weight_unit="KG",
            description="Wool",
            total_packages=3,
        )
    )
    lines.append(
        TmsLineItem(
            package_type=PackageType.PLT,
            stackable=True,
            height=150.5,
            length=120,
            width=80,
            length_unit="CM",
            package_weight=345,
            weight_unit="KG",
            description="Printer cartridges",
            total_packages=2,
        )
    )
    lines.append(
        TmsLineItem(
            package_type=PackageType.COIL,
            stackable=True,
            height=86,
            length=100,
            width=100,
            length_unit="CM",
            package_weight=256.128,
            weight_unit="KG",
            description="Networking cable",
            total_packages=1,
        )
    )
    return lines


@pytest.fixture
def broker_line_items() -> List[TmsLineItem]:
    lines = []
    for _ in range(3):
        lines.append(
            BrokerHandlingUnit(
                packagingQualifier=BrokerPackagingQualifier.BL,
                height=120.5,
                length=120.5,
                width=120.5,
                grossWeight=120,
            )
        )

    for _ in range(2):
        lines.append(
            BrokerHandlingUnit(
                packagingQualifier=BrokerPackagingQualifier.PL,
                height=150.5,
                length=120,
                width=80,
                grossWeight=345,
            )
        )
    for _ in range(1):
        lines.append(
            BrokerHandlingUnit(
                packagingQualifier=BrokerPackagingQualifier.CL,
                height=86,
                length=100,
                width=100,
                grossWeight=256.128,
            )
        )
    return lines


@pytest.fixture
def tms_stops() -> List[TmsStop]:
    pickup_address = TmsAddress(
        address="123 Pickup St", city="Origin City", postal_code="12345", country="US"
    )
    pickup_location = TmsLocation(
        code="PU001",
        name="Pickup Location",
        address=pickup_address,
        latitude=40.7128,
        longitude=-74.0060,
    )
    pickup_stop = TmsStop(
        type=StopType.PICKUP,
        location=pickup_location,
        planned_date=date(2024, 1, 15),
        planned_time_window_start=time(9, 0),
        planned_time_window_end=time(17, 0),
    )

    delivery_address = TmsAddress(
        address="456 Delivery Ave",
        city="Destination City",
        postal_code="67890",
        country="US",
    )
    delivery_location = TmsLocation(
        code="DEL001",
        name="Delivery Location",
        address=delivery_address,
        latitude=41.8781,
        longitude=-87.6298,
    )
    delivery_stop = TmsStop(
        type=StopType.DELIVERY,
        location=delivery_location,
        planned_date=date(2024, 1, 16),
        planned_time_window_start=time(8, 0),
        planned_time_window_end=time(16, 0),
    )

    return [pickup_stop, delivery_stop]


@pytest.fixture(autouse=True)
def mock_auth():
    """Override authentication dependency for all tests."""
    from integrationsandbox.security.models import User
    from integrationsandbox.security.service import get_current_active_user

    def mock_get_current_active_user():
        return User(username="testuser", disabled=False)

    # Override the dependency in the app
    app.dependency_overrides[get_current_active_user] = mock_get_current_active_user
    yield
    # Clean up
    app.dependency_overrides.clear()
