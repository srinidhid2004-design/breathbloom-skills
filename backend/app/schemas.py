"""Strict legacy version-1 API contracts under FocusBloom branding."""

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def validate_utc_timestamp(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("timestamp must be text")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", value) is None:
        raise ValueError("timestamp must use UTC ISO 8601 milliseconds")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise ValueError("timestamp must use UTC ISO 8601 milliseconds") from exc
    parsed = parsed.replace(tzinfo=timezone.utc)
    if parsed.year < 2000 or parsed.year > 2100:
        raise ValueError("timestamp outside supported coursework range")
    return value


UtcTimestamp = Annotated[str, BeforeValidator(validate_utc_timestamp)]


class MotionMode(str, Enum):
    FULL = "full"
    GENTLE = "gentle"
    NONE = "none"


class GuidanceLevel(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    MORE = "more"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"
    INTERRUPTED = "interrupted"


class EndingPhase(str, Enum):
    SETUP = "setup"
    READY = "ready"
    INHALE = "inhale"
    EXHALE = "exhale"


class NextTimeSetup(str, Enum):
    USE_THIS_SETUP = "use_this_setup"
    CHANGE_MOTION = "change_motion"
    CHANGE_GUIDANCE = "change_guidance"
    NO_PREFERENCE = "no_preference"


class RequestKind(str, Enum):
    INTRODUCTION = "introduction"
    REFLECTION = "reflection"
    HISTORY_SUMMARY = "history_summary"


class PreferenceUpdate(StrictModel):
    motion_mode: MotionMode
    guidance_level: GuidanceLevel
    expected_version: int = Field(ge=1)
    idempotency_key: UUID


class SessionStart(StrictModel):
    client_session_id: UUID
    idempotency_key: UUID
    started_at: UtcTimestamp
    planned_duration_ms: Literal[60_000]
    motion_mode: MotionMode
    guidance_level: GuidanceLevel


class SessionSnapshotAction(StrictModel):
    expected_version: int = Field(ge=1)
    idempotency_key: UUID
    observed_active_duration_ms: int = Field(ge=0, le=62_000)
    paused_duration_ms: int = Field(ge=0, le=86_400_000)
    wall_clock_duration_ms: int = Field(ge=0, le=86_400_000)
    completed_cycles: int = Field(ge=0, le=6)
    ending_phase: EndingPhase
    phase_elapsed_ms: int = Field(ge=0, le=8_000)


class PauseAction(SessionSnapshotAction):
    action: Literal["pause"]


class ResumeAction(SessionSnapshotAction):
    action: Literal["resume"]


class StopAction(SessionSnapshotAction):
    action: Literal["stop"]
    ended_at: UtcTimestamp


class CompleteAction(SessionSnapshotAction):
    action: Literal["complete"]
    ended_at: UtcTimestamp


class InterruptAction(SessionSnapshotAction):
    action: Literal["interrupt"]
    ended_at: UtcTimestamp


class SaveNextTimeSetupAction(StrictModel):
    action: Literal["save_next_time_setup"]
    expected_version: int = Field(ge=1)
    idempotency_key: UUID
    next_time_setup: NextTimeSetup


SessionAction = Annotated[
    PauseAction
    | ResumeAction
    | StopAction
    | CompleteAction
    | InterruptAction
    | SaveNextTimeSetupAction,
    Field(discriminator="action"),
]


class ConversationCreate(StrictModel):
    client_conversation_id: UUID
    session_id: UUID | None = None


class ModelActionRequest(StrictModel):
    request_kind: RequestKind
    session_id: UUID | None = None
    reflection_choice: NextTimeSetup | None = None
    idempotency_key: UUID

    @model_validator(mode="after")
    def validate_kind_fields(self) -> "ModelActionRequest":
        if self.request_kind is RequestKind.REFLECTION:
            if self.session_id is None or self.reflection_choice is None:
                raise ValueError("reflection requires session and choice")
        elif self.session_id is not None or self.reflection_choice is not None:
            raise ValueError("only reflection accepts session and choice")
        return self


class DemoResetRequest(StrictModel):
    confirmation: Literal["RESET FICTIONAL FOCUSBLOOM DATA"]
    expected_reset_version: int = Field(ge=0)
    idempotency_key: UUID


class ProviderPayload(StrictModel):
    response_text: str = Field(min_length=1, max_length=600)
    response_kind: RequestKind
    limitation: Literal["Coursework prototype; not therapy or medical advice."]
