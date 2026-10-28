"""Credential-free test harness for the legacy backend under FocusBloom branding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import Settings
from app.main import create_app
from app.schemas import ProviderPayload, RequestKind


class FakeGateway:
    def __init__(self, result: Any | None = None, error: Exception | None = None) -> None:
        self.result = result or ProviderPayload(
            response_text="This fictional coursework activity uses application-owned steps.",
            response_kind=RequestKind.INTRODUCTION,
            limitation="Coursework prototype; not therapy or medical advice.",
        )
        self.error = error
        self.calls: list[tuple[str, RequestKind]] = []

    def generate(self, context: str, expected_kind: RequestKind) -> Any:
        self.calls.append((context, expected_kind))
        if self.error is not None:
            raise self.error
        return self.result


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
        database_path = tmp_path / f"case-{serial}.sqlite3"
        selected_gateway = gateway or FakeGateway()
        settings = Settings(
            _env_file=None,
            database_path=database_path,
            gemini_api_key=SecretStr("fictional-test-key") if configured else None,
        )
        return Harness(create_app(settings=settings, gateway=selected_gateway), database_path, selected_gateway)

    return build


def start_payload(client_id: str, request_id: str) -> dict[str, Any]:
    return {
        "client_session_id": client_id,
        "idempotency_key": request_id,
        "started_at": "2026-10-27T16:00:00.000Z",
        "planned_duration_ms": 60000,
        "motion_mode": "gentle",
        "guidance_level": "standard",
    }


def create_conversation(harness: Harness, client_id: str) -> str:
    response = harness.request(
        "POST", "/api/conversations", json={"client_conversation_id": client_id}
    )
    assert response.status_code == 201
    return response.json()["conversation"]["conversation_id"]
