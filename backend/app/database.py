"""Legacy version-1 SQLite persistence under FocusBloom branding."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Literal
from uuid import NAMESPACE_URL, uuid4, uuid5


SCHEMA_VERSION = 1
BUSY_TIMEOUT_MS = 5_000
DEMO_PROFILE_ID = "breathbloom-fictional-demo"
DEMO_LABEL = "Fictional FocusBloom coursework profile"
DEFAULT_MOTION = "gentle"
DEFAULT_GUIDANCE = "standard"
DatabaseStatus = Literal["available", "not initialized"]


DDL = (
    """
    CREATE TABLE IF NOT EXISTS demo_profiles (
        profile_id TEXT PRIMARY KEY
            CHECK (profile_id = 'breathbloom-fictional-demo'),
        display_label TEXT NOT NULL,
        jurisdiction_scope TEXT NOT NULL CHECK (jurisdiction_scope = 'US-DEMO'),
        reset_version INTEGER NOT NULL DEFAULT 0 CHECK (reset_version >= 0),
        last_reset_key TEXT,
        created_at TEXT NOT NULL CHECK (created_at GLOB '????-??-??T??:??:??.???Z'),
        updated_at TEXT NOT NULL CHECK (updated_at GLOB '????-??-??T??:??:??.???Z')
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS preferences (
        preference_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL UNIQUE
            REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        motion_mode TEXT NOT NULL CHECK (motion_mode IN ('full', 'gentle', 'none')),
        guidance_level TEXT NOT NULL
            CHECK (guidance_level IN ('minimal', 'standard', 'more')),
        source TEXT NOT NULL CHECK (source IN ('explicit', 'default', 'reset')),
        version INTEGER NOT NULL CHECK (version >= 1),
        last_idempotency_key TEXT,
        created_at TEXT NOT NULL CHECK (created_at GLOB '????-??-??T??:??:??.???Z'),
        updated_at TEXT NOT NULL CHECK (updated_at GLOB '????-??-??T??:??:??.???Z')
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_sessions (
        session_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL
            REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        client_session_id TEXT NOT NULL UNIQUE,
        create_idempotency_key TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL
            CHECK (status IN ('active', 'paused', 'completed', 'stopped', 'interrupted')),
        started_at TEXT NOT NULL CHECK (started_at GLOB '????-??-??T??:??:??.???Z'),
        ended_at TEXT CHECK (ended_at IS NULL OR ended_at GLOB '????-??-??T??:??:??.???Z'),
        planned_duration_ms INTEGER NOT NULL DEFAULT 60000
            CHECK (planned_duration_ms = 60000),
        observed_active_duration_ms INTEGER NOT NULL DEFAULT 0
            CHECK (observed_active_duration_ms BETWEEN 0 AND 62000),
        paused_duration_ms INTEGER NOT NULL DEFAULT 0 CHECK (paused_duration_ms >= 0),
        wall_clock_duration_ms INTEGER NOT NULL DEFAULT 0
            CHECK (wall_clock_duration_ms >= observed_active_duration_ms),
        completed_cycles INTEGER NOT NULL DEFAULT 0 CHECK (completed_cycles BETWEEN 0 AND 6),
        ending_phase TEXT CHECK (ending_phase IS NULL OR ending_phase IN ('setup', 'ready', 'inhale', 'exhale')),
        phase_elapsed_ms INTEGER NOT NULL DEFAULT 0 CHECK (phase_elapsed_ms BETWEEN 0 AND 8000),
        motion_mode TEXT NOT NULL CHECK (motion_mode IN ('full', 'gentle', 'none')),
        guidance_level TEXT NOT NULL
            CHECK (guidance_level IN ('minimal', 'standard', 'more')),
        next_time_setup TEXT CHECK (
            next_time_setup IS NULL OR next_time_setup IN (
                'use_this_setup', 'change_motion', 'change_guidance', 'no_preference'
            )
        ),
        persistence_status TEXT NOT NULL
            CHECK (persistence_status IN ('pending', 'saved', 'failed')),
        version INTEGER NOT NULL CHECK (version >= 1),
        last_action_id TEXT,
        created_at TEXT NOT NULL CHECK (created_at GLOB '????-??-??T??:??:??.???Z'),
        updated_at TEXT NOT NULL CHECK (updated_at GLOB '????-??-??T??:??:??.???Z'),
        CHECK (
            (status IN ('active', 'paused') AND ended_at IS NULL)
            OR (status IN ('completed', 'stopped', 'interrupted') AND ended_at IS NOT NULL)
        ),
        CHECK (status != 'completed' OR completed_cycles = 6),
        CHECK (status NOT IN ('stopped', 'interrupted') OR completed_cycles < 6)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS conversations (
        conversation_id TEXT PRIMARY KEY,
        profile_id TEXT NOT NULL
            REFERENCES demo_profiles(profile_id) ON DELETE CASCADE,
        session_id TEXT
            REFERENCES exercise_sessions(session_id) ON DELETE SET NULL,
        client_conversation_id TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
        created_at TEXT NOT NULL CHECK (created_at GLOB '????-??-??T??:??:??.???Z'),
        updated_at TEXT NOT NULL CHECK (updated_at GLOB '????-??-??T??:??:??.???Z')
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL
            REFERENCES conversations(conversation_id) ON DELETE CASCADE,
        client_message_id TEXT NOT NULL,
        ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        content TEXT NOT NULL CHECK (length(trim(content)) BETWEEN 1 AND 2000),
        request_id TEXT UNIQUE,
        request_purpose TEXT CHECK (
            request_purpose IS NULL OR request_purpose IN (
                'introduction', 'factual_reflection', 'history_question'
            )
        ),
        request_status TEXT CHECK (
            request_status IS NULL OR request_status IN (
                'pending', 'succeeded', 'failed', 'stale'
            )
        ),
        safe_error_code TEXT CHECK (
            safe_error_code IS NULL OR safe_error_code IN (
                'missing_configuration', 'authentication_failure',
                'permission_failure', 'quota_failure', 'rate_limit_failure',
                'timeout', 'provider_failure', 'malformed_response',
                'stale_response', 'persistence_failure',
                'database_failure'
            )
        ),
        created_at TEXT NOT NULL CHECK (created_at GLOB '????-??-??T??:??:??.???Z'),
        updated_at TEXT NOT NULL CHECK (updated_at GLOB '????-??-??T??:??:??.???Z'),
        UNIQUE (conversation_id, client_message_id),
        UNIQUE (conversation_id, ordinal),
        CHECK (
            role = 'user'
            OR (
                request_id IS NULL AND request_purpose IS NULL
                AND request_status IS NULL AND safe_error_code IS NULL
            )
        )
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_sessions_profile_started ON exercise_sessions(profile_id, started_at DESC, session_id DESC)",
    "CREATE INDEX IF NOT EXISTS idx_messages_conversation_ordinal ON messages(conversation_id, ordinal)",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def get_database_status(database_path: Path) -> DatabaseStatus:
    """Inspect an existing database read-only without creating or changing it."""

    if not database_path.is_file():
        return "not initialized"
    try:
        uri = f"{database_path.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(uri, uri=True, timeout=5) as connection:
            connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            connection.execute("SELECT 1 FROM demo_profiles LIMIT 1").fetchone()
        return "available" if version == SCHEMA_VERSION else "not initialized"
    except (OSError, sqlite3.Error):
        return "not initialized"


class Repository:
    """Parameterized persistence scoped to one fixed fictional demo profile."""

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
        """Explicitly create or reopen the approved schema and demo defaults."""

        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, SCHEMA_VERSION):
                raise sqlite3.DatabaseError("unsupported schema version")
            for statement in DDL:
                connection.execute(statement)
            now = utc_now()
            connection.execute(
                """
                INSERT OR IGNORE INTO demo_profiles (
                    profile_id, display_label, jurisdiction_scope,
                    reset_version, created_at, updated_at
                ) VALUES (?, ?, 'US-DEMO', 0, ?, ?)
                """,
                (DEMO_PROFILE_ID, DEMO_LABEL, now, now),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO preferences (
                    preference_id, profile_id, motion_mode, guidance_level,
                    source, version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'default', 1, ?, ?)
                """,
                (str(uuid4()), DEMO_PROFILE_ID, DEFAULT_MOTION, DEFAULT_GUIDANCE, now, now),
            )
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    @staticmethod
    def _dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row is not None else None

    def profile(self) -> dict[str, Any]:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM demo_profiles WHERE profile_id = ?", (DEMO_PROFILE_ID,)
            ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("fictional profile unavailable")
        return dict(row)

    def preferences(self) -> dict[str, Any]:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM preferences WHERE profile_id = ?", (DEMO_PROFILE_ID,)
            ).fetchone()
        if row is None:
            raise sqlite3.DatabaseError("preferences unavailable")
        return dict(row)

    def update_preferences(
        self,
        *,
        motion_mode: str,
        guidance_level: str,
        expected_version: int,
        idempotency_key: str,
    ) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM preferences WHERE profile_id = ?", (DEMO_PROFILE_ID,)
            ).fetchone()
            if row is None:
                raise sqlite3.DatabaseError("preferences unavailable")
            if row["last_idempotency_key"] == idempotency_key:
                return dict(row), True
            if row["version"] != expected_version:
                raise ValueError("stale preference version")
            now = utc_now()
            connection.execute(
                """
                UPDATE preferences
                SET motion_mode = ?, guidance_level = ?, source = 'explicit',
                    version = version + 1, last_idempotency_key = ?, updated_at = ?
                WHERE profile_id = ? AND version = ?
                """,
                (
                    motion_mode,
                    guidance_level,
                    idempotency_key,
                    now,
                    DEMO_PROFILE_ID,
                    expected_version,
                ),
            )
            updated = connection.execute(
                "SELECT * FROM preferences WHERE profile_id = ?", (DEMO_PROFILE_ID,)
            ).fetchone()
            return dict(updated), False

    def create_session(self, values: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                """
                SELECT * FROM exercise_sessions
                WHERE profile_id = ? AND (
                    client_session_id = ? OR create_idempotency_key = ?
                )
                """,
                (
                    DEMO_PROFILE_ID,
                    values["client_session_id"],
                    values["create_idempotency_key"],
                ),
            ).fetchone()
            if existing is not None:
                if (
                    existing["client_session_id"] != values["client_session_id"]
                    or existing["create_idempotency_key"] != values["create_idempotency_key"]
                ):
                    raise ValueError("idempotency conflict")
                return dict(existing), True
            connection.execute(
                """
                INSERT INTO exercise_sessions (
                    session_id, profile_id, client_session_id, create_idempotency_key,
                    status, started_at, planned_duration_ms,
                    observed_active_duration_ms, paused_duration_ms,
                    wall_clock_duration_ms, completed_cycles, ending_phase,
                    phase_elapsed_ms, motion_mode, guidance_level,
                    persistence_status, version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'active', ?, 60000, 0, 0, 0, 0,
                          'inhale', 0, ?, ?, 'saved', 1, ?, ?)
                """,
                (
                    values["session_id"],
                    DEMO_PROFILE_ID,
                    values["client_session_id"],
                    values["create_idempotency_key"],
                    values["started_at"],
                    values["motion_mode"],
                    values["guidance_level"],
                    values["created_at"],
                    values["created_at"],
                ),
            )
            row = connection.execute(
                "SELECT * FROM exercise_sessions WHERE session_id = ?",
                (values["session_id"],),
            ).fetchone()
            return dict(row), False

    def session(self, session_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                """
                SELECT * FROM exercise_sessions
                WHERE session_id = ? AND profile_id = ?
                """,
                (session_id, DEMO_PROFILE_ID),
            ).fetchone()
        return self._dict(row)

    def update_session(
        self,
        *,
        session_id: str,
        expected_version: int,
        action_id: str,
        updates: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            row = connection.execute(
                """
                SELECT * FROM exercise_sessions
                WHERE session_id = ? AND profile_id = ?
                """,
                (session_id, DEMO_PROFILE_ID),
            ).fetchone()
            if row is None:
                raise LookupError("session not found")
            if row["last_action_id"] == action_id:
                return dict(row), True
            if row["version"] != expected_version:
                raise ValueError("stale session version")
            assignments = [f"{column} = ?" for column in updates]
            parameters = list(updates.values())
            assignments.extend(["version = version + 1", "last_action_id = ?", "updated_at = ?"])
            parameters.extend([action_id, utc_now(), session_id, DEMO_PROFILE_ID, expected_version])
            cursor = connection.execute(
                f"""
                UPDATE exercise_sessions SET {', '.join(assignments)}
                WHERE session_id = ? AND profile_id = ? AND version = ?
                """,
                parameters,
            )
            if cursor.rowcount != 1:
                raise ValueError("stale session version")
            updated = connection.execute(
                "SELECT * FROM exercise_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            return dict(updated), False

    def list_sessions(
        self, *, cursor: int = 0, limit: int = 20, status: str | None = None
    ) -> tuple[list[dict[str, Any]], int | None]:
        clauses = ["profile_id = ?"]
        parameters: list[Any] = [DEMO_PROFILE_ID]
        if status is not None:
            clauses.append("status = ?")
            parameters.append(status)
        parameters.extend([limit + 1, cursor])
        with self.connect(read_only=True) as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM exercise_sessions
                WHERE {' AND '.join(clauses)}
                ORDER BY started_at DESC, session_id DESC
                LIMIT ? OFFSET ?
                """,
                parameters,
            ).fetchall()
        has_more = len(rows) > limit
        items = [dict(row) for row in rows[:limit]]
        return items, cursor + limit if has_more else None

    def create_conversation(
        self, *, client_conversation_id: str, session_id: str | None
    ) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                """
                SELECT * FROM conversations
                WHERE profile_id = ? AND client_conversation_id = ?
                """,
                (DEMO_PROFILE_ID, client_conversation_id),
            ).fetchone()
            if existing is not None:
                if existing["session_id"] != session_id:
                    raise ValueError("conversation idempotency conflict")
                return dict(existing), True
            if session_id is not None:
                owner = connection.execute(
                    """
                    SELECT 1 FROM exercise_sessions
                    WHERE session_id = ? AND profile_id = ?
                    """,
                    (session_id, DEMO_PROFILE_ID),
                ).fetchone()
                if owner is None:
                    raise LookupError("session not found")
            now = utc_now()
            conversation_id = str(uuid4())
            connection.execute(
                """
                INSERT INTO conversations (
                    conversation_id, profile_id, session_id,
                    client_conversation_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'open', ?, ?)
                """,
                (
                    conversation_id,
                    DEMO_PROFILE_ID,
                    session_id,
                    client_conversation_id,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            return dict(row), False

    def conversation(self, conversation_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                """
                SELECT * FROM conversations
                WHERE conversation_id = ? AND profile_id = ?
                """,
                (conversation_id, DEMO_PROFILE_ID),
            ).fetchone()
        return self._dict(row)

    def request_message(self, request_id: str) -> dict[str, Any] | None:
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM messages WHERE request_id = ?", (request_id,)
            ).fetchone()
        return self._dict(row)

    def assistant_for_request(self, request_id: str) -> dict[str, Any] | None:
        client_message_id = str(uuid5(NAMESPACE_URL, f"breathbloom:{request_id}:assistant"))
        with self.connect(read_only=True) as connection:
            row = connection.execute(
                "SELECT * FROM messages WHERE client_message_id = ?",
                (client_message_id,),
            ).fetchone()
        return self._dict(row)

    def create_request_message(
        self,
        *,
        conversation_id: str,
        request_id: str,
        request_purpose: str,
        content: str,
    ) -> tuple[dict[str, Any], bool]:
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM messages WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing is not None:
                if existing["conversation_id"] != conversation_id:
                    raise ValueError("request idempotency conflict")
                return dict(existing), True
            owner = connection.execute(
                """
                SELECT 1 FROM conversations
                WHERE conversation_id = ? AND profile_id = ? AND status = 'open'
                """,
                (conversation_id, DEMO_PROFILE_ID),
            ).fetchone()
            if owner is None:
                raise LookupError("conversation not found")
            ordinal = connection.execute(
                "SELECT COALESCE(MAX(ordinal), -1) + 1 FROM messages WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()[0]
            now = utc_now()
            message_id = str(uuid4())
            client_message_id = str(uuid5(NAMESPACE_URL, f"breathbloom:{request_id}:user"))
            connection.execute(
                """
                INSERT INTO messages (
                    message_id, conversation_id, client_message_id, ordinal,
                    role, content, request_id, request_purpose, request_status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'user', ?, ?, ?, 'pending', ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    client_message_id,
                    ordinal,
                    content,
                    request_id,
                    request_purpose,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM messages WHERE message_id = ?", (message_id,)
            ).fetchone()
            return dict(row), False

    def mark_request_failed(self, *, request_id: str, safe_error_code: str) -> None:
        with self.transaction() as connection:
            connection.execute(
                """
                UPDATE messages
                SET request_status = 'failed', safe_error_code = ?, updated_at = ?
                WHERE request_id = ? AND request_status = 'pending'
                """,
                (safe_error_code, utc_now(), request_id),
            )

    def complete_request(
        self, *, request_id: str, assistant_content: str
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            user_message = connection.execute(
                "SELECT * FROM messages WHERE request_id = ?", (request_id,)
            ).fetchone()
            if user_message is None or user_message["request_status"] != "pending":
                raise ValueError("request is no longer pending")
            ordinal = connection.execute(
                "SELECT COALESCE(MAX(ordinal), -1) + 1 FROM messages WHERE conversation_id = ?",
                (user_message["conversation_id"],),
            ).fetchone()[0]
            now = utc_now()
            assistant_id = str(uuid4())
            client_message_id = str(uuid5(NAMESPACE_URL, f"breathbloom:{request_id}:assistant"))
            connection.execute(
                """
                INSERT INTO messages (
                    message_id, conversation_id, client_message_id, ordinal,
                    role, content, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'assistant', ?, ?, ?)
                """,
                (
                    assistant_id,
                    user_message["conversation_id"],
                    client_message_id,
                    ordinal,
                    assistant_content,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                UPDATE messages
                SET request_status = 'succeeded', safe_error_code = NULL, updated_at = ?
                WHERE request_id = ? AND request_status = 'pending'
                """,
                (now, request_id),
            )
            assistant = connection.execute(
                "SELECT * FROM messages WHERE message_id = ?", (assistant_id,)
            ).fetchone()
            return dict(assistant)

    def list_messages(
        self, *, conversation_id: str, cursor: int = 0, limit: int = 50
    ) -> tuple[list[dict[str, Any]], int | None]:
        if self.conversation(conversation_id) is None:
            raise LookupError("conversation not found")
        with self.connect(read_only=True) as connection:
            rows = connection.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ? AND ordinal >= ?
                ORDER BY ordinal ASC
                LIMIT ?
                """,
                (conversation_id, cursor, limit + 1),
            ).fetchall()
        has_more = len(rows) > limit
        items = [dict(row) for row in rows[:limit]]
        next_cursor = items[-1]["ordinal"] + 1 if has_more and items else None
        return items, next_cursor

    def reset_demo(
        self, *, expected_reset_version: int, idempotency_key: str
    ) -> tuple[dict[str, Any], dict[str, int], bool]:
        with self.transaction() as connection:
            profile = connection.execute(
                "SELECT * FROM demo_profiles WHERE profile_id = ?", (DEMO_PROFILE_ID,)
            ).fetchone()
            if profile is None:
                raise sqlite3.DatabaseError("fictional profile unavailable")
            if profile["last_reset_key"] == idempotency_key:
                return dict(profile), {"messages": 0, "conversations": 0, "sessions": 0}, True
            if profile["reset_version"] != expected_reset_version:
                raise ValueError("stale reset version")
            counts = {
                "messages": connection.execute(
                    """
                    SELECT COUNT(*) FROM messages
                    WHERE conversation_id IN (
                        SELECT conversation_id FROM conversations WHERE profile_id = ?
                    )
                    """,
                    (DEMO_PROFILE_ID,),
                ).fetchone()[0],
                "conversations": connection.execute(
                    "SELECT COUNT(*) FROM conversations WHERE profile_id = ?",
                    (DEMO_PROFILE_ID,),
                ).fetchone()[0],
                "sessions": connection.execute(
                    "SELECT COUNT(*) FROM exercise_sessions WHERE profile_id = ?",
                    (DEMO_PROFILE_ID,),
                ).fetchone()[0],
            }
            connection.execute("DELETE FROM conversations WHERE profile_id = ?", (DEMO_PROFILE_ID,))
            connection.execute("DELETE FROM exercise_sessions WHERE profile_id = ?", (DEMO_PROFILE_ID,))
            connection.execute("DELETE FROM preferences WHERE profile_id = ?", (DEMO_PROFILE_ID,))
            now = utc_now()
            connection.execute(
                """
                INSERT INTO preferences (
                    preference_id, profile_id, motion_mode, guidance_level,
                    source, version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'reset', 1, ?, ?)
                """,
                (str(uuid4()), DEMO_PROFILE_ID, DEFAULT_MOTION, DEFAULT_GUIDANCE, now, now),
            )
            connection.execute(
                """
                UPDATE demo_profiles
                SET reset_version = reset_version + 1, last_reset_key = ?, updated_at = ?
                WHERE profile_id = ?
                """,
                (idempotency_key, now, DEMO_PROFILE_ID),
            )
            updated = connection.execute(
                "SELECT * FROM demo_profiles WHERE profile_id = ?", (DEMO_PROFILE_ID,)
            ).fetchone()
            return dict(updated), counts, False
