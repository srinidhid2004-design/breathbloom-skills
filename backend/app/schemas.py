"""Strict FocusBloom version-2 request and provider contracts."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def validate_utc_timestamp(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", value
    ) is None:
        raise ValueError("timestamp must use UTC ISO 8601 milliseconds")
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    if not 2000 <= parsed.year <= 2100:
        raise ValueError("timestamp outside supported coursework range")
    return value


UtcTimestamp = Annotated[str, BeforeValidator(validate_utc_timestamp)]


class MotionMode(str, Enum):
    STANDARD = "standard"
    NO_MOTION = "no_motion"


class GuidanceLevel(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    MORE = "more"


class Difficulty(str, Enum):
    EASY = "easy"
    STANDARD = "standard"
    CHALLENGE = "challenge"


class ActivityType(str, Enum):
    DIFFERENT_LEAF = "different_leaf"
    RIPPLE_PATH = "ripple_path"
    FLOWER_MATCH = "flower_match"
    FLOWER_CHANGE = "flower_change"
    PETAL_SEQUENCE = "petal_sequence"
    CLUE_SEARCH = "clue_search"
    GARDEN_PATH = "garden_path"
    PERSPECTIVE_STUDIO = "perspective_studio"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    STOPPED = "stopped"
    SKIPPED = "skipped"
    INTERRUPTED = "interrupted"


class PerspectiveProgress(str, Enum):
    NONE = "none"
    INTERPRETATION = "interpretation"
    EVIDENCE = "evidence"
    ALTERNATIVE = "alternative"
    REVIEWED = "reviewed"


class ModelStatus(str, Enum):
    SKIPPED = "skipped"
    LOADING = "loading"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    NO_MATCH = "no_match"
    QUERY_REJECTED = "query_rejected"


class PreferenceUpdate(StrictModel):
    motion_mode: MotionMode
    guidance_level: GuidanceLevel
    difficulty: Difficulty
    remember_preferences: bool
    expected_version: int = Field(ge=1)
    idempotency_key: UUID


class ActivitySessionCreate(StrictModel):
    client_session_id: UUID
    activity_type: ActivityType
    started_at: UtcTimestamp
    difficulty: Difficulty
    motion_mode: MotionMode
    guidance_level: GuidanceLevel


class ActivitySessionUpdate(StrictModel):
    action: Literal["complete", "stop", "skip", "interrupt"]
    expected_version: int = Field(ge=1)
    idempotency_key: UUID
    ended_at: UtcTimestamp
    duration_ms: int = Field(ge=0, le=86_400_000)
    perspective_progress: PerspectiveProgress = PerspectiveProgress.NONE
    model_status: ModelStatus = ModelStatus.SKIPPED

    @model_validator(mode="after")
    def validate_terminal_state(self) -> "ActivitySessionUpdate":
        if self.model_status is ModelStatus.LOADING:
            raise ValueError("a terminal session cannot retain loading model state")
        if self.action == "skip" and self.duration_ms != 0:
            raise ValueError("a skipped activity has zero duration")
        return self


class EventPayload(StrictModel):
    result: Literal["correct", "not_correct", "shown", "none"] | None = None
    item_id: str | None = Field(default=None, min_length=1, max_length=40)
    step: int | None = Field(default=None, ge=0, le=20)


class ActivityEventCreate(StrictModel):
    client_event_id: UUID
    ordinal: int = Field(ge=0, le=100)
    event_type: Literal[
        "started", "shown", "attempted", "completed", "stopped", "skipped",
        "interrupted", "perspective_step", "alternative_reviewed"
    ]
    happened_at: UtcTimestamp
    elapsed_ms: int = Field(ge=0, le=86_400_000)
    payload: EventPayload = Field(default_factory=EventPayload)


class PerspectiveAlternativesRequest(StrictModel):
    idempotency_key: UUID
    interpretation: str = Field(min_length=1, max_length=280)
    supporting_evidence: list[str] = Field(default_factory=list, max_length=3)
    uncertainty: list[str] = Field(default_factory=list, max_length=3)
    observer_mode: Literal["none", "fictional_alex"]

    @model_validator(mode="after")
    def validate_cards(self) -> "PerspectiveAlternativesRequest":
        if any(not card or len(card) > 180 for card in self.supporting_evidence + self.uncertainty):
            raise ValueError("evidence cards must contain 1 to 180 characters")
        return self


class PerspectiveAlternative(StrictModel):
    alternative: str = Field(min_length=1, max_length=240)
    factual_basis: str = Field(min_length=1, max_length=180)


class PerspectiveAlternativesOutput(StrictModel):
    alternatives: list[PerspectiveAlternative] = Field(min_length=1, max_length=2)
    limitation: Literal["Coursework prototype; not therapy or medical advice."]


class PerspectiveArtifactCreate(StrictModel):
    client_artifact_id: UUID
    session_id: UUID | None = None
    interpretation_text: str = Field(min_length=1, max_length=280)
    supporting_evidence: list[str] = Field(default_factory=list, max_length=3)
    uncertainty: list[str] = Field(default_factory=list, max_length=3)
    alternative_text: str = Field(min_length=1, max_length=240)
    alternative_source: Literal["user", "gemini", "fictional_example"]
    observer_mode: Literal["none", "fictional_alex"]

    @model_validator(mode="after")
    def validate_cards(self) -> "PerspectiveArtifactCreate":
        if any(not card or len(card) > 180 for card in self.supporting_evidence + self.uncertainty):
            raise ValueError("evidence cards must contain 1 to 180 characters")
        return self


class NextStepSeedCreate(StrictModel):
    client_seed_id: UUID
    session_id: UUID | None = None
    situation_text: str = Field(min_length=1, max_length=180)
    action_text: str = Field(min_length=1, max_length=180)
    formatted_plan: str = Field(min_length=1, max_length=400)
    source: Literal["user", "template", "gemini_format"]


class ConversationCreate(StrictModel):
    client_conversation_id: UUID
    purpose: Literal["history_guide"] = "history_guide"


class HistoryMessageCreate(StrictModel):
    idempotency_key: UUID
    question: str = Field(min_length=1, max_length=300)


class HistoryRunRequest(StrictModel):
    request_id: UUID


class HistoryQueryProposal(StrictModel):
    outcome: Literal["query", "out_of_scope"]
    intent: str = Field(min_length=1, max_length=180)
    sql: str | None = Field(default=None, max_length=2000)
    parameters: dict[str, str | int] = Field(default_factory=dict, max_length=6)

    @model_validator(mode="after")
    def validate_shape(self) -> "HistoryQueryProposal":
        if self.outcome == "query" and not self.sql:
            raise ValueError("query outcome requires SQL")
        if self.outcome == "out_of_scope" and (self.sql is not None or self.parameters):
            raise ValueError("out-of-scope outcome cannot include SQL")
        if any(not re.fullmatch(r"[a-z][a-z0-9_]{0,30}", key) for key in self.parameters):
            raise ValueError("invalid parameter name")
        if any(isinstance(value, str) and len(value) > 120 for value in self.parameters.values()):
            raise ValueError("parameter value is too long")
        return self


class GroundedHistoryAnswer(StrictModel):
    answer: str = Field(min_length=1, max_length=600)
    row_references: list[int] = Field(min_length=1, max_length=20)
    limitation: Literal["Coursework prototype; factual saved records only."]


class SavedTextDeleteRequest(StrictModel):
    confirmation: Literal["DELETE SAVED FOCUSBLOOM TEXT"]


class DemoResetRequest(StrictModel):
    confirmation: Literal["RESET FICTIONAL FOCUSBLOOM DATA"]
    expected_reset_version: int = Field(ge=0)
    idempotency_key: UUID
