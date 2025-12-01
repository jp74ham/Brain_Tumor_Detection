"""
Database helper utilities for the MyApp package.
Provides a single authoritative function `get_db_path()` that returns
an absolute path to `brain_etl.db` located in the `MyApp` directory.
"""
from __future__ import annotations
import os


def get_db_path() -> str:
    """Return the absolute path to the app's brain_etl.db file."""
    return os.path.join(os.path.dirname(__file__), 'brain_etl.db')


def connect_db():
    """Convenience: return a sqlite3 connection to the app DB.
    Importing sqlite3 here is intentionally lazy in callers that don't
    need it; callers can import sqlite3 and use `connect_db()`.
    """
    import sqlite3
    return sqlite3.connect(get_db_path())
