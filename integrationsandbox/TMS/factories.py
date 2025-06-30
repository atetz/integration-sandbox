from faker import Faker

from integrationsandbox.TMS.models import TmsCustomer, TmsLineItem


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
    
    def create_line_item(self) -> TmsLineItem


def main() -> None:
    shipment_factory = TmsShipmentFactory()
    print(shipment_factory.create_customer())


if __name__ == "__main__":
    main()
