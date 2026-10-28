"""Bounded Gemini boundary, lifecycle, and conversation-integrity tests."""

import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import SecretStr

import app.gemini as gemini_module
from app.config import GEMINI_MODEL, Settings
from app.database import Repository
from app.gemini import GoogleGeminiGateway, provider_problem
from app.schemas import ProviderPayload, RequestKind
from conftest import FakeGateway, create_conversation, start_payload


INVALID_MESSAGE = (
    "FocusBloom only supports the listed coursework requests. No model request was made. "
    "You can continue with the available prototype or open Support information at any time."
)


def new_id() -> str:
    return str(uuid4())


def model_payload(request_id: str, kind: str = "introduction") -> dict[str, str]:
    return {"request_kind": kind, "idempotency_key": request_id}


def test_success_uses_one_call_and_persists_ordered_validated_messages(harness_factory) -> None:
    gateway = FakeGateway()
    harness = harness_factory(gateway=gateway)
    conversation_id = create_conversation(harness, new_id())

    response = harness.request(
        "POST",
        f"/api/conversations/{conversation_id}/messages",
        json=model_payload(new_id()),
    )

    assert response.status_code == 201
    assert response.json()["outcome"] == "success"
    assert len(gateway.calls) == 1
    context = gateway.calls[0][0]
    assert len(context) <= 4096
    assert "fictional-test-key" not in context
    assert "sqlite" not in context.lower()
    messages = harness.request(
        "GET", f"/api/conversations/{conversation_id}/messages"
    ).json()["messages"]
    assert [(row["ordinal"], row["role"]) for row in messages] == [
        (0, "user"),
        (1, "assistant"),
    ]
    assert messages[0]["request_status"] == "succeeded"
    assert messages[1]["content"] == gateway.result.response_text
    assert messages[0]["message_id"] != messages[1]["message_id"]


def test_duplicate_model_submit_never_calls_provider_twice(harness_factory) -> None:
    gateway = FakeGateway()
    harness = harness_factory(gateway=gateway)
    conversation_id = create_conversation(harness, new_id())
    payload = model_payload(new_id())

    first = harness.request("POST", f"/api/conversations/{conversation_id}/messages", json=payload)
    second = harness.request("POST", f"/api/conversations/{conversation_id}/messages", json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["outcome"] == "duplicate_request"
    assert len(gateway.calls) == 1
    assert len(harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]) == 2


def test_missing_configuration_persists_failed_attempt_with_zero_calls(harness_factory) -> None:
    gateway = FakeGateway()
    harness = harness_factory(configured=False, gateway=gateway)
    conversation_id = create_conversation(harness, new_id())
    response = harness.request(
        "POST", f"/api/conversations/{conversation_id}/messages", json=model_payload(new_id())
    )

    assert response.status_code == 503
    assert response.json()["outcome"] == "missing_configuration"
    assert gateway.calls == []
    messages = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert len(messages) == 1
    assert (messages[0]["request_status"], messages[0]["safe_error_code"]) == (
        "failed",
        "missing_configuration",
    )


@pytest.mark.parametrize(
    ("outcome", "status_code"),
    [
        ("authentication_failure", 502),
        ("permission_failure", 502),
        ("quota_failure", 503),
        ("rate_limit_failure", 429),
        ("timeout", 504),
        ("provider_failure", 502),
    ],
)
def test_provider_failures_are_safe_and_persisted(harness_factory, outcome, status_code) -> None:
    gateway = FakeGateway(error=provider_problem(outcome))
    harness = harness_factory(gateway=gateway)
    conversation_id = create_conversation(harness, new_id())
    response = harness.request(
        "POST", f"/api/conversations/{conversation_id}/messages", json=model_payload(new_id())
    )

    assert response.status_code == status_code
    assert response.json()["outcome"] == outcome
    assert len(gateway.calls) == 1
    assert "exception" not in response.text.lower()
    messages = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert len(messages) == 1
    assert messages[0]["request_status"] == "failed"
    assert messages[0]["safe_error_code"] == outcome


@pytest.mark.parametrize(
    "bad_result",
    [
        {"response_text": "<script>bad</script>", "response_kind": "introduction", "limitation": "Coursework prototype; not therapy or medical advice."},
        {"response_text": "Visit https://example.test", "response_kind": "introduction", "limitation": "Coursework prototype; not therapy or medical advice."},
        {"response_text": "I can diagnose this.", "response_kind": "introduction", "limitation": "Coursework prototype; not therapy or medical advice."},
        {"response_text": "Valid", "response_kind": "introduction", "limitation": "Coursework prototype; not therapy or medical advice.", "unknown": True},
    ],
)
def test_malformed_provider_output_is_never_persisted_as_assistant(harness_factory, bad_result) -> None:
    gateway = FakeGateway(result=bad_result)
    harness = harness_factory(gateway=gateway)
    conversation_id = create_conversation(harness, new_id())
    response = harness.request(
        "POST", f"/api/conversations/{conversation_id}/messages", json=model_payload(new_id())
    )

    assert response.status_code == 502
    assert response.json()["outcome"] == "malformed_response"
    messages = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert len(messages) == 1
    assert messages[0]["safe_error_code"] == "malformed_response"
    assert str(bad_result) not in response.text


