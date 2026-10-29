"""FocusBloom version-2 deterministic business rules and model orchestration."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Any

from .config import Settings
from .database import ACTIVITY_TYPES, Repository
from .errors import (
    APIError, DATABASE_FAILURE_MESSAGE, MISSING_CONFIGURATION_MESSAGE,
    MODEL_FAILURE_MESSAGE, NO_MATCH_MESSAGE, QUERY_REJECTED_MESSAGE,
)
from .gemini import (
    GeminiGateway, GoogleGeminiGateway, ProviderProblem, validate_grounded_answer,
    validate_perspective, validate_query_proposal,
)
from .rag import QueryRejected, RetrievalFailure, execute_read_only, validate_query
from .schemas import (
    ActivityEventCreate, ActivitySessionCreate, ActivitySessionUpdate, ConversationCreate,
    DemoResetRequest, HistoryMessageCreate, HistoryRunRequest, NextStepSeedCreate,
    PerspectiveAlternativesRequest, PerspectiveArtifactCreate, PreferenceUpdate,
)


ACTIVITIES = (
    {"activity_type": "different_leaf", "label": "Different leaf", "instruction": "Choose the leaf with a different shape."},
    {"activity_type": "ripple_path", "label": "Ripple path", "instruction": "Follow the marked ripple across the lily pads."},
    {"activity_type": "flower_match", "label": "Flower match", "instruction": "Choose the two flowers with the same pattern."},
    {"activity_type": "flower_change", "label": "Flower change", "instruction": "Choose the flower that changed."},
    {"activity_type": "petal_sequence", "label": "Petal sequence", "instruction": "Rebuild the short visible petal sequence."},
    {"activity_type": "clue_search", "label": "Clue search", "instruction": "Find the garden object that matches the visible clues."},
    {"activity_type": "garden_path", "label": "Garden path", "instruction": "Connect the two marked garden locations."},
)


def _hash(value: Any) -> str:
    serialized = json.dumps(value, separators=(",", ":"), sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _conflict(message: str) -> APIError:
    return APIError(409, "invalid_request", message)


def _not_found(message: str) -> APIError:
    return APIError(404, "not_found", message)


def _database_failure() -> APIError:
    return APIError(503, "database_failure", DATABASE_FAILURE_MESSAGE)


def public_preferences(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "motion_mode": row["motion_mode"], "guidance_level": row["guidance_level"],
        "difficulty": row["difficulty"], "remember_preferences": bool(row["remember_preferences"]),
        "version": row["version"], "updated_at": row["updated_at"],
    }


def public_session(row: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "session_id", "activity_type", "status", "started_at", "ended_at", "duration_ms",
        "difficulty", "motion_mode", "guidance_level", "perspective_progress",
        "alternative_save_state", "seed_save_state", "model_status", "version",
        "created_at", "updated_at",
    )
    return {field: row[field] for field in fields}


def public_event(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": row["event_id"], "session_id": row["session_id"],
        "ordinal": row["ordinal"], "event_type": row["event_type"],
        "happened_at": row["happened_at"], "elapsed_ms": row["elapsed_ms"],
        "payload": json.loads(row["payload_json"]), "created_at": row["created_at"],
    }


def public_artifact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_id": row["artifact_id"], "session_id": row["session_id"],
        "interpretation_text": row["interpretation_text"],
        "supporting_evidence": json.loads(row["supporting_evidence_json"]),
        "uncertainty": json.loads(row["uncertainty_json"]),
        "alternative_text": row["alternative_text"], "alternative_source": row["alternative_source"],
        "observer_mode": row["observer_mode"], "saved_at": row["saved_at"], "updated_at": row["updated_at"],
    }


def public_seed(row: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "seed_id", "session_id", "situation_text", "action_text", "formatted_plan",
        "source", "saved_at", "updated_at",
    )
    return {field: row[field] for field in fields}


def public_conversation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "conversation_id": row["conversation_id"], "purpose": row["purpose"],
        "created_at": row["created_at"], "updated_at": row["updated_at"],
    }


def public_message(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "message_id": row["message_id"], "conversation_id": row["conversation_id"],
        "ordinal": row["ordinal"], "role": row["role"], "content": row["content"],
        "created_at": row["created_at"],
    }


def public_request(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": row["request_id"], "purpose": row["purpose"], "status": row["status"],
        "safe_error_code": row["safe_error_code"], "attempt_count": row["attempt_count"],
        "created_at": row["created_at"], "updated_at": row["updated_at"],
    }


class FocusBloomService:
    def __init__(self, repository: Repository, settings: Settings, gateway: GeminiGateway | None = None) -> None:
        self.repository = repository
        self.settings = settings
        self.gateway = gateway

    @property
    def model(self) -> GeminiGateway:
        return self.gateway or GoogleGeminiGateway(self.settings)

    def get_preferences(self) -> dict[str, Any]:
        try:
            return {"outcome": "success", "preferences": public_preferences(self.repository.preferences())}
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc

    def update_preferences(self, payload: PreferenceUpdate) -> dict[str, Any]:
        try:
            row, duplicate = self.repository.update_preferences({
                "motion_mode": payload.motion_mode.value,
                "guidance_level": payload.guidance_level.value,
                "difficulty": payload.difficulty.value,
                "remember_preferences": payload.remember_preferences,
                "expected_version": payload.expected_version,
                "idempotency_key": str(payload.idempotency_key),
            })
        except ValueError as exc:
            raise _conflict("The preference version or idempotency key is not current.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "preferences": public_preferences(row)}

    def focus_activities(self) -> dict[str, Any]:
        return {
            "outcome": "success", "activities": ACTIVITIES,
            "controls": ["Show me", "Skip this", "Stop", "Support"],
            "notice": "Optional fictional coursework activities; no scores or mental-health conclusions.",
        }

    def create_session(self, payload: ActivitySessionCreate) -> dict[str, Any]:
        try:
            row, duplicate = self.repository.create_session({
                "client_session_id": str(payload.client_session_id),
                "activity_type": payload.activity_type.value, "started_at": payload.started_at,
                "difficulty": payload.difficulty.value, "motion_mode": payload.motion_mode.value,
                "guidance_level": payload.guidance_level.value,
            })
        except ValueError as exc:
            raise _conflict("The client session identifier conflicts with a stored session.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "session": public_session(row)}

    def update_session(self, session_id: str, payload: ActivitySessionUpdate) -> dict[str, Any]:
        try:
            current = self.repository.session(session_id)
            if current is None:
                raise _not_found("The fictional activity session was not found.")
            started = datetime.strptime(current["started_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            ended = datetime.strptime(payload.ended_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            if ended < started:
                raise _conflict("The end time cannot precede the start time.")
            row, duplicate = self.repository.update_session(session_id, {
                "action": payload.action, "expected_version": payload.expected_version,
                "ended_at": payload.ended_at, "duration_ms": payload.duration_ms,
                "perspective_progress": payload.perspective_progress.value,
                "model_status": payload.model_status.value,
            })
        except APIError:
            raise
        except LookupError as exc:
            raise _not_found("The fictional activity session was not found.") from exc
        except ValueError as exc:
            raise _conflict("The session version or lifecycle transition is not current.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "session": public_session(row)}

    def create_event(self, session_id: str, payload: ActivityEventCreate) -> dict[str, Any]:
        try:
            row, duplicate = self.repository.create_event(session_id, {
                "client_event_id": str(payload.client_event_id), "ordinal": payload.ordinal,
                "event_type": payload.event_type, "happened_at": payload.happened_at,
                "elapsed_ms": payload.elapsed_ms, "payload": payload.payload.model_dump(exclude_none=True),
            })
        except LookupError as exc:
            raise _not_found("The fictional activity session was not found.") from exc
        except (ValueError, sqlite3.IntegrityError) as exc:
            raise _conflict("The event identifier or ordinal conflicts with stored activity data.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "event": public_event(row)}

    def list_sessions(self, cursor: int, limit: int, status: str | None, activity_type: str | None) -> dict[str, Any]:
        try:
            rows, next_cursor = self.repository.list_sessions(cursor, limit, status, activity_type)
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "sessions": [public_session(row) for row in rows], "next_cursor": next_cursor}

    def get_session(self, session_id: str) -> dict[str, Any]:
        try:
            row, events = self.repository.session_with_events(session_id)
        except LookupError as exc:
            raise _not_found("The fictional activity session was not found.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "session": public_session(row), "events": [public_event(event) for event in events]}

    def perspective_alternatives(self, payload: PerspectiveAlternativesRequest) -> tuple[int, dict[str, Any]]:
        context = {
            "interpretation": payload.interpretation,
            "supporting_evidence": payload.supporting_evidence,
            "uncertainty": payload.uncertainty,
            "observer_mode": payload.observer_mode,
        }
        try:
            request, duplicate = self.repository.create_model_request(
                idempotency_key=str(payload.idempotency_key), purpose="perspective_alternatives",
                input_hash=_hash(context),
            )
        except ValueError as exc:
            raise _conflict("The model-request identifier conflicts with a different request.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        if duplicate:
            return 200, {"outcome": "duplicate_request", "request": public_request(request), "alternatives": None}
        if self.settings.gemini_api_key_status != "configured":
            self.repository.update_model_request(request["request_id"], status="failed", safe_error_code="missing_configuration", attempt_count=0)
            raise APIError(503, "missing_configuration", MISSING_CONFIGURATION_MESSAGE)
        try:
            output = validate_perspective(self.model.perspective(context))
        except ProviderProblem as exc:
            self.repository.update_model_request(
                request["request_id"], status="failed", safe_error_code=exc.safe_error_code, attempt_count=1
            )
            raise APIError(exc.status_code, "model_failure", MODEL_FAILURE_MESSAGE) from exc
        request = self.repository.update_model_request(request["request_id"], status="succeeded", attempt_count=1)
        return 200, {
            "outcome": "success", "request": public_request(request),
            "alternatives": output.model_dump(), "saved": False,
        }

    def create_artifact(self, payload: PerspectiveArtifactCreate) -> dict[str, Any]:
        try:
            values = payload.model_dump(mode="json")
            values["session_id"] = str(payload.session_id) if payload.session_id else None
            values["client_artifact_id"] = str(payload.client_artifact_id)
            row, duplicate = self.repository.create_artifact(values)
        except LookupError as exc:
            raise _not_found("The related fictional session was not found.") from exc
        except ValueError as exc:
            raise _conflict("The artifact identifier conflicts with different saved content.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "artifact": public_artifact(row)}

    def list_artifacts(self, cursor: int, limit: int) -> dict[str, Any]:
        try:
            rows, next_cursor = self.repository.list_artifacts(cursor, limit)
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "artifacts": [public_artifact(row) for row in rows], "next_cursor": next_cursor}

    def delete_artifact(self, artifact_id: str) -> dict[str, Any]:
        try:
            deleted = self.repository.delete_artifact(artifact_id)
        except LookupError as exc:
            raise _not_found("The saved Perspective artifact was not found.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "deleted": deleted}

    def create_seed(self, payload: NextStepSeedCreate) -> dict[str, Any]:
        try:
            values = payload.model_dump(mode="json")
            values["session_id"] = str(payload.session_id) if payload.session_id else None
            values["client_seed_id"] = str(payload.client_seed_id)
            row, duplicate = self.repository.create_seed(values)
        except LookupError as exc:
            raise _not_found("The related fictional session was not found.") from exc
        except ValueError as exc:
            raise _conflict("The seed identifier conflicts with different saved content.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "seed": public_seed(row)}

    def list_seeds(self, cursor: int, limit: int) -> dict[str, Any]:
        try:
            rows, next_cursor = self.repository.list_seeds(cursor, limit)
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "seeds": [public_seed(row) for row in rows], "next_cursor": next_cursor}

    def delete_seed(self, seed_id: str) -> dict[str, Any]:
        try:
            deleted = self.repository.delete_seed(seed_id)
        except LookupError as exc:
            raise _not_found("The saved Next-Step Seed was not found.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "deleted": deleted}

    def create_conversation(self, payload: ConversationCreate) -> dict[str, Any]:
        try:
            row, duplicate = self.repository.create_conversation(str(payload.client_conversation_id))
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "conversation": public_conversation(row)}

    def list_messages(self, conversation_id: str, cursor: int, limit: int) -> dict[str, Any]:
        try:
            rows, next_cursor = self.repository.list_messages(conversation_id, cursor, limit)
        except LookupError as exc:
            raise _not_found("The history-guide conversation was not found.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "success", "messages": [public_message(row) for row in rows], "next_cursor": next_cursor}

    def create_history_message(self, conversation_id: str, payload: HistoryMessageCreate) -> dict[str, Any]:
        try:
            message, request, duplicate = self.repository.create_history_request(
                conversation_id, str(payload.idempotency_key), payload.question, _hash({"question": payload.question})
            )
        except LookupError as exc:
            raise _not_found("The history-guide conversation was not found.") from exc
        except ValueError as exc:
            raise _conflict("The request identifier belongs to another conversation.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {
            "outcome": "duplicate_request" if duplicate else "success",
            "message": public_message(message), "request": public_request(request),
        }

    def run_history(self, payload: HistoryRunRequest) -> tuple[int, dict[str, Any]]:
        try:
            request = self.repository.model_request(str(payload.request_id))
            if request is None or request["purpose"] != "history_sql":
                raise _not_found("The accepted history question request was not found.")
            question_row = self.repository.message(request["initiating_message_id"])
            if question_row is None:
                raise _not_found("The accepted history question was not found.")
        except APIError:
            raise
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        if request["status"] != "accepted":
            return 200, {"outcome": "duplicate_request", "request": public_request(request), "answer": None}
        if self.settings.gemini_api_key_status != "configured":
            self.repository.update_model_request(request["request_id"], status="failed", safe_error_code="missing_configuration", attempt_count=0)
            raise APIError(503, "missing_configuration", MISSING_CONFIGURATION_MESSAGE)
        try:
            proposal = validate_query_proposal(self.model.propose_history_query(question_row["content"]))
        except ProviderProblem as exc:
            self.repository.update_model_request(
                request["request_id"], status="failed", safe_error_code=exc.safe_error_code, attempt_count=1
            )
            raise APIError(exc.status_code, "model_failure", MODEL_FAILURE_MESSAGE) from exc
        if proposal.outcome == "out_of_scope":
            rejected = self.repository.update_model_request(
                request["request_id"], status="query_rejected", safe_error_code="out_of_scope", attempt_count=1
            )
            return 422, {"outcome": "history_query_rejected", "message": QUERY_REJECTED_MESSAGE, "request": public_request(rejected)}
        try:
            query = validate_query(proposal.sql or "", proposal.parameters)
            retrieved = execute_read_only(self.settings.database_path, query)
        except QueryRejected:
            rejected = self.repository.update_model_request(
                request["request_id"], status="query_rejected", safe_error_code="query_rejected", attempt_count=1
            )
            return 422, {"outcome": "history_query_rejected", "message": QUERY_REJECTED_MESSAGE, "request": public_request(rejected)}
        except RetrievalFailure as exc:
            failed = self.repository.update_model_request(
                request["request_id"], status="failed", safe_error_code="retrieval_failure", attempt_count=1
            )
            raise APIError(503, "database_failure", DATABASE_FAILURE_MESSAGE) from exc
        if not retrieved.rows:
            no_match = self.repository.update_model_request(
                request["request_id"], status="no_match", safe_error_code=None, attempt_count=1
            )
            return 200, {"outcome": "history_no_match", "message": NO_MATCH_MESSAGE, "request": public_request(no_match), "answer": None}

        sql_request = self.repository.update_model_request(
            request["request_id"], status="succeeded", attempt_count=1, row_refs=list(retrieved.row_references)
        )
        answer_context = {
            "question": question_row["content"], "intent": proposal.intent,
            "columns": retrieved.columns,
            "rows": [
                {"row_reference": index, "values": list(row)}
                for index, row in zip(retrieved.row_references, retrieved.rows, strict=True)
            ],
        }
        answer_request, duplicate = self.repository.create_model_request(
            idempotency_key=f"history-answer:{request['request_id']}", purpose="history_answer",
            input_hash=_hash(answer_context), conversation_id=request["conversation_id"],
            initiating_message_id=request["initiating_message_id"],
        )
        if duplicate:
            return 200, {"outcome": "duplicate_request", "request": public_request(answer_request), "answer": None}
        try:
            answer = validate_grounded_answer(self.model.answer_history(answer_context))
            references = answer.row_references
            if len(references) != len(set(references)) or not set(references).issubset(retrieved.row_references):
                raise ProviderProblem("invalid_grounding")
        except ProviderProblem as exc:
            self.repository.update_model_request(
                answer_request["request_id"], status="failed", safe_error_code=exc.safe_error_code, attempt_count=1
            )
            raise APIError(exc.status_code, "model_failure", MODEL_FAILURE_MESSAGE) from exc
        try:
            assistant = self.repository.complete_history_answer(
                sql_request_id=sql_request["request_id"], answer_request_id=answer_request["request_id"],
                answer=answer.answer, row_refs=references,
            )
        except (OSError, sqlite3.Error, ValueError) as exc:
            try:
                self.repository.update_model_request(
                    answer_request["request_id"], status="failed", safe_error_code="persistence_failure", attempt_count=1
                )
            except (OSError, sqlite3.Error):
                pass
            raise _database_failure() from exc
        completed = self.repository.model_request(answer_request["request_id"])
        return 200, {
            "outcome": "success", "request": public_request(completed),
            "answer": public_message(assistant), "row_references": references,
        }

    def delete_saved_text(self) -> dict[str, Any]:
        try:
            return {"outcome": "success", "deleted": self.repository.delete_saved_text()}
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc

    def reset_demo(self, payload: DemoResetRequest) -> dict[str, Any]:
        try:
            version, counts, duplicate = self.repository.reset_demo(payload.expected_reset_version)
        except ValueError as exc:
            raise _conflict("The reset version is not current.") from exc
        except (OSError, sqlite3.Error) as exc:
            raise _database_failure() from exc
        return {"outcome": "duplicate_request" if duplicate else "success", "reset_version": version, "deleted": counts}
