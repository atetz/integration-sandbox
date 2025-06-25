from datetime import datetime

from pydantic import BaseModel


class TmsShipmentEvent(BaseModel):
    id: int
    created_at: datetime
    event_type: str
    occured_at: datetime
    source: str
