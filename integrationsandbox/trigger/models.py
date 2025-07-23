from typing import List

from pydantic import AnyUrl, BaseModel, Field, PositiveInt

from integrationsandbox.broker.models import BrokerEventType


class ShipmentTrigger(BaseModel):
    target_url: AnyUrl = Field(description="URL to send the generated events to")
    count: PositiveInt = Field(
        description="Number of shipments to generate and send to target", le=1000
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "target_url": "https://api.example.com/shipments",
                    "count": 10,
                }
            ]
        }
    }


class EventTrigger(BaseModel):
    target_url: AnyUrl = Field(description="URL to send the generated events to")
    event: BrokerEventType = Field(
        description="Type of event to generate for all shipments"
    )
    shipment_ids: List[str] = Field(
        description="List of shipment IDs to generate events for. Supports multiple shipments for bulk testing.",
        le=1000,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "target_url": "https://api.example.com/events",
                    "event": "ORDER_LOADED",
                    "shipment_ids": [
                        "976eb041-b766-4286-a378-0938c65e7050",
                        "976eb041-b766-4286-a378-0938c65e7051",
                        "976eb041-b766-4286-a378-0938c65e7052",
                    ],
                }
            ]
        }
    }
