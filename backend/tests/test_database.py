"""Version-2 schema, constraint, transaction, lifecycle, and reopen tests."""

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from app.database import DEMO_PROFILE_ID, Repository, SCHEMA_VERSION


EXPECTED_TABLES = {
    "demo_profiles", "preferences", "activity_sessions", "activity_events",
    "perspective_artifacts", "next_step_seeds", "conversations", "messages",
    "model_requests",
}


def test_schema_has_exact_nine_tables_and_version_two(tmp_path: Path) -> None:
    path = tmp_path / "schema.sqlite3"
    repository = Repository(path)
    assert not path.exists()
    repository.initialize()
    with repository.connect(read_only=True) as connection:
        tables = {
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        assert tables == EXPECTED_TABLES
        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_version_one_database_stops_without_modification(tmp_path: Path) -> None:
    path = tmp_path / "v1.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE exercise_sessions(value TEXT)")
        connection.execute("PRAGMA user_version=1")
    with pytest.raises(sqlite3.DatabaseError):
        Repository(path).initialize()
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='exercise_sessions'").fetchone()


def test_constraints_and_foreign_keys_are_enforced(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "constraints.sqlite3")
    repository.initialize()
    with repository.connect() as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE preferences SET motion_mode='full' WHERE profile_id=?", (DEMO_PROFILE_ID,)
            )
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                "INSERT INTO activity_events VALUES (?, ?, ?, 0, 'started', ?, 0, '{}', ?)",
                (str(uuid4()), "missing", str(uuid4()), "2026-10-28T14:00:00.000Z", "2026-10-28T14:00:00.000Z"),
            )


def test_reopen_preserves_version_two_records(tmp_path: Path) -> None:
    path = tmp_path / "reopen.sqlite3"
    repository = Repository(path)
    repository.initialize()
    repository.update_preferences({
        "motion_mode": "no_motion", "guidance_level": "minimal", "difficulty": "easy",
        "remember_preferences": True, "expected_version": 1, "idempotency_key": str(uuid4()),
    })
    Repository(path).initialize()
    assert Repository(path).preferences()["motion_mode"] == "no_motion"
    assert Repository(path).preferences()["version"] == 2


def test_preferences_are_idempotent_and_versioned(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "prefs.sqlite3")
    repository.initialize()
    key = str(uuid4())
    values = {
        "motion_mode": "no_motion", "guidance_level": "more", "difficulty": "challenge",
        "remember_preferences": True, "expected_version": 1, "idempotency_key": key,
    }
    first, duplicate = repository.update_preferences(values)
    second, repeated = repository.update_preferences(values)
    assert not duplicate and repeated
    assert first["version"] == second["version"] == 2


def test_reset_is_atomic_and_reseeds_defaults(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "reset.sqlite3")
    repository.initialize()
    repository.create_session({
        "client_session_id": str(uuid4()), "activity_type": "different_leaf",
        "started_at": "2026-10-28T14:00:00.000Z", "difficulty": "standard",
        "motion_mode": "standard", "guidance_level": "standard",
    })
    version, counts, duplicate = repository.reset_demo(0)
    assert (version, duplicate) == (1, False)
    assert counts["activity_sessions"] == 1
    assert repository.preferences()["version"] == 1
    assert repository.list_sessions(0, 20, None, None)[0] == []
    assert repository.reset_demo(0)[2] is True
