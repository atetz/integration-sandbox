from typing import Any, List, Tuple

from integrationsandbox.broker.models import BrokerEventFilters, BrokerEventMessage
from integrationsandbox.infrastructure.database import create_connection


def create_many(events: List[BrokerEventMessage]) -> None:
    with create_connection() as con:
        # REPLACE will overwrite existing combinations of shipment_id and status.
        # This makes is easier to validate incoming broker messages that were accidentally triggered multiple times for a status/id combination
        con.executemany(
            "REPLACE INTO broker_event(id, shipment_id, event_type, data) VALUES(?,?,?,?)",
            [
                (
                    event.id,
                    event.shipmentId,
                    event.situation.event,
                    event.model_dump_json(),
                )
                for event in events
            ],
        )


def create(event: BrokerEventMessage) -> None:
    with create_connection() as con:
        # REPLACE will overwrite existing combinations of shipment_id and status.
        # This makes is easier to validate incoming broker messages that were accidentally triggered multiple times for a status/id combination
        con.execute(
            "REPLACE INTO broker_event(id, shipment_id, event_type, data) VALUES(?,?,?,?)",
            (
                event.id,
                event.shipmentId,
                event.situation.event,
                event.model_dump_json(),
            ),
        )


def build_where_clause(filters: BrokerEventFilters) -> Tuple[str, List[Any]]:
    conditions = []
    params = []

    for field, value in filters.model_dump(exclude_none=True).items():
        col = "event_type" if field == "event" else field
        conditions.append(f"{col} = ?")
        params.append(value)

    clause = ""
    if conditions:
        clause = " WHERE " + " AND ".join(conditions)

    return clause, params


def get_all(filters: BrokerEventFilters | None) -> List[BrokerEventMessage] | None:
    base_query = "SELECT data from broker_event"
    where_clause, params = build_where_clause(filters)
    query = base_query + where_clause

    with create_connection() as con:
        res = con.execute(query, params)
        rows = res.fetchall()
        if rows:
            return [BrokerEventMessage.model_validate_json(row[0]) for row in rows]

        return None


def get(filters: BrokerEventFilters | None) -> BrokerEventMessage | None:
    base_query = "SELECT data from broker_event"
    where_clause, params = build_where_clause(filters)
    query = base_query + where_clause + " LIMIT 1"

    with create_connection() as con:
        res = con.execute(query, params)
        row = res.fetchone()
        if row:
            return BrokerEventMessage.model_validate_json(row[0])
        return None
