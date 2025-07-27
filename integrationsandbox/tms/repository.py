from typing import Any, List, Optional, Tuple

from integrationsandbox.infrastructure.database import create_connection
from integrationsandbox.infrastructure.exceptions import handle_db_errors
from integrationsandbox.tms.models import TmsShipment, TmsShipmentFilters


# overkill for only 1 filter but keeping the same as other repo.
def build_where_clause(filters: TmsShipmentFilters) -> Tuple[str, List[Any]]:
    conditions = []
    params = []

    for field, value in filters.model_dump(exclude_none=True).items():
        if field == "limit":
            continue
        operator = "="
        col = field
        if field == "start":
            col = "row_id"
            operator = ">="
        conditions.append(f"{col} {operator} ?")
        params.append(value)

    clause = ""
    if conditions:
        clause = " WHERE " + " AND ".join(conditions)

    if filters.limit:
        params.append(filters.limit)
        clause += " LIMIT ?"

    return clause, params


@handle_db_errors
def create_many(shipments: List[TmsShipment]) -> None:
    with create_connection() as con:
        con.executemany(
            "INSERT INTO tms_shipment(id, data) VALUES(?, ?)",
            [(shipment.id, shipment.model_dump_json()) for shipment in shipments],
        )


@handle_db_errors
def create(shipment: TmsShipment) -> None:
    with create_connection() as con:
        con.execute(
            "INSERT INTO tms_shipment(id, data) VALUES(?, ?)",
            (shipment.id, shipment.model_dump_json()),
        )


@handle_db_errors
def get_by_id(id: str) -> Optional[TmsShipment]:
    params = (id,)
    with create_connection() as con:
        res = con.execute("SELECT data from tms_shipment where id = ?", params)
        row = res.fetchone()
        if row:
            return TmsShipment.model_validate_json(row[0])
        return None


@handle_db_errors
def get_by_id_list(shipment_ids: List[str]) -> List[TmsShipment]:
    placeholders = ",".join("?" * len(shipment_ids))
    # use IN clause to prevent n+1 query
    query = f"SELECT id, data FROM tms_shipment WHERE id IN ({placeholders})"

    with create_connection() as con:
        res = con.execute(query, shipment_ids)
        rows = res.fetchall()

        shipment_data = {row[0]: row[1] for row in rows}

        shipments = []
        for shipment_id in shipment_ids:
            if shipment_id not in shipment_data:
                raise ValueError(f'Shipment with id "{shipment_id}" not found')
            shipments.append(
                TmsShipment.model_validate_json(shipment_data[shipment_id])
            )

        return shipments


@handle_db_errors
def get_all(filters: TmsShipmentFilters) -> List[TmsShipment] | None:
    base_query = "SELECT data from tms_shipment"
    where_clause, params = build_where_clause(filters)
    query = base_query + where_clause

    with create_connection() as con:
        res = con.execute(query, params)
        rows = res.fetchall()
        if rows:
            return [TmsShipment.model_validate_json(row[0]) for row in rows]

        return None
