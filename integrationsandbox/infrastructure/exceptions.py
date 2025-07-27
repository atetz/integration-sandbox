import sqlite3


class RepositoryError(Exception):
    """Base repository exception"""

    pass


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.OperationalError as e:
            raise RepositoryError(
                f"Database error: {e}. This usually means the table was not found or the database file is not accessible. Restart the app to re-create the database / tables."
            )
        except sqlite3.Error as e:
            raise RepositoryError(f"Database error: {e}")

    return wrapper
