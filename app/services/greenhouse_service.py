from app.models import Greenhouse
from sqlite3 import Cursor


_INSERT_GREENHOUSE = "INSERT INTO greenhouse(serial) VALUES(?);"
_SELECT_GREENHOUSE_BY_ID = "SELECT * FROM greenhouse WHERE serial = ?;"


def create_greenhouse(cursor: Cursor, serial: str):
    cursor.execute(_INSERT_GREENHOUSE, (serial,))
    return cursor.lastrowid


def get_greenhouse_by_serial(cursor: Cursor, serial: str):
    cursor.execute(_SELECT_GREENHOUSE_BY_ID, (serial,))
    row = cursor.fetchone()
    if not row:
        return None
    return Greenhouse(**row)
