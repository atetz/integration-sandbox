import random
import uuid
from datetime import datetime, timedelta

from faker import Faker

from integrationsandbox.broker.models import (
    BrokerEventMessage,
    BrokerEventOrder,
    BrokerEventPosition,
    BrokerEventSituation,
    BrokerEventType,
)


def get_random_enum_choice(enum_cls):
    return random.choice(list(enum_cls))


class BrokerEventMessageFactory:
    """Allow methods to take in parameters so that it can be linked to order data."""

    def __init__(self):
        self.fake = Faker()

    def create_org(self, org_name: str = None) -> str:
        return org_name if org_name is not None else self.fake.company()

    def create_order(self, reference: str = None) -> BrokerEventOrder:
        return BrokerEventOrder(
            reference=reference
            if reference is not None
            else self.fake.bothify(text="ORD-#####"),
            eta=self.fake.date_time_between(start_date="now", end_date="+10d"),
        )

    def create_position(self, location_reference: str = None) -> BrokerEventPosition:
        return BrokerEventPosition(
            locationReference=location_reference
            if location_reference
            else self.fake.bothify(text="LOC-####"),
            latitude=self.fake.latitude(),
            longitude=self.fake.longitude(),
        )

    def create_situation(
        self, event_type: BrokerEventType = None, location_reference: str = None
    ) -> BrokerEventSituation:
        now = datetime.now()
        actual = now + timedelta(minutes=random.randint(-60, 60))
        position = True
        if event_type in [BrokerEventType.CANCEL_ORDER, BrokerEventType.ORDER_CREATED]:
            position = False
        return BrokerEventSituation(
            event=event_type
            if event_type is not None
            else get_random_enum_choice(BrokerEventType),
            registrationDate=now,
            actualDate=actual,
            position=self.create_position(location_reference) if position else None,
        )

    def create_event_message(
        self,
        shipment_id: str = None,
        owner_name: str = None,
        reference: str = None,
        event_type: BrokerEventType = None,
        carrier_name: str = None,
        location_reference: str = None,
    ) -> BrokerEventMessage:
        return BrokerEventMessage(
            id=str(uuid.uuid4()),
            shipmentId=shipment_id
            if shipment_id is not None
            else self.fake.bothify(text="SHIP-#####"),
            dateTransmission=self.fake.date_time_between(
                start_date="-1d", end_date="now"
            ),
            owner=self.create_org(owner_name),
            order=self.create_order(reference),
            situation=self.create_situation(event_type, location_reference),
            carrier=self.create_org(carrier_name),
        )
