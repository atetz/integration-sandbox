import logging
import sqlite3

logger = logging.getLogger("integrationsandbox.infrastructure.database")


class RepositoryError(Exception):
    """Base repository exception"""

    pass


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.OperationalError as e:
            logger.error("Database operational error in %s", e)
            msg = f"Database error: {e}. This usually means the table was not found or the database file is not accessible. Restart the app to re-create the database / tables."
            raise RepositoryError(msg) from e
        except sqlite3.Error as e:
            logger.error("Database error in %s", e)
            raise RepositoryError(f"Database error: {e}") from e

    return wrapper
