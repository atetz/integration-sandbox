from integrationsandbox.broker.factories import BrokerEventMessageFactory
from integrationsandbox.broker.models import BrokerEventType


def main():
    print("Hello from integration-sandbox!")

    fact = BrokerEventMessageFactory()

    event_type = BrokerEventType.ORDER_CREATED
    event = fact.create_event_message(
        shipment_id="custom-shipment-id", reference="custom-ref", event_type=event_type
    )

    print(event.model_dump_json())


if __name__ == "__main__":
    main()
