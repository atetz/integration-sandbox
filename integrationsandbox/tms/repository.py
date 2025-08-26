import logging
from datetime import datetime
from typing import Any, List, Optional, Tuple

from integrationsandbox.infrastructure.database import create_connection
from integrationsandbox.infrastructure.exceptions import handle_db_errors
from integrationsandbox.tms.models import TmsShipment, TmsShipmentFilters

logger = logging.getLogger(__name__)


# overkill for only 1 filter but keeping the same as other repo.
def build_where_clause(filters: TmsShipmentFilters) -> Tuple[str, List[Any]]:
    conditions = []
    params = []
    for field, value in filters.model_dump(exclude_none=True).items():
        if field in ["limit", "skip"]:
            continue
        operator = "="
        col = field
        if field == "external_reference":
            col = "json_extract(data, '$.external_reference')"
        if field == "new":
            if value:
                conditions.append("processed_at is null")
            continue
        conditions.append(f"{col} {operator} ?")
        params.append(value)

    clause = ""
    if conditions:
        clause = " WHERE " + " AND ".join(conditions)
    clause += " ORDER BY row_id"
    if filters.limit:
        params.append(filters.limit)
        clause += " LIMIT ?"
    if filters.skip:
        params.append(filters.skip)
        clause += " OFFSET ?"
    return clause, params


@handle_db_errors
def create_many(shipments: List[TmsShipment]) -> None:
    logger.info("Inserting %d TMS shipments into database", len(shipments))
    with create_connection() as con:
        con.executemany(
            "INSERT INTO tms_shipment(id, data) VALUES(?, ?)",
            [(shipment.id, shipment.model_dump_json()) for shipment in shipments],
        )
    logger.info("Successfully inserted %d shipments", len(shipments))


@handle_db_errors
def create(shipment: TmsShipment) -> None:
    logger.info("Inserting TMS shipment into database: %s", shipment.id)
    with create_connection() as con:
        con.execute(
            "INSERT INTO tms_shipment(id, data) VALUES(?, ?)",
            (shipment.id, shipment.model_dump_json()),
        )
    logger.info("Successfully inserted shipment: %s", shipment.id)


@handle_db_errors
def update(shipment: TmsShipment) -> None:
    logger.info("Updating TMS shipment in database: %s", shipment.id)
    with create_connection() as con:
        con.execute(
            "UPDATE tms_shipment set data = ? where id = ?",
            (shipment.model_dump_json(), shipment.id),
        )
    logger.info("Successfully updated shipment: %s", shipment.id)


@handle_db_errors
def get_by_id(id: str) -> Optional[TmsShipment]:
    logger.info("Querying TMS shipment by ID: %s", id)
    params = (id,)
    with create_connection() as con:
        res = con.execute("SELECT data from tms_shipment where id = ?", params)
        row = res.fetchone()
        if row:
            logger.info("Retrieved shipment from database: %s", id)
            return TmsShipment.model_validate_json(row[0])
        logger.info("No shipment found with ID: %s", id)
        return None


@handle_db_errors
def get_by_id_list(
    shipment_ids: List[str],
) -> Tuple[List[TmsShipment], List[str]]:
    logger.info("Querying %d TMS shipments by ID list", len(shipment_ids))
    logger.debug("Shipment IDs: %s", shipment_ids)
    placeholders = ",".join("?" * len(shipment_ids))
    # use IN clause to prevent n+1 query
    query = f"SELECT id, data FROM tms_shipment WHERE id IN ({placeholders})"

    with create_connection() as con:
        res = con.execute(query, shipment_ids)
        rows = res.fetchall()

        shipment_data = {row[0]: row[1] for row in rows}
        shipments = []
        not_found = []
        for shipment_id in shipment_ids:
            if not shipment_data.get(shipment_id, False):
                not_found.append(shipment_id)
                continue
            shipments.append(
                TmsShipment.model_validate_json(shipment_data[shipment_id])
            )

        logger.info(
            "Retrieved %d shipments, %d not found", len(shipments), len(not_found)
        )
        if not_found:
            logger.debug("Not found IDs: %s", not_found)
        return shipments, not_found


@handle_db_errors
def get_all(filters: TmsShipmentFilters) -> List[TmsShipment] | None:
    base_query = "SELECT data from tms_shipment"
    where_clause, params = build_where_clause(filters)
    query = base_query + where_clause
    logger.info("Querying TMS shipments from database")
    logger.debug("Query: %s with params: %s", query, params)

    with create_connection() as con:
        res = con.execute(query, params)
        rows = res.fetchall()
        if rows:
            shipments = [TmsShipment.model_validate_json(row[0]) for row in rows]
            logger.info("Retrieved %d shipments from database", len(shipments))
            return shipments

        logger.info("No shipments found matching filters")
        return None


@handle_db_errors
def mark_as_processed(shipment_id: str) -> bool:
    processed_at = datetime.now().isoformat()

    logger.info("Marking shipment as processed: %s", shipment_id)

    with create_connection() as con:
        cursor = con.execute(
            "UPDATE tms_shipment SET processed_at = ? WHERE id = ?",
            (processed_at, shipment_id),
        )

        if cursor.rowcount > 0:
            logger.info("Successfully marked shipment as processed: %s", shipment_id)
            return True
        else:
            logger.warning("No shipment found with id: %s", shipment_id)
            return False
