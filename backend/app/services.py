"""Deterministic backend rules above the SQLite and Gemini adapters."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any
from uuid import uuid4

from .config import GEMINI_HISTORY_LIMIT, GEMINI_MAX_CONTEXT_CHARS, Settings
from .database import Repository, utc_now
from .errors import APIError, DATABASE_FAILURE_MESSAGE
from .gemini import (
    GeminiGateway,
    GoogleGeminiGateway,
    ProviderProblem,
    validate_provider_payload,
)
from .schemas import (
    CompleteAction,
    ConversationCreate,
    DemoResetRequest,
    InterruptAction,
    ModelActionRequest,
    PreferenceUpdate,
    RequestKind,
    SaveNextTimeSetupAction,
    SessionAction,
    SessionSnapshotAction,
    SessionStart,
    StopAction,
)


PURPOSE_BY_KIND = {
    RequestKind.INTRODUCTION: "introduction",
    RequestKind.REFLECTION: "factual_reflection",
    RequestKind.HISTORY_SUMMARY: "history_question",
}

CANONICAL_LABELS = {
    RequestKind.INTRODUCTION: "Requested a brief practice introduction.",
    RequestKind.REFLECTION: "Requested a factual reflection for a fictional practice.",
    RequestKind.HISTORY_SUMMARY: "Requested a factual summary of recent fictional practices.",
}

MISSING_CONFIGURATION_MESSAGE = (
    "The optional Gemini request is not configured. The available prototype, "
    "factual history, and Support information remain available."
)


def public_preference(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "motion_mode": row["motion_mode"],
        "guidance_level": row["guidance_level"],
        "source": row["source"],
        "version": row["version"],
        "updated_at": row["updated_at"],
        "persistence_status": "saved",
    }


def public_session(row: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "session_id",
        "status",
        "started_at",
        "ended_at",
        "planned_duration_ms",
        "observed_active_duration_ms",
        "paused_duration_ms",
        "wall_clock_duration_ms",
        "completed_cycles",
        "ending_phase",
        "phase_elapsed_ms",
        "motion_mode",
        "guidance_level",
        "next_time_setup",
        "persistence_status",
        "version",
        "created_at",
        "updated_at",
    )
    return {field: row[field] for field in fields}


def public_conversation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "conversation_id": row["conversation_id"],
        "session_id": row["session_id"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "persistence_status": "saved",
    }


def public_message(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "message_id": row["message_id"],
        "conversation_id": row["conversation_id"],
        "ordinal": row["ordinal"],
        "role": row["role"],
        "content": row["content"],
        "request_id": row["request_id"],
        "request_purpose": row["request_purpose"],
        "request_status": row["request_status"],
        "safe_error_code": row["safe_error_code"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _conflict(message: str) -> APIError:
    return APIError(409, "invalid_request", message)


def _not_found(message: str) -> APIError:
    return APIError(404, "invalid_request", message)


def _database_failure() -> APIError:
    return APIError(503, "database_failure", DATABASE_FAILURE_MESSAGE)


class LegacyV1Service:
    def __init__(
        self,
        repository: Repository,
        settings: Settings,
        gateway: GeminiGateway | None = None,
    ) -> None:
        self.repository = repository
        self.settings = settings
        self.gateway = gateway

    def get_preferences(self) -> dict[str, Any]:
        try:
            return {"outcome": "success", "preferences": public_preference(self.repository.preferences())}
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc

    def update_preferences(self, payload: PreferenceUpdate) -> dict[str, Any]:
        try:
            row, duplicate = self.repository.update_preferences(
                motion_mode=payload.motion_mode.value,
                guidance_level=payload.guidance_level.value,
                expected_version=payload.expected_version,
                idempotency_key=str(payload.idempotency_key),
            )
        except ValueError as exc:
            raise _conflict("The preference version or idempotency key is not current.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "duplicate_request" if duplicate else "success",
            "preferences": public_preference(row),
        }

    def start_session(self, payload: SessionStart) -> dict[str, Any]:
        values = {
            "session_id": str(uuid4()),
            "client_session_id": str(payload.client_session_id),
            "create_idempotency_key": str(payload.idempotency_key),
            "started_at": payload.started_at,
            "motion_mode": payload.motion_mode.value,
            "guidance_level": payload.guidance_level.value,
            "created_at": utc_now(),
        }
        try:
            row, duplicate = self.repository.create_session(values)
        except ValueError as exc:
            raise _conflict("The session identifiers conflict with an existing request.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "duplicate_request" if duplicate else "success",
            "session": public_session(row),
        }

    @staticmethod
    def _validate_snapshot(payload: SessionSnapshotAction, action: str) -> None:
        active = payload.observed_active_duration_ms
        paused = payload.paused_duration_ms
        if payload.wall_clock_duration_ms < active + paused:
            raise _conflict("Wall-clock duration cannot be shorter than active plus paused time.")

        if action == "complete":
            if (
                active < 60_000
                or payload.completed_cycles != 6
                or payload.ending_phase.value != "exhale"
                or payload.phase_elapsed_ms < 6_000
            ):
                raise _conflict("Completion requires the deterministic six-cycle 60-second state.")
            return

        if active >= 60_000 or payload.completed_cycles >= 6:
            raise _conflict("A non-complete snapshot must remain below the completion boundary.")
        expected_cycles = active // 10_000
        if payload.completed_cycles != expected_cycles:
            raise _conflict("Completed cycles do not match deterministic active time.")
        remainder = active % 10_000
        expected_phase = "inhale" if remainder < 4_000 else "exhale"
        expected_phase_elapsed = remainder if remainder < 4_000 else remainder - 4_000
        if payload.ending_phase.value != expected_phase or payload.phase_elapsed_ms != expected_phase_elapsed:
            raise _conflict("Phase state does not match deterministic active time.")

    def update_session(self, session_id: str, payload: SessionAction) -> dict[str, Any]:
        try:
            current = self.repository.session(session_id)
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        if current is None:
            raise _not_found("The fictional session was not found.")

        action = payload.action
        if current["last_action_id"] == str(payload.idempotency_key):
            return {"outcome": "duplicate_request", "session": public_session(current)}
        allowed = {
            "pause": {"active"},
            "resume": {"paused"},
            "stop": {"active", "paused"},
            "complete": {"active"},
            "interrupt": {"active", "paused"},
            "save_next_time_setup": {"completed", "stopped"},
        }
        if current["status"] not in allowed[action]:
            raise _conflict("That session action is not valid from the current state.")

        if isinstance(payload, SaveNextTimeSetupAction):
            updates = {"next_time_setup": payload.next_time_setup.value}
        else:
            self._validate_snapshot(payload, action)
            status_by_action = {
                "pause": "paused",
                "resume": "active",
                "stop": "stopped",
                "complete": "completed",
                "interrupt": "interrupted",
            }
            updates = {
                "status": status_by_action[action],
                "observed_active_duration_ms": payload.observed_active_duration_ms,
                "paused_duration_ms": payload.paused_duration_ms,
                "wall_clock_duration_ms": payload.wall_clock_duration_ms,
                "completed_cycles": payload.completed_cycles,
                "ending_phase": payload.ending_phase.value,
                "phase_elapsed_ms": payload.phase_elapsed_ms,
                "persistence_status": "saved",
            }
            if isinstance(payload, (StopAction, CompleteAction, InterruptAction)):
                started = datetime.strptime(current["started_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                ended = datetime.strptime(payload.ended_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                if ended < started:
                    raise _conflict("The terminal timestamp cannot precede session start.")
                updates["ended_at"] = payload.ended_at

        try:
            row, duplicate = self.repository.update_session(
                session_id=session_id,
                expected_version=payload.expected_version,
                action_id=str(payload.idempotency_key),
                updates=updates,
            )
        except LookupError as exc:
            raise _not_found("The fictional session was not found.") from exc
        except ValueError as exc:
            raise _conflict("The session version or idempotency key is not current.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "duplicate_request" if duplicate else "success",
            "session": public_session(row),
        }

    def list_sessions(self, cursor: int, limit: int, status: str | None) -> dict[str, Any]:
        try:
            rows, next_cursor = self.repository.list_sessions(
                cursor=cursor, limit=limit, status=status
            )
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "success",
            "sessions": [public_session(row) for row in rows],
            "next_cursor": next_cursor,
        }

    def get_session(self, session_id: str) -> dict[str, Any]:
        try:
            row = self.repository.session(session_id)
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        if row is None:
            raise _not_found("The fictional session was not found.")
        return {"outcome": "success", "session": public_session(row)}

    def create_conversation(self, payload: ConversationCreate) -> dict[str, Any]:
        try:
            row, duplicate = self.repository.create_conversation(
                client_conversation_id=str(payload.client_conversation_id),
                session_id=str(payload.session_id) if payload.session_id else None,
            )
        except LookupError as exc:
            raise _not_found("The related fictional session was not found.") from exc
        except ValueError as exc:
            raise _conflict("The conversation identifier conflicts with an existing request.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "duplicate_request" if duplicate else "success",
            "conversation": public_conversation(row),
        }

    def list_messages(self, conversation_id: str, cursor: int, limit: int) -> dict[str, Any]:
        try:
            rows, next_cursor = self.repository.list_messages(
                conversation_id=conversation_id, cursor=cursor, limit=limit
            )
        except LookupError as exc:
            raise _not_found("The fictional conversation was not found.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "success",
            "messages": [public_message(row) for row in rows],
            "next_cursor": next_cursor,
        }

    def _build_model_context(
        self, conversation: dict[str, Any], payload: ModelActionRequest
    ) -> str:
        profile = self.repository.profile()
        preferences = self.repository.preferences()
        context: dict[str, Any] = {
            "coursework_scope": "fictional FocusBloom data only",
            "profile_label": profile["display_label"],
            "request_kind": payload.request_kind.value,
        }
        if payload.request_kind is RequestKind.INTRODUCTION:
            context["preferences"] = {
                "motion_mode": preferences["motion_mode"],
                "guidance_level": preferences["guidance_level"],
            }
        elif payload.request_kind is RequestKind.REFLECTION:
            session_id = str(payload.session_id)
            session = self.repository.session(session_id)
            if session is None:
                raise _not_found("The reflection session was not found.")
            if conversation["session_id"] not in (None, session_id):
                raise _conflict("The reflection session does not match the conversation.")
            if session["status"] not in ("completed", "stopped"):
                raise _conflict("A reflection requires a completed or stopped fictional practice.")
            context["reflection_choice"] = payload.reflection_choice.value
            context["session"] = {
                key: session[key]
                for key in (
                    "session_id",
                    "status",
                    "started_at",
                    "observed_active_duration_ms",
                    "completed_cycles",
                    "motion_mode",
                    "guidance_level",
                )
            }
        else:
            sessions, _ = self.repository.list_sessions(limit=GEMINI_HISTORY_LIMIT)
            context["recent_sessions"] = [
                {
                    key: row[key]
                    for key in (
                        "session_id",
                        "status",
                        "started_at",
                        "observed_active_duration_ms",
                        "completed_cycles",
                        "motion_mode",
                        "guidance_level",
                    )
                }
                for row in sessions
            ]
        serialized = json.dumps(context, separators=(",", ":"), sort_keys=True)
        if len(serialized) > GEMINI_MAX_CONTEXT_CHARS:
            raise APIError(422, "invalid_request", "The approved model context is too large.")
        return serialized

    def request_model(
        self, conversation_id: str, payload: ModelActionRequest
    ) -> tuple[int, dict[str, Any]]:
        try:
            conversation = self.repository.conversation(conversation_id)
            if conversation is None:
                raise _not_found("The fictional conversation was not found.")
            request_id = str(payload.idempotency_key)
            existing = self.repository.request_message(request_id)
            if existing is not None:
                if existing["conversation_id"] != conversation_id:
                    raise _conflict("The model-request identifier belongs to another conversation.")
                assistant = self.repository.assistant_for_request(request_id)
                return 200, {
                    "outcome": "duplicate_request",
                    "request_status": existing["request_status"],
                    "safe_error_code": existing["safe_error_code"],
                    "user_message": public_message(existing),
                    "assistant_message": public_message(assistant) if assistant else None,
                }
            context = self._build_model_context(conversation, payload)
            user_message, duplicate = self.repository.create_request_message(
                conversation_id=conversation_id,
                request_id=request_id,
                request_purpose=PURPOSE_BY_KIND[payload.request_kind],
                content=CANONICAL_LABELS[payload.request_kind],
            )
            if duplicate:
                return 200, {
                    "outcome": "duplicate_request",
                    "request_status": user_message["request_status"],
                    "safe_error_code": user_message["safe_error_code"],
                    "user_message": public_message(user_message),
                    "assistant_message": None,
                }
        except APIError:
            raise
        except (ValueError, LookupError) as exc:
            raise _conflict("The model request conflicts with stored fictional data.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc

        if self.settings.gemini_api_key_status != "configured":
            try:
                self.repository.mark_request_failed(
                    request_id=request_id, safe_error_code="missing_configuration"
                )
            except (OSError, sqlite3.Error) as exc:
                raise _database_failure() from exc
            raise APIError(503, "missing_configuration", MISSING_CONFIGURATION_MESSAGE)

        gateway = self.gateway or GoogleGeminiGateway(self.settings)
        try:
            raw_payload = gateway.generate(context, payload.request_kind)
            validated = validate_provider_payload(raw_payload, payload.request_kind)
        except ProviderProblem as exc:
            try:
                self.repository.mark_request_failed(
                    request_id=request_id, safe_error_code=exc.safe_error_code
                )
            except (OSError, sqlite3.Error) as database_exc:
                raise _database_failure() from database_exc
            raise APIError(exc.status_code, exc.outcome, exc.message) from exc

        try:
            assistant = self.repository.complete_request(
                request_id=request_id,
                assistant_content=validated.response_text,
            )
        except (OSError, sqlite3.Error, ValueError) as exc:
            try:
                self.repository.mark_request_failed(
                    request_id=request_id, safe_error_code="persistence_failure"
                )
            except (OSError, sqlite3.Error):
                pass
            raise _database_failure() from exc
        succeeded = self.repository.request_message(request_id)
        return 201, {
            "outcome": "success",
            "request_status": "succeeded",
            "safe_error_code": None,
            "user_message": public_message(succeeded),
            "assistant_message": public_message(assistant),
        }

    def reset_demo(self, payload: DemoResetRequest) -> dict[str, Any]:
        try:
            profile, counts, duplicate = self.repository.reset_demo(
                expected_reset_version=payload.expected_reset_version,
                idempotency_key=str(payload.idempotency_key),
            )
        except ValueError as exc:
            raise _conflict("The reset version is not current.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "duplicate_request" if duplicate else "success",
            "reset_version": profile["reset_version"],
            "deleted": counts,
        }
