"""Minimal SQLite lifecycle helpers; no application schema is created yet."""

import sqlite3
from pathlib import Path
from typing import Literal


DatabaseStatus = Literal["available", "not initialized"]


def get_database_status(database_path: Path) -> DatabaseStatus:
    """Check an existing database read-only without creating a file."""

    if not database_path.is_file():
        return "not initialized"

    try:
        uri = f"{database_path.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            connection.execute("SELECT 1").fetchone()
    except (OSError, sqlite3.Error):
        return "not initialized"
    return "available"


def initialize_database(database_path: Path) -> None:
    """Create an empty SQLite database only when explicitly invoked later."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.commit()
