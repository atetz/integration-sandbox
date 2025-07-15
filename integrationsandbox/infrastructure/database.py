import sqlite3
from sqlite3 import Connection


def create_connection() -> Connection:
    return sqlite3.connect("integrationsandbox/infrastructure/db.sqlite3")


def setup() -> None:
    with create_connection() as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS tms_shipment(id TEXT PRIMARY KEY, data JSON)"
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_event(
            id TEXT PRIMARY KEY, 
            shipment_id TEXT, 
            event_type TEXT, 
            data JSON, 
            UNIQUE(shipment_id,event_type))
            """
        )
