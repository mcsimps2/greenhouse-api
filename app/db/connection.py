import sqlite3
from enum import Enum
from threading import local

from flask import current_app

from .schemas import schemas

DEFAULT_TIMEOUT = 30

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))


class CustomConnection(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        self.immediate = kwargs.pop("immediate", False)
        super().__init__(*args, **kwargs)

    def close(self) -> None:
        super().close()

    def commit(self) -> None:
        return super().commit()

    def __del__(self):
        # TODO: this isn't being called for processes, would be nice to catch SIGINT/SIGTERM/atexit
        self.close()


class BeginStatement(str, Enum):
    DEFERRED = "DEFERRED"
    IMMEDIATE = "IMMEDIATE"
    EXCLUSIVE = "EXCLUSIVE"


class TransactionManager:
    __slots__ = ("_connection", "_cursor", "_close_cursor", "_commit", "begin")

    def __init__(self, connection: CustomConnection = None, cursor: sqlite3.Cursor = None, begin: BeginStatement = None):
        self._connection = connection
        self._cursor = cursor
        self._close_cursor = (cursor is None)
        self._commit = False
        self.begin = begin

    @property
    def connection(self):
        if self._connection is None:
            self._connection = current_local.connection
        return self._connection

    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    def __enter__(self):
        cursor = self.cursor
        # Don't commit if someone else is already managing the transaction
        self._commit = not cursor.connection.in_transaction
        if not cursor.connection.in_transaction:
            if self.begin:
                # No prepared statement support here
                cursor.execute(f"BEGIN {self.begin}")
            else:
                cursor.execute("BEGIN")
        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._close_cursor:
            self._cursor.close()
        if self._commit:
            return self._cursor.connection.__exit__(exc_type, exc_val, exc_tb)


def connect(db_path=None, **kwargs):
    db_path = db_path if db_path is not None else current_app.config["DATABASE_FILE"]
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    kwargs.setdefault("detect_types", sqlite3.PARSE_DECLTYPES)
    kwargs.setdefault("check_same_thread", False)  # Disable for our __del__ implementation
    kwargs.setdefault("isolation_level", None)
    conn = sqlite3.connect(
        db_path,
        **kwargs,
        factory=CustomConnection
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    conn.execute("PRAGMA journal_mode = WAL")  # For concurrency
    # No prepared statement support here
    conn.execute(f"PRAGMA busy_timeout = {DEFAULT_TIMEOUT * 1000}")
    return conn


class LocalConnection(local):
    """
    Stores a SQLite connection for a given thread.
    The great part about this is that, when the thread ends and is garbage collected, so is the
    connection, which means it is automatically closed (uses weakref.ref under the hood).
    This should only be referenced by one thread, thereby avoiding race conditions.
    """
    def __init__(self):
        self._connection = None
        super().__init__()

    @property
    def connection(self):
        if self._connection is None:
            self._connection = connect()
        return self._connection

    def close(self):
        if self._connection is not None:
            self._connection.close()


current_local = LocalConnection()


def initialize_tables(connection: sqlite3.Connection):
    with connection:
        for schema in schemas:
            connection.executescript(schema)