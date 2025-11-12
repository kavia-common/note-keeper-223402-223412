import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional


DB_PATH_ENV = "DB_PATH"
DEFAULT_DB_PATH = "./data/notes.db"


# PUBLIC_INTERFACE
def get_db_path() -> str:
    """Return the configured database path from the DB_PATH environment variable or default."""
    return os.getenv(DB_PATH_ENV, DEFAULT_DB_PATH)


def _ensure_data_dir_exists(db_path: str) -> None:
    """Ensure the directory for the sqlite db exists (e.g., ./data)."""
    directory = os.path.dirname(db_path) or "."
    os.makedirs(directory, exist_ok=True)


# PUBLIC_INTERFACE
@contextmanager
def get_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager that yields a SQLite connection with row factory as dict-like.

    The connection is configured with:
    - row_factory to access columns by name.
    - foreign_keys pragma enabled.

    It will commit on success and rollback on exception, then always close.
    """
    path = db_path or get_db_path()
    _ensure_data_dir_exists(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        # Ensure foreign keys support
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# PUBLIC_INTERFACE
def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the SQLite database and ensure the notes table exists.

    Creates the database file if missing and the 'notes' table with schema:
    - id INTEGER PRIMARY KEY AUTOINCREMENT
    - title TEXT NOT NULL
    - content TEXT NOT NULL
    - created_at TEXT NOT NULL (ISO8601)
    - updated_at TEXT NOT NULL (ISO8601)
    """
    path = db_path or get_db_path()
    _ensure_data_dir_exists(path)
    with get_connection(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )


def iso_now() -> str:
    """Return current UTC time in ISO8601 format."""
    return datetime.utcnow().isoformat() + "Z"
