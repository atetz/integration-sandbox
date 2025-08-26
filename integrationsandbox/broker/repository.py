import logging
from datetime import datetime
from typing import Any, List, Tuple

from integrationsandbox.broker.models import BrokerEventFilters, BrokerEventMessage
from integrationsandbox.infrastructure.database import create_connection
from integrationsandbox.infrastructure.exceptions import handle_db_errors

logger = logging.getLogger(__name__)


@handle_db_errors
def create_many(events: List[BrokerEventMessage]) -> None:
    logger.info("Inserting %d broker events into database", len(events))
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
    logger.info("Successfully inserted %d events", len(events))


@handle_db_errors
def create(event: BrokerEventMessage) -> None:
    logger.info("Inserting broker event into database: %s", event.id)
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
    logger.info("Successfully inserted event: %s", event.id)


def build_where_clause(filters: BrokerEventFilters) -> Tuple[str, List[Any]]:
    conditions = []
    params = []

    for field, value in filters.model_dump(exclude_none=True).items():
        if field in ["limit", "skip"]:
            continue
        if field == "new":
            if value:
                conditions.append("processed_at is null")
            continue
        col = "event_type" if field == "event" else field
        conditions.append(f"{col} = ?")
        params.append(value)

    clause = ""
    if conditions:
        clause = " WHERE " + " AND ".join(conditions)

    clause += " ORDER BY rowid"
    if filters.limit:
        params.append(filters.limit)
        clause += " LIMIT ?"
    if filters.skip:
        params.append(filters.skip)
        clause += " OFFSET ?"

    return clause, params


@handle_db_errors
def get_all(filters: BrokerEventFilters | None) -> List[BrokerEventMessage] | None:
    base_query = "SELECT data from broker_event"
    where_clause, params = build_where_clause(filters)
    query = base_query + where_clause
    logger.info("Querying broker events from database")
    logger.debug("Query: %s with params: %s", query, params)

    with create_connection() as con:
        res = con.execute(query, params)
        rows = res.fetchall()
        if rows:
            events = [BrokerEventMessage.model_validate_json(row[0]) for row in rows]
            logger.info("Retrieved %d events from database", len(events))
            return events

        logger.info("No events found matching filters")
        return None


@handle_db_errors
def get(filters: BrokerEventFilters | None) -> BrokerEventMessage | None:
    base_query = "SELECT data from broker_event"
    filters.limit = 1
    where_clause, params = build_where_clause(filters)
    query = base_query + where_clause
    logger.info("Querying single broker event from database")
    logger.debug("Query: %s with params: %s", query, params)

    with create_connection() as con:
        res = con.execute(query, params)
        row = res.fetchone()
        if row:
            event = BrokerEventMessage.model_validate_json(row[0])
            logger.info("Retrieved event from database: %s", event.id)
            return event
        logger.info("No event found matching filters")
        return None


@handle_db_errors
def mark_as_processed(event_id: str) -> bool:
    processed_at = datetime.now().isoformat()

    logger.info("Marking broker event as processed: %s", event_id)

    with create_connection() as con:
        cursor = con.execute(
            "UPDATE broker_event SET processed_at = ? WHERE id = ?",
            (processed_at, event_id),
        )

        if cursor.rowcount > 0:
            logger.info("Successfully marked event as processed: %s", event_id)
            return True
        else:
            logger.warning("No event found with id: %s", event_id)
            return False
