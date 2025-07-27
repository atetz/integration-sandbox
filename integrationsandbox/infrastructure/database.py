import sqlite3
from sqlite3 import Connection

from integrationsandbox.config import get_settings

settings = get_settings()


def create_connection() -> Connection:
    return sqlite3.connect(settings.database_path)


def setup() -> None:
    with create_connection() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS tms_shipment(
                row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT UNIQUE NOT NULL,
                data JSON)
            """
        )

        con.execute(
            """
            CREATE TABLE IF NOT EXISTS broker_event(
                row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT UNIQUE NOT NULL,
                shipment_id TEXT,
                event_type TEXT,
                data JSON,
                UNIQUE(shipment_id,event_type))
            """
        )
