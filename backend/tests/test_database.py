"""Direct checks for the five-table SQLite contract."""

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from app.database import DEMO_PROFILE_ID, Repository, SCHEMA_VERSION


def test_schema_has_exact_five_tables_and_constraints(tmp_path: Path) -> None:
    path = tmp_path / "schema.sqlite3"
    repository = Repository(path)
    assert not path.exists()

    repository.initialize()

    with repository.connect(read_only=True) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
            )
        }
        assert tables == {
            "demo_profiles",
            "preferences",
            "exercise_sessions",
            "conversations",
            "messages",
        }
        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION

    with repository.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE preferences SET motion_mode = ? WHERE profile_id = ?",
                ("inferred", DEMO_PROFILE_ID),
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO demo_profiles (
                    profile_id, display_label, jurisdiction_scope,
                    reset_version, created_at, updated_at
                ) VALUES (?, ?, 'US-DEMO', 0, ?, ?)
                """,
                (
                    "another-profile",
                    "Not approved",
                    "2026-10-27T16:00:00.000Z",
                    "2026-10-27T16:00:00.000Z",
                ),
            )


def test_foreign_keys_are_enabled_on_every_connection(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "foreign-keys.sqlite3")
    repository.initialize()
    with repository.connect() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO conversations (
                    conversation_id, profile_id, client_conversation_id,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, 'open', ?, ?)
                """,
                (
                    str(uuid4()),
                    "not-the-fictional-profile",
                    str(uuid4()),
                    "2026-10-27T16:00:00.000Z",
                    "2026-10-27T16:00:00.000Z",
                ),
            )


def test_initialize_is_idempotent_and_records_survive_reopen(tmp_path: Path) -> None:
    path = tmp_path / "restart.sqlite3"
    first = Repository(path)
    first.initialize()
    first.update_preferences(
        motion_mode="none",
        guidance_level="minimal",
        expected_version=1,
        idempotency_key=str(uuid4()),
    )

    reopened = Repository(path)
    reopened.initialize()

    assert reopened.preferences()["motion_mode"] == "none"
    assert reopened.preferences()["guidance_level"] == "minimal"
    assert reopened.preferences()["version"] == 2
