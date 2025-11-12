import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
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
    """Context manager that yields a SQLite connection configured for convenience and safety.

    Configuration details:
    - Ensures the parent directory for the DB file exists.
    - Sets row_factory to sqlite3.Row so columns can be accessed by name.
    - Enables foreign key constraints with PRAGMA.
    - Commits on success; rolls back on exception; always closes the connection.

    Parameters:
    - db_path: Optional explicit path to the SQLite DB file. Falls back to environment/default.

    Yields:
    - sqlite3.Connection instance ready for executing statements.
    """
    path = db_path or get_db_path()
    _ensure_data_dir_exists(path)
    # check_same_thread=False to allow usage across FastAPI worker threads when needed.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# PUBLIC_INTERFACE
@contextmanager
def transaction(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transaction context identical to get_connection.

    This is a semantic alias to improve readability at call sites where an
    explicit 'transaction' is desired. See get_connection for details.
    """
    with get_connection(db_path) as conn:
        yield conn


def _create_schema(conn: sqlite3.Connection) -> None:
    """Create tables if they do not already exist."""
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


# PUBLIC_INTERFACE
def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the SQLite database and ensure the required tables exist.

    Creates the database file if missing and the 'notes' table with schema:
    - id INTEGER PRIMARY KEY AUTOINCREMENT
    - title TEXT NOT NULL
    - content TEXT NOT NULL
    - created_at TEXT NOT NULL (ISO8601, UTC)
    - updated_at TEXT NOT NULL (ISO8601, UTC)
    """
    path = db_path or get_db_path()
    _ensure_data_dir_exists(path)
    with get_connection(path) as conn:
        _create_schema(conn)


# PUBLIC_INTERFACE
def iso_now() -> str:
    """Return current UTC time in strict ISO8601 format with 'Z' timezone marker."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
