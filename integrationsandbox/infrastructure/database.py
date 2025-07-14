import sqlite3
from sqlite3 import Connection


def create_connection() -> Connection:
    return sqlite3.connect("integrationsandbox/infrastructure/db.sqlite3")


def setup() -> None:
    with create_connection() as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS tms_orders(id TEXT PRIMARY KEY, data JSON)"
        )