def test_structurally_invalid_free_form_input_has_zero_calls_and_zero_writes(harness_factory) -> None:
    gateway = FakeGateway()
    harness = harness_factory(gateway=gateway)
    conversation_id = create_conversation(harness, new_id())
    before = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]

    response = harness.request(
        "POST",
        f"/api/conversations/{conversation_id}/messages",
        json={"request_kind": "introduction", "message": "arbitrary free-form text", "idempotency_key": new_id()},
    )

    after = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert response.status_code == 422
    assert response.json() == {"outcome": "invalid_request", "message": INVALID_MESSAGE}
    assert gateway.calls == []
    assert before == after == []


def test_support_has_no_backend_or_model_dependency(harness_factory) -> None:
    gateway = FakeGateway()
    harness = harness_factory(gateway=gateway)
    response = harness.request("GET", "/api/support")
    assert response.status_code == 404
    assert gateway.calls == []


def test_failed_request_retry_is_idempotent_without_invented_assistant(harness_factory) -> None:
    gateway = FakeGateway(error=provider_problem("timeout"))
    harness = harness_factory(gateway=gateway)
    conversation_id = create_conversation(harness, new_id())
    request_id = new_id()
    payload = model_payload(request_id)
    first = harness.request("POST", f"/api/conversations/{conversation_id}/messages", json=payload)
    second = harness.request("POST", f"/api/conversations/{conversation_id}/messages", json=payload)

    assert first.status_code == 504
    assert second.status_code == 200
    assert second.json()["outcome"] == "duplicate_request"
    assert second.json()["assistant_message"] is None
    assert len(gateway.calls) == 1
    with pytest.raises(ValueError):
        Repository(harness.database_path).complete_request(
            request_id=request_id,
            assistant_content="A late response must not be written.",
        )
    messages = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert len(messages) == 1


def test_history_context_is_bounded_to_five_factual_sessions(harness_factory) -> None:
    result = ProviderPayload(
        response_text="Five recent fictional sessions are available for factual review.",
        response_kind=RequestKind.HISTORY_SUMMARY,
        limitation="Coursework prototype; not therapy or medical advice.",
    )
    gateway = FakeGateway(result=result)
    harness = harness_factory(gateway=gateway)
    for _ in range(6):
        harness.request("POST", "/api/sessions", json=start_payload(new_id(), new_id()))
    conversation_id = create_conversation(harness, new_id())
    response = harness.request(
        "POST",
        f"/api/conversations/{conversation_id}/messages",
        json=model_payload(new_id(), "history_summary"),
    )
    assert response.status_code == 201
    context = json.loads(gateway.calls[0][0])
    assert len(context["recent_sessions"]) == 5
    assert len(gateway.calls[0][0]) <= 4096


def test_google_gateway_is_one_attempt_fixed_model_no_fallback(monkeypatch, tmp_path) -> None:
    captured = {"generate_calls": 0}

    class Models:
        def generate_content(self, **kwargs):
            captured["generate_calls"] += 1
            captured["model"] = kwargs["model"]
            captured["config"] = kwargs["config"]
            return SimpleNamespace(
                parsed=ProviderPayload(
                    response_text="A bounded fictional introduction.",
                    response_kind=RequestKind.INTRODUCTION,
                    limitation="Coursework prototype; not therapy or medical advice.",
                )
            )

    class Client:
        def __init__(self, *, api_key, http_options):
            captured["key"] = api_key
            captured["http_options"] = http_options
            self.models = Models()

    monkeypatch.setattr(gemini_module.genai, "Client", Client)
    settings = Settings(
        _env_file=None,
        database_path=tmp_path / "unused.sqlite3",
        gemini_api_key=SecretStr("fake-sdk-key"),
    )
    result = GoogleGeminiGateway(settings).generate("{}", RequestKind.INTRODUCTION)

    assert result.response_kind is RequestKind.INTRODUCTION
    assert captured["generate_calls"] == 1
    assert captured["model"] == GEMINI_MODEL
    assert captured["http_options"].timeout == 10_000
    assert captured["http_options"].retry_options.attempts == 1
    assert captured["config"].max_output_tokens == 256
