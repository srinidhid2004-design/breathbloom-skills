"""Credential-free test harness for the FocusBloom version-2 backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import Settings
from app.main import create_app
from app.schemas import (
    GroundedHistoryAnswer, HistoryQueryProposal, PerspectiveAlternative,
    PerspectiveAlternativesOutput,
)


class FakeGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.perspective_result: Any = PerspectiveAlternativesOutput(
            alternatives=[PerspectiveAlternative(
                alternative="The visible facts could support more than one interpretation.",
                factual_basis="The provided cards do not establish only one explanation.",
            )],
            limitation="Coursework prototype; not therapy or medical advice.",
        )
        self.query_result: Any = HistoryQueryProposal(
            outcome="query", intent="List recent fictional activity records.",
            sql=(
                "SELECT session_id, activity_type, status, duration_ms "
                "FROM activity_sessions WHERE profile_id = :profile_id "
                "ORDER BY started_at DESC LIMIT 20"
            ), parameters={},
        )
        self.answer_result: Any = GroundedHistoryAnswer(
            answer="Row 1 records one fictional activity session.",
            row_references=[1],
            limitation="Coursework prototype; factual saved records only.",
        )
        self.perspective_error: Exception | None = None
        self.query_error: Exception | None = None
        self.answer_error: Exception | None = None

    def perspective(self, context: dict[str, Any]) -> Any:
        self.calls.append(("perspective", context))
        if self.perspective_error:
            raise self.perspective_error
        return self.perspective_result

    def propose_history_query(self, question: str) -> Any:
        self.calls.append(("history_sql", question))
        if self.query_error:
            raise self.query_error
        return self.query_result

    def answer_history(self, context: dict[str, Any]) -> Any:
        self.calls.append(("history_answer", context))
        if self.answer_error:
            raise self.answer_error
        return self.answer_result


@dataclass
class Harness:
    app: Any
    database_path: Path
    gateway: FakeGateway

    def request(self, method: str, path: str, **kwargs: Any):
        with TestClient(self.app, raise_server_exceptions=False) as client:
            return client.request(method, path, **kwargs)


@pytest.fixture
def harness_factory(tmp_path: Path):
    serial = 0

    def build(*, configured: bool = True, gateway: FakeGateway | None = None) -> Harness:
        nonlocal serial
        serial += 1
        database_path = tmp_path / f"focusbloom-{serial}.sqlite3"
        selected = gateway or FakeGateway()
        settings = Settings(
            _env_file=None, database_path=database_path,
            gemini_api_key=SecretStr("fictional-test-key") if configured else None,
        )
        return Harness(create_app(settings=settings, gateway=selected), database_path, selected)

    return build


def session_payload(*, client_id: str | None = None, activity_type: str = "different_leaf") -> dict[str, Any]:
    return {
        "client_session_id": client_id or str(uuid4()), "activity_type": activity_type,
        "started_at": "2026-10-28T14:00:00.000Z", "difficulty": "standard",
        "motion_mode": "standard", "guidance_level": "standard",
    }


def create_session(harness: Harness, *, activity_type: str = "different_leaf") -> dict[str, Any]:
    response = harness.request("POST", "/api/activity-sessions", json=session_payload(activity_type=activity_type))
    assert response.status_code == 201, response.text
    return response.json()["session"]


def create_conversation(harness: Harness) -> str:
    response = harness.request(
        "POST", "/api/conversations",
        json={"client_conversation_id": str(uuid4()), "purpose": "history_guide"},
    )
    assert response.status_code == 201, response.text
    return response.json()["conversation"]["conversation_id"]


def create_history_request(harness: Harness, conversation_id: str) -> str:
    response = harness.request(
        "POST", f"/api/conversations/{conversation_id}/messages",
        json={"idempotency_key": str(uuid4()), "question": "Which fictional activities are saved?"},
    )
    assert response.status_code == 201, response.text
    return response.json()["request"]["request_id"]
