from sqlite3 import Cursor

from app.models import Sample
from app.db.connection import TransactionManager, BeginStatement
from .exceptions import Invalid
from .greenhouse_service import get_greenhouse_by_serial


_INSERT_SAMPLE = """
INSERT INTO sample(humidity, temperature, humidifier_state, fan_state, lights_state, greenhouse_id) 
VALUES(?, ?, ?, ?, ?, ?);
"""

_SELECT_LATEST_SAMPLE_BY_SERIAL = """
SELECT t1.* 
FROM sample t1 
INNER JOIN greenhouse t2
ON t1.greenhouse_id = t2.id
WHERE t2.serial = ? 
ORDER BY created DESC 
LIMIT 1;
"""


_SELECT_LATEST_SAMPLE_FOR_ALL = """
SELECT t1.*, t2.*
FROM greenhouse t1
LEFT JOIN (
    SELECT st1.*, MAX(created) as max_created
    FROM sample st1
    GROUP BY st1.greenhouse_id
) t2
ON t1.id == t2.greenhouse_id;
"""


def insert_sample(cursor: Cursor, humidity: float, temperature: float, humidifier_state: int, fan_state: int, lights_state: int, serial: str):
    with TransactionManager(begin=BeginStatement.IMMEDIATE):
        greenhouse = get_greenhouse_by_serial(cursor, serial)
        if not greenhouse:
            raise Invalid(f"No such greenhouse with serial {serial} exists.")
        cursor.execute(_INSERT_SAMPLE, (humidity, temperature, humidifier_state, fan_state, lights_state, greenhouse.id))
    return cursor.lastrowid


def select_latest_sample_for_serial(cursor: Cursor, serial: str):
    cursor.execute(_SELECT_LATEST_SAMPLE_BY_SERIAL, (serial,))
    row = cursor.fetchone()
    if not row:
        return None
    return Sample(**row)


def select_latest_sample_for_all(cursor: Cursor):
    cursor.execute(_SELECT_LATEST_SAMPLE_FOR_ALL)
    return cursor.fetchall()
