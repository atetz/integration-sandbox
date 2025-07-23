from typing import Any, Dict, List, Tuple

from integrationsandbox.broker.models import BrokerEventMessage
from integrationsandbox.infrastructure.database import create_connection


def create_events(events: List[BrokerEventMessage]) -> None:
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


def build_where_clause(query_params: dict) -> Tuple[str, list]:
    filters = []
    params = []

    for param, value in query_params.items():
        if "__eq" in param:
            col = param.split("__eq")[0]
            filters.append(f"{col} = ?")
            params.append(value)

    clause = ""
    if filters:
        clause = " WHERE " + " AND ".join(filters)

    return clause, params


def get_events(query_params: Dict[str, Any] | None) -> List[BrokerEventMessage] | None:
    base_query = "SELECT data from broker_event"
    where_clause, params = build_where_clause(query_params)
    query = base_query + where_clause

    with create_connection() as con:
        res = con.execute(query, params)
        rows = res.fetchall()
        if rows:
            return [BrokerEventMessage.model_validate_json(row[0]) for row in rows]

        return None


def get_event(query_params: Dict[str, Any] | None) -> BrokerEventMessage | None:
    base_query = "SELECT data from broker_event"
    where_clause, params = build_where_clause(query_params)
    query = base_query + where_clause + " LIMIT 1"

    with create_connection() as con:
        res = con.execute(query, params)
        row = res.fetchone()
        if row:
            return BrokerEventMessage.model_validate_json(row[0])
        return None
