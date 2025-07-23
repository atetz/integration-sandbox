from typing import List, Optional

from integrationsandbox.infrastructure.database import create_connection
from integrationsandbox.tms.models import TmsShipment


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
