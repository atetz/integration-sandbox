from typing import Any, List, Optional, Tuple

from integrationsandbox.infrastructure.database import create_connection
from integrationsandbox.tms.models import TmsShipment, TmsShipmentFilters


# overkill for only 1 filter but keeping the same as other repo.
def build_where_clause(filters: TmsShipmentFilters) -> Tuple[str, List[Any]]:
    conditions = []
    params = []

    for field, value in filters.model_dump(exclude_none=True).items():
        col = field
        conditions.append(f"{col} = ?")
        params.append(value)

    clause = ""
    if conditions:
        clause = " WHERE " + " AND ".join(conditions)

    return clause, params


def create_shipments(shipments: List[TmsShipment]) -> None:
    with create_connection() as con:
        con.executemany(
            "INSERT INTO tms_shipment(id, data) VALUES(?, ?)",
            [(shipment.id, shipment.model_dump_json()) for shipment in shipments],
        )


def get_shipment_by_id(id: str) -> Optional[TmsShipment]:
    params = (id,)
    with create_connection() as con:
        res = con.execute("SELECT data from tms_shipment where id = ?", params)
        row = res.fetchone()
        if row:
            return TmsShipment.model_validate_json(row[0])
        return None


def get_shipments_by_id(shipment_ids: List[str]) -> List[TmsShipment]:
    if not shipment_ids:
        return []

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
