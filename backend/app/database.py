"""Version-2 SQLite persistence for one fixed fictional FocusBloom profile."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Literal
from uuid import uuid4

from .config import GEMINI_MODEL


SCHEMA_VERSION = 2
BUSY_TIMEOUT_MS = 5_000
DEMO_PROFILE_ID = "focusbloom-fictional-demo"
DEMO_LABEL = "Fictional FocusBloom coursework profile"
DEFAULT_MOTION = "standard"
DEFAULT_GUIDANCE = "standard"
DEFAULT_DIFFICULTY = "standard"
DatabaseStatus = Literal["available", "not initialized", "incompatible"]

ACTIVITY_TYPES = (
    "different_leaf", "ripple_path", "flower_match", "flower_change",
    "petal_sequence", "clue_search", "garden_path", "perspective_studio",
)
EVENT_TYPES = (
    "started", "shown", "attempted", "completed", "stopped", "skipped",
    "interrupted", "perspective_step", "alternative_reviewed",
)


DDL = (
    """
    CREATE TABLE demo_profiles (
        profile_id TEXT PRIMARY KEY CHECK(profile_id = 'focusbloom-fictional-demo'),
        display_label TEXT NOT NULL,
        schema_version INTEGER NOT NULL CHECK(schema_version = 2),
        reset_version INTEGER NOT NULL DEFAULT 0 CHECK(reset_version >= 0),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE preferences (
        profile_id TEXT PRIMARY KEY REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        motion_mode TEXT NOT NULL CHECK(motion_mode IN ('standard','no_motion')),
        guidance_level TEXT NOT NULL CHECK(guidance_level IN ('minimal','standard','more')),
        difficulty TEXT NOT NULL CHECK(difficulty IN ('easy','standard','challenge')),
        remember_preferences INTEGER NOT NULL CHECK(remember_preferences IN (0,1)),
        version INTEGER NOT NULL CHECK(version >= 1),
        last_idempotency_key TEXT UNIQUE,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE activity_sessions (
        session_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        client_session_id TEXT NOT NULL UNIQUE,
        activity_type TEXT NOT NULL CHECK(activity_type IN (
            'different_leaf','ripple_path','flower_match','flower_change',
            'petal_sequence','clue_search','garden_path','perspective_studio'
        )),
        status TEXT NOT NULL CHECK(status IN ('active','completed','stopped','skipped','interrupted')),
        started_at TEXT NOT NULL,
        ended_at TEXT,
        duration_ms INTEGER NOT NULL DEFAULT 0 CHECK(duration_ms >= 0),
        difficulty TEXT NOT NULL CHECK(difficulty IN ('easy','standard','challenge')),
        motion_mode TEXT NOT NULL CHECK(motion_mode IN ('standard','no_motion')),
        guidance_level TEXT NOT NULL CHECK(guidance_level IN ('minimal','standard','more')),
        perspective_progress TEXT NOT NULL DEFAULT 'none' CHECK(perspective_progress IN (
            'none','interpretation','evidence','alternative','reviewed'
        )),
        alternative_save_state TEXT NOT NULL DEFAULT 'none' CHECK(alternative_save_state IN ('none','saved','deleted')),
        seed_save_state TEXT NOT NULL DEFAULT 'none' CHECK(seed_save_state IN ('none','saved','deleted')),
        model_status TEXT NOT NULL DEFAULT 'skipped' CHECK(model_status IN (
            'skipped','loading','succeeded','failed','no_match','query_rejected'
        )),
        version INTEGER NOT NULL DEFAULT 1 CHECK(version >= 1),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        CHECK((status = 'active' AND ended_at IS NULL) OR (status != 'active' AND ended_at IS NOT NULL)),
        CHECK(status != 'skipped' OR duration_ms = 0)
    )
    """,
    """
    CREATE TABLE activity_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL REFERENCES activity_sessions(session_id) ON DELETE CASCADE,
        client_event_id TEXT NOT NULL UNIQUE,
        ordinal INTEGER NOT NULL CHECK(ordinal >= 0),
        event_type TEXT NOT NULL CHECK(event_type IN (
            'started','shown','attempted','completed','stopped','skipped',
            'interrupted','perspective_step','alternative_reviewed'
        )),
        happened_at TEXT NOT NULL,
        elapsed_ms INTEGER NOT NULL CHECK(elapsed_ms >= 0),
        payload_json TEXT NOT NULL DEFAULT '{}' CHECK(length(payload_json) <= 2048),
        created_at TEXT NOT NULL,
        UNIQUE(session_id, ordinal)
    )
    """,
    """
    CREATE TABLE perspective_artifacts (
        artifact_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        session_id TEXT REFERENCES activity_sessions(session_id) ON DELETE SET NULL,
        client_artifact_id TEXT NOT NULL UNIQUE,
        interpretation_text TEXT NOT NULL CHECK(length(interpretation_text) BETWEEN 1 AND 280),
        supporting_evidence_json TEXT NOT NULL CHECK(length(supporting_evidence_json) <= 2048),
        uncertainty_json TEXT NOT NULL CHECK(length(uncertainty_json) <= 2048),
        alternative_text TEXT NOT NULL CHECK(length(alternative_text) BETWEEN 1 AND 240),
        alternative_source TEXT NOT NULL CHECK(alternative_source IN ('user','gemini','fictional_example')),
        observer_mode TEXT NOT NULL CHECK(observer_mode IN ('none','fictional_alex')),
        saved_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE next_step_seeds (
        seed_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        session_id TEXT REFERENCES activity_sessions(session_id) ON DELETE SET NULL,
        client_seed_id TEXT NOT NULL UNIQUE,
        situation_text TEXT NOT NULL CHECK(length(situation_text) BETWEEN 1 AND 180),
        action_text TEXT NOT NULL CHECK(length(action_text) BETWEEN 1 AND 180),
        formatted_plan TEXT NOT NULL CHECK(length(formatted_plan) <= 400),
        source TEXT NOT NULL CHECK(source IN ('user','template','gemini_format')),
        saved_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE conversations (
        conversation_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        client_conversation_id TEXT NOT NULL UNIQUE,
        purpose TEXT NOT NULL CHECK(purpose IN ('history_guide')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE messages (
        message_id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
        ordinal INTEGER NOT NULL CHECK(ordinal >= 0),
        role TEXT NOT NULL CHECK(role IN ('user','assistant')),
        content TEXT NOT NULL CHECK(length(content) BETWEEN 1 AND 600),
        created_at TEXT NOT NULL,
        UNIQUE(conversation_id, ordinal)
    )
    """,
    """
    CREATE TABLE model_requests (
        request_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        conversation_id TEXT REFERENCES conversations(conversation_id) ON DELETE CASCADE,
        initiating_message_id TEXT REFERENCES messages(message_id) ON DELETE CASCADE,
        response_message_id TEXT REFERENCES messages(message_id) ON DELETE SET NULL,
        idempotency_key TEXT NOT NULL UNIQUE,
        purpose TEXT NOT NULL CHECK(purpose IN (
            'perspective_alternatives','history_sql','history_answer','seed_format'
        )),
        status TEXT NOT NULL CHECK(status IN (
            'accepted','succeeded','failed','no_match','query_rejected','cancelled'
        )),
        safe_error_code TEXT,
        input_hash TEXT NOT NULL,
        model_name TEXT NOT NULL CHECK(model_name = 'gemini-3.5-flash-lite'),
        attempt_count INTEGER NOT NULL CHECK(attempt_count IN (0,1)),
        retrieved_row_refs_json TEXT CHECK(length(retrieved_row_refs_json) <= 4096),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX idx_sessions_profile_started ON activity_sessions(profile_id, started_at DESC, session_id DESC)",
    "CREATE INDEX idx_events_session_ordinal ON activity_events(session_id, ordinal)",
    "CREATE INDEX idx_artifacts_profile_saved ON perspective_artifacts(profile_id, saved_at DESC, artifact_id DESC)",
    "CREATE INDEX idx_seeds_profile_saved ON next_step_seeds(profile_id, saved_at DESC, seed_id DESC)",
    "CREATE INDEX idx_messages_conversation_ordinal ON messages(conversation_id, ordinal)",
    "CREATE INDEX idx_requests_idempotency ON model_requests(idempotency_key)",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def get_database_status(database_path: Path) -> DatabaseStatus:
    if not database_path.is_file():
        return "not initialized"
    try:
        uri = f"{database_path.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(uri, uri=True, timeout=5) as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version != SCHEMA_VERSION:
                return "incompatible"
            connection.execute("SELECT 1 FROM demo_profiles LIMIT 1").fetchone()
        return "available"
    except (OSError, sqlite3.Error):
        return "not initialized"


class Repository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    @contextmanager
    def connect(self, *, read_only: bool = False) -> Iterator[sqlite3.Connection]:
        if read_only:
            uri = f"{self.database_path.resolve().as_uri()}?mode=ro"
            connection = sqlite3.connect(uri, uri=True, timeout=5)
        else:
            connection = sqlite3.connect(self.database_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise
            else:
                connection.commit()

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.database_path.exists()
        with self.transaction() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
            if version == 1 or (version not in (0, SCHEMA_VERSION)):
                raise sqlite3.DatabaseError("unsupported schema version")
            if version == 0 and tables:
                raise sqlite3.DatabaseError("unversioned schema requires a developer decision")
            if version == 0:
                for statement in DDL:
                    connection.execute(statement)
                now = utc_now()
                connection.execute(
                    "INSERT INTO demo_profiles VALUES (?, ?, 2, 0, ?, ?)",
                    (DEMO_PROFILE_ID, DEMO_LABEL, now, now),
                )
                connection.execute(
                    """INSERT INTO preferences (
                        profile_id,motion_mode,guidance_level,difficulty,
                        remember_preferences,version,last_idempotency_key,updated_at
                    ) VALUES (?, ?, ?, ?, 0, 1, NULL, ?)""",
                    (DEMO_PROFILE_ID, DEFAULT_MOTION, DEFAULT_GUIDANCE, DEFAULT_DIFFICULTY, now),
                )
                connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            violations = connection.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                raise sqlite3.DatabaseError("foreign key validation failed")
        if not existed and not self.database_path.exists():
            raise sqlite3.DatabaseError("database initialization failed")

    @staticmethod
    def _dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row is not None else None

    def profile(self) -> dict[str, Any]:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM demo_profiles WHERE profile_id=?", (DEMO_PROFILE_ID,)
            ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("fictional profile unavailable")
        return dict(row)

    def preferences(self) -> dict[str, Any]:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM preferences WHERE profile_id=?", (DEMO_PROFILE_ID,)
            ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("preferences unavailable")
        return dict(row)

    def update_preferences(self, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM preferences WHERE profile_id=?", (DEMO_PROFILE_ID,)
            ).fetchone()
            if row["last_idempotency_key"] == values["idempotency_key"]:
                expected = {
                    "motion_mode": values["motion_mode"],
                    "guidance_level": values["guidance_level"],
                    "difficulty": values["difficulty"],
                    "remember_preferences": int(values["remember_preferences"]),
                }
                if any(row[key] != value for key, value in expected.items()):
                    raise ValueError("preference idempotency conflict")
                return dict(row), True
            if row["version"] != values["expected_version"]:
                raise ValueError("stale preference version")
            connection.execute(
                """UPDATE preferences SET motion_mode=?,guidance_level=?,difficulty=?,
                    remember_preferences=?,version=version+1,last_idempotency_key=?,updated_at=?
                    WHERE profile_id=? AND version=?""",
                (
                    values["motion_mode"], values["guidance_level"], values["difficulty"],
                    int(values["remember_preferences"]), values["idempotency_key"], utc_now(),
                    DEMO_PROFILE_ID, values["expected_version"],
                ),
            )
            updated = connection.execute(
                "SELECT * FROM preferences WHERE profile_id=?", (DEMO_PROFILE_ID,)
            ).fetchone()
            return dict(updated), False

    def create_session(self, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM activity_sessions WHERE client_session_id=?",
                (values["client_session_id"],),
            ).fetchone()
            if existing is not None:
                comparable = ("activity_type", "started_at", "difficulty", "motion_mode", "guidance_level")
                if any(existing[key] != values[key] for key in comparable):
                    raise ValueError("client session id conflict")
                return dict(existing), True
            now = utc_now()
            session_id = str(uuid4())
            connection.execute(
                """INSERT INTO activity_sessions (
                    session_id,profile_id,client_session_id,activity_type,status,started_at,
                    difficulty,motion_mode,guidance_level,created_at,updated_at
                ) VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?)""",
                (
                    session_id, DEMO_PROFILE_ID, values["client_session_id"],
                    values["activity_type"], values["started_at"], values["difficulty"],
                    values["motion_mode"], values["guidance_level"], now, now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM activity_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            return dict(row), False

    def session(self, session_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM activity_sessions WHERE session_id=? AND profile_id=?",
                (session_id, DEMO_PROFILE_ID),
            ).fetchone()
        return self._dict(row)

    def update_session(self, session_id: str, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        terminal = {"complete": "completed", "stop": "stopped", "skip": "skipped", "interrupt": "interrupted"}
        target = terminal[values["action"]]
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM activity_sessions WHERE session_id=? AND profile_id=?",
                (session_id, DEMO_PROFILE_ID),
            ).fetchone()
            if row is None:
                raise LookupError("session not found")
            if row["status"] != "active":
                duplicate_fields = {
                    "status": target, "ended_at": values["ended_at"],
                    "duration_ms": values["duration_ms"],
                    "perspective_progress": values["perspective_progress"],
                    "model_status": values["model_status"],
                }
                if all(row[key] == value for key, value in duplicate_fields.items()):
                    return dict(row), True
                raise ValueError("terminal session cannot transition")
            if row["version"] != values["expected_version"]:
                raise ValueError("stale session version")
            connection.execute(
                """UPDATE activity_sessions SET status=?,ended_at=?,duration_ms=?,
                    perspective_progress=?,model_status=?,version=version+1,updated_at=?
                    WHERE session_id=? AND profile_id=? AND version=?""",
                (
                    target, values["ended_at"], values["duration_ms"],
                    values["perspective_progress"], values["model_status"], utc_now(),
                    session_id, DEMO_PROFILE_ID, values["expected_version"],
                ),
            )
            updated = connection.execute(
                "SELECT * FROM activity_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            return dict(updated), False

    def create_event(self, session_id: str, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            owner = connection.execute(
                "SELECT * FROM activity_sessions WHERE session_id=? AND profile_id=?",
                (session_id, DEMO_PROFILE_ID),
            ).fetchone()
            if owner is None:
                raise LookupError("session not found")
            existing = connection.execute(
                "SELECT * FROM activity_events WHERE client_event_id=?", (values["client_event_id"],)
            ).fetchone()
            payload_json = json.dumps(values["payload"], sort_keys=True, separators=(",", ":"))
            if existing is not None:
                expected = {
                    "session_id": session_id, "ordinal": values["ordinal"],
                    "event_type": values["event_type"], "happened_at": values["happened_at"],
                    "elapsed_ms": values["elapsed_ms"], "payload_json": payload_json,
                }
                if any(existing[key] != value for key, value in expected.items()):
                    raise ValueError("event id conflict")
                return dict(existing), True
            event_id = str(uuid4())
            connection.execute(
                """INSERT INTO activity_events (
                    event_id,session_id,client_event_id,ordinal,event_type,happened_at,
                    elapsed_ms,payload_json,created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event_id, session_id, values["client_event_id"], values["ordinal"],
                    values["event_type"], values["happened_at"], values["elapsed_ms"],
                    payload_json, utc_now(),
                ),
            )
            row = connection.execute(
                "SELECT * FROM activity_events WHERE event_id=?", (event_id,)
            ).fetchone()
            return dict(row), False

    def list_sessions(
        self, cursor: int, limit: int, status: str | None, activity_type: str | None
    ) -> tuple[list[dict[str, Any]], int | None]:
        clauses = ["profile_id=?"]
        params: list[Any] = [DEMO_PROFILE_ID]
        if status:
            clauses.append("status=?")
            params.append(status)
        if activity_type:
            clauses.append("activity_type=?")
            params.append(activity_type)
        params.extend([limit + 1, cursor])
        with self.connect(read_only=True) as connection:
            rows = connection.execute(
                f"""SELECT * FROM activity_sessions WHERE {' AND '.join(clauses)}
                    ORDER BY started_at DESC,session_id DESC LIMIT ? OFFSET ?""",
                params,
            ).fetchall()
        return [dict(row) for row in rows[:limit]], cursor + limit if len(rows) > limit else None

    def session_with_events(self, session_id: str, limit: int = 100) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        row = self.session(session_id)
        if row is None:
            raise LookupError("session not found")
        with self.connect(read_only=True) as connection:
            events = connection.execute(
                "SELECT * FROM activity_events WHERE session_id=? ORDER BY ordinal LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return row, [dict(event) for event in events]

    def create_artifact(self, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM perspective_artifacts WHERE client_artifact_id=?",
                (values["client_artifact_id"],),
            ).fetchone()
            if existing is not None:
                expected = {
                    "session_id": values.get("session_id"),
                    "interpretation_text": values["interpretation_text"],
                    "supporting_evidence_json": json.dumps(values["supporting_evidence"], separators=(",", ":")),
                    "uncertainty_json": json.dumps(values["uncertainty"], separators=(",", ":")),
                    "alternative_text": values["alternative_text"],
                    "alternative_source": values["alternative_source"],
                    "observer_mode": values["observer_mode"],
                }
                if any(existing[key] != value for key, value in expected.items()):
                    raise ValueError("artifact id conflict")
                return dict(existing), True
            self._validate_session_owner(connection, values.get("session_id"))
            artifact_id, now = str(uuid4()), utc_now()
            connection.execute(
                """INSERT INTO perspective_artifacts VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )""",
                (
                    artifact_id, DEMO_PROFILE_ID, values.get("session_id"), values["client_artifact_id"],
                    values["interpretation_text"], json.dumps(values["supporting_evidence"], separators=(",", ":")),
                    json.dumps(values["uncertainty"], separators=(",", ":")), values["alternative_text"],
                    values["alternative_source"], values["observer_mode"], now, now,
                ),
            )
            if values.get("session_id"):
                connection.execute(
                    "UPDATE activity_sessions SET alternative_save_state='saved',updated_at=? WHERE session_id=?",
                    (now, values["session_id"]),
                )
            row = connection.execute(
                "SELECT * FROM perspective_artifacts WHERE artifact_id=?", (artifact_id,)
            ).fetchone()
            return dict(row), False

    def list_artifacts(self, cursor: int, limit: int) -> tuple[list[dict[str, Any]], int | None]:
        return self._bounded_list("perspective_artifacts", "saved_at", cursor, limit)

    def delete_artifact(self, artifact_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM perspective_artifacts WHERE artifact_id=? AND profile_id=?",
                (artifact_id, DEMO_PROFILE_ID),
            ).fetchone()
            if row is None:
                raise LookupError("artifact not found")
            connection.execute("DELETE FROM perspective_artifacts WHERE artifact_id=?", (artifact_id,))
            if row["session_id"]:
                connection.execute(
                    "UPDATE activity_sessions SET alternative_save_state='deleted',updated_at=? WHERE session_id=?",
                    (utc_now(), row["session_id"]),
                )
            return {"artifact_id": artifact_id, "session_id": row["session_id"]}

    def create_seed(self, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM next_step_seeds WHERE client_seed_id=?", (values["client_seed_id"],)
            ).fetchone()
            if existing is not None:
                expected = {
                    "session_id": values.get("session_id"), "situation_text": values["situation_text"],
                    "action_text": values["action_text"], "formatted_plan": values["formatted_plan"],
                    "source": values["source"],
                }
                if any(existing[key] != value for key, value in expected.items()):
                    raise ValueError("seed id conflict")
                return dict(existing), True
            self._validate_session_owner(connection, values.get("session_id"))
            seed_id, now = str(uuid4()), utc_now()
            connection.execute(
                "INSERT INTO next_step_seeds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    seed_id, DEMO_PROFILE_ID, values.get("session_id"), values["client_seed_id"],
                    values["situation_text"], values["action_text"], values["formatted_plan"],
                    values["source"], now, now,
                ),
            )
            if values.get("session_id"):
                connection.execute(
                    "UPDATE activity_sessions SET seed_save_state='saved',updated_at=? WHERE session_id=?",
                    (now, values["session_id"]),
                )
            row = connection.execute("SELECT * FROM next_step_seeds WHERE seed_id=?", (seed_id,)).fetchone()
            return dict(row), False

    def list_seeds(self, cursor: int, limit: int) -> tuple[list[dict[str, Any]], int | None]:
        return self._bounded_list("next_step_seeds", "saved_at", cursor, limit)

    def delete_seed(self, seed_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM next_step_seeds WHERE seed_id=? AND profile_id=?",
                (seed_id, DEMO_PROFILE_ID),
            ).fetchone()
            if row is None:
                raise LookupError("seed not found")
            connection.execute("DELETE FROM next_step_seeds WHERE seed_id=?", (seed_id,))
            if row["session_id"]:
                connection.execute(
                    "UPDATE activity_sessions SET seed_save_state='deleted',updated_at=? WHERE session_id=?",
                    (utc_now(), row["session_id"]),
                )
            return {"seed_id": seed_id, "session_id": row["session_id"]}

    @staticmethod
    def _validate_session_owner(connection: sqlite3.Connection, session_id: str | None) -> None:
        if session_id is None:
            return
        row = connection.execute(
            "SELECT 1 FROM activity_sessions WHERE session_id=? AND profile_id=?",
            (session_id, DEMO_PROFILE_ID),
        ).fetchone()
        if row is None:
            raise LookupError("session not found")

    def _bounded_list(self, table: str, time_column: str, cursor: int, limit: int) -> tuple[list[dict[str, Any]], int | None]:
        if table not in {"perspective_artifacts", "next_step_seeds"}:
            raise ValueError("unapproved table")
        with self.connect(read_only=True) as connection:
            rows = connection.execute(
                f"SELECT * FROM {table} WHERE profile_id=? ORDER BY {time_column} DESC LIMIT ? OFFSET ?",
                (DEMO_PROFILE_ID, limit + 1, cursor),
            ).fetchall()
        return [dict(row) for row in rows[:limit]], cursor + limit if len(rows) > limit else None

    def create_conversation(self, client_id: str) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM conversations WHERE client_conversation_id=?", (client_id,)
            ).fetchone()
            if existing is not None:
                return dict(existing), True
            conversation_id, now = str(uuid4()), utc_now()
            connection.execute(
                "INSERT INTO conversations VALUES (?, ?, ?, 'history_guide', ?, ?)",
                (conversation_id, DEMO_PROFILE_ID, client_id, now, now),
            )
            row = connection.execute(
                "SELECT * FROM conversations WHERE conversation_id=?", (conversation_id,)
            ).fetchone()
            return dict(row), False

    def conversation(self, conversation_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM conversations WHERE conversation_id=? AND profile_id=?",
                (conversation_id, DEMO_PROFILE_ID),
            ).fetchone()
        return self._dict(row)

    def create_history_request(
        self, conversation_id: str, idempotency_key: str, question: str, input_hash: str
    ) -> tuple[dict[str, Any], dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM model_requests WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
            if existing is not None:
                if existing["conversation_id"] != conversation_id or existing["input_hash"] != input_hash:
                    raise ValueError("idempotency key conflict")
                message = connection.execute(
                    "SELECT * FROM messages WHERE message_id=?", (existing["initiating_message_id"],)
                ).fetchone()
                return dict(message), dict(existing), True
            owner = connection.execute(
                "SELECT 1 FROM conversations WHERE conversation_id=? AND profile_id=?",
                (conversation_id, DEMO_PROFILE_ID),
            ).fetchone()
            if owner is None:
                raise LookupError("conversation not found")
            ordinal = connection.execute(
                "SELECT COALESCE(MAX(ordinal),-1)+1 FROM messages WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()[0]
            now, message_id, request_id = utc_now(), str(uuid4()), str(uuid4())
            connection.execute(
                "INSERT INTO messages VALUES (?, ?, ?, 'user', ?, ?)",
                (message_id, conversation_id, ordinal, question, now),
            )
            connection.execute(
                """INSERT INTO model_requests (
                    request_id,profile_id,conversation_id,initiating_message_id,
                    idempotency_key,purpose,status,input_hash,model_name,attempt_count,
                    created_at,updated_at
                ) VALUES (?, ?, ?, ?, ?, 'history_sql', 'accepted', ?, ?, 0, ?, ?)""",
                (
                    request_id, DEMO_PROFILE_ID, conversation_id, message_id,
                    idempotency_key, input_hash, GEMINI_MODEL, now, now,
                ),
            )
            message = connection.execute("SELECT * FROM messages WHERE message_id=?", (message_id,)).fetchone()
            request = connection.execute("SELECT * FROM model_requests WHERE request_id=?", (request_id,)).fetchone()
            return dict(message), dict(request), False

    def model_request(self, request_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM model_requests WHERE request_id=? AND profile_id=?",
                (request_id, DEMO_PROFILE_ID),
            ).fetchone()
        return self._dict(row)

    def message(self, message_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute("SELECT * FROM messages WHERE message_id=?", (message_id,)).fetchone()
        return self._dict(row)

    def create_model_request(
        self, *, idempotency_key: str, purpose: str, input_hash: str,
        conversation_id: str | None = None, initiating_message_id: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM model_requests WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
            if existing is not None:
                expected = {
                    "purpose": purpose, "input_hash": input_hash,
                    "conversation_id": conversation_id,
                    "initiating_message_id": initiating_message_id,
                }
                if any(existing[key] != value for key, value in expected.items()):
                    raise ValueError("model request idempotency conflict")
                return dict(existing), True
            request_id, now = str(uuid4()), utc_now()
            connection.execute(
                """INSERT INTO model_requests (
                    request_id,profile_id,conversation_id,initiating_message_id,idempotency_key,
                    purpose,status,input_hash,model_name,attempt_count,created_at,updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'accepted', ?, ?, 0, ?, ?)""",
                (
                    request_id, DEMO_PROFILE_ID, conversation_id, initiating_message_id,
                    idempotency_key, purpose, input_hash, GEMINI_MODEL, now, now,
                ),
            )
            row = connection.execute("SELECT * FROM model_requests WHERE request_id=?", (request_id,)).fetchone()
            return dict(row), False

    def update_model_request(
        self, request_id: str, *, status: str, safe_error_code: str | None = None,
        attempt_count: int | None = None, row_refs: list[int] | None = None,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            current = connection.execute(
                "SELECT * FROM model_requests WHERE request_id=?", (request_id,)
            ).fetchone()
            if current is None:
                raise LookupError("request not found")
            connection.execute(
                """UPDATE model_requests SET status=?,safe_error_code=?,attempt_count=?,
                    retrieved_row_refs_json=?,updated_at=? WHERE request_id=?""",
                (
                    status, safe_error_code,
                    current["attempt_count"] if attempt_count is None else attempt_count,
                    current["retrieved_row_refs_json"] if row_refs is None else json.dumps(row_refs),
                    utc_now(), request_id,
                ),
            )
            row = connection.execute("SELECT * FROM model_requests WHERE request_id=?", (request_id,)).fetchone()
            return dict(row)

    def complete_history_answer(
        self, *, sql_request_id: str, answer_request_id: str, answer: str, row_refs: list[int]
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            sql_request = connection.execute(
                "SELECT * FROM model_requests WHERE request_id=?", (sql_request_id,)
            ).fetchone()
            answer_request = connection.execute(
                "SELECT * FROM model_requests WHERE request_id=?", (answer_request_id,)
            ).fetchone()
            if sql_request is None or answer_request is None or answer_request["status"] != "accepted":
                raise ValueError("request is not completable")
            ordinal = connection.execute(
                "SELECT COALESCE(MAX(ordinal),-1)+1 FROM messages WHERE conversation_id=?",
                (sql_request["conversation_id"],),
            ).fetchone()[0]
            message_id, now = str(uuid4()), utc_now()
            connection.execute(
                "INSERT INTO messages VALUES (?, ?, ?, 'assistant', ?, ?)",
                (message_id, sql_request["conversation_id"], ordinal, answer, now),
            )
            refs = json.dumps(row_refs)
            connection.execute(
                """UPDATE model_requests SET status='succeeded',attempt_count=1,
                    retrieved_row_refs_json=?,updated_at=? WHERE request_id=?""",
                (refs, now, sql_request_id),
            )
            connection.execute(
                """UPDATE model_requests SET status='succeeded',attempt_count=1,
                    response_message_id=?,retrieved_row_refs_json=?,updated_at=? WHERE request_id=?""",
                (message_id, refs, now, answer_request_id),
            )
            row = connection.execute("SELECT * FROM messages WHERE message_id=?", (message_id,)).fetchone()
            return dict(row)

    def list_messages(self, conversation_id: str, cursor: int, limit: int) -> tuple[list[dict[str, Any]], int | None]:
        if self.conversation(conversation_id) is None:
            raise LookupError("conversation not found")
        with self.connect(read_only=True) as connection:
            rows = connection.execute(
                """SELECT * FROM messages WHERE conversation_id=? AND ordinal>=?
                    ORDER BY ordinal LIMIT ?""",
                (conversation_id, cursor, limit + 1),
            ).fetchall()
        items = [dict(row) for row in rows[:limit]]
        return items, items[-1]["ordinal"] + 1 if len(rows) > limit and items else None

    def delete_saved_text(self) -> dict[str, int]:
        with self.transaction() as connection:
            counts = {
                "perspective_artifacts": connection.execute(
                    "SELECT COUNT(*) FROM perspective_artifacts WHERE profile_id=?", (DEMO_PROFILE_ID,)
                ).fetchone()[0],
                "next_step_seeds": connection.execute(
                    "SELECT COUNT(*) FROM next_step_seeds WHERE profile_id=?", (DEMO_PROFILE_ID,)
                ).fetchone()[0],
                "messages": connection.execute(
                    """SELECT COUNT(*) FROM messages WHERE conversation_id IN (
                        SELECT conversation_id FROM conversations WHERE profile_id=?
                    )""", (DEMO_PROFILE_ID,)
                ).fetchone()[0],
            }
            connection.execute("DELETE FROM perspective_artifacts WHERE profile_id=?", (DEMO_PROFILE_ID,))
            connection.execute("DELETE FROM next_step_seeds WHERE profile_id=?", (DEMO_PROFILE_ID,))
            connection.execute("DELETE FROM conversations WHERE profile_id=?", (DEMO_PROFILE_ID,))
            now = utc_now()
            connection.execute(
                """UPDATE activity_sessions SET
                    alternative_save_state=CASE WHEN alternative_save_state='saved' THEN 'deleted' ELSE alternative_save_state END,
                    seed_save_state=CASE WHEN seed_save_state='saved' THEN 'deleted' ELSE seed_save_state END,
                    updated_at=? WHERE profile_id=?""",
                (now, DEMO_PROFILE_ID),
            )
            return counts

    def reset_demo(self, expected_version: int) -> tuple[int, dict[str, int], bool]:
        with self.transaction() as connection:
            profile = connection.execute(
                "SELECT * FROM demo_profiles WHERE profile_id=?", (DEMO_PROFILE_ID,)
            ).fetchone()
            if profile["reset_version"] == expected_version + 1:
                return profile["reset_version"], {}, True
            if profile["reset_version"] != expected_version:
                raise ValueError("stale reset version")
            counts = {
                table: connection.execute(
                    f"SELECT COUNT(*) FROM {table}"  # table names are a fixed internal tuple
                ).fetchone()[0]
                for table in (
                    "activity_sessions", "activity_events", "perspective_artifacts",
                    "next_step_seeds", "conversations", "messages", "model_requests",
                )
            }
            connection.execute("DELETE FROM demo_profiles WHERE profile_id=?", (DEMO_PROFILE_ID,))
            now, next_version = utc_now(), expected_version + 1
            connection.execute(
                "INSERT INTO demo_profiles VALUES (?, ?, 2, ?, ?, ?)",
                (DEMO_PROFILE_ID, DEMO_LABEL, next_version, now, now),
            )
            connection.execute(
                """INSERT INTO preferences VALUES (
                    ?, ?, ?, ?, 0, 1, NULL, ?
                )""",
                (DEMO_PROFILE_ID, DEFAULT_MOTION, DEFAULT_GUIDANCE, DEFAULT_DIFFICULTY, now),
            )
            return next_version, counts, False
