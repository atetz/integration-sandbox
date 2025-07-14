from typing import List, Optional

from integrationsandbox.infrastructure.database import create_connection
from integrationsandbox.tms.models import TmsShipment


def create_orders(orders: List[TmsShipment]) -> None:
    with create_connection() as con:
        con.executemany(
            "INSERT INTO tms_orders(id, data) VALUES(?, ?)",
            [(order.id, order.model_dump_json()) for order in orders],
        )


def get_order_by_id(id: str) -> Optional[TmsShipment]:
    params = (id,)
    with create_connection() as con:
        res = con.execute("SELECT data from tms_orders where id = ?", params)
        row = res.fetchone()
        if row:
            return TmsShipment.model_validate_json(res[0])
        return None
