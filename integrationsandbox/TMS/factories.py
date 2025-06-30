import random
from enum import Enum

from faker import Faker

from integrationsandbox.TMS.models import PackageType, TmsCustomer, TmsLineItem


def get_random_enum_choice(enum_attribute: Enum) -> Enum:
    return random.choice(list(enum_attribute))


class TmsShipmentFactory:
    def __init__(self):
        self.fake = Faker()

    def create_customer(self) -> TmsCustomer:
        fake = self.fake
        return TmsCustomer(
            id=fake.uuid4(),
            name=fake.company(),
            carrier=f"{fake.company()} Transport",
        )

    def create_line_item(self) -> TmsLineItem:
        fake = self.fake
        return TmsLineItem(
            id=fake.uuid4(),
            name=fake.company(),
            carrier=f"{fake.company()} Transport",
        )


def main() -> None:
    shipment_factory = TmsShipmentFactory()
    customer = shipment_factory.create_customer()

    print(get_random_enum_choice(PackageType))


if __name__ == "__main__":
    main()
