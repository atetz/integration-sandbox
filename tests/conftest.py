from typing import List

import pytest

from integrationsandbox.broker.models import (
    BrokerHandlingUnit,
    BrokerPackagingQualifier,
)
from integrationsandbox.tms.models import PackageType, TmsLineItem


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
