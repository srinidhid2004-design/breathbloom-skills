"""Mocked one-request Perspective workflow and explicit-save boundary tests."""

from uuid import uuid4

from app.gemini import ProviderProblem


def perspective_payload(key: str | None = None) -> dict:
    return {
        "idempotency_key": key or str(uuid4()),
        "interpretation": "The fictional result must have only one explanation.",
        "supporting_evidence": ["One fictional attempt was incomplete."],
        "uncertainty": ["Other possible explanations were not checked."],
        "observer_mode": "fictional_alex",
    }


def test_success_uses_one_call_and_does_not_save_artifact(harness_factory) -> None:
    harness = harness_factory()
    response = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload())
    assert response.status_code == 200
    assert response.json()["saved"] is False
    assert len(response.json()["alternatives"]["alternatives"]) == 1
    assert [call[0] for call in harness.gateway.calls] == ["perspective"]
    assert harness.request("GET", "/api/perspective-artifacts").json()["artifacts"] == []


def test_missing_configuration_uses_zero_calls(harness_factory) -> None:
    harness = harness_factory(configured=False)
    response = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload())
    assert response.status_code == 503
    assert response.json()["outcome"] == "missing_configuration"
    assert harness.gateway.calls == []


def test_duplicate_request_never_calls_provider_twice(harness_factory) -> None:
    harness = harness_factory()
    key = str(uuid4())
    assert harness.request("POST", "/api/perspective/alternatives", json=perspective_payload(key)).status_code == 200
    repeated = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload(key))
    assert repeated.json()["outcome"] == "duplicate_request"
    assert len(harness.gateway.calls) == 1


def test_provider_failure_has_one_call_and_sanitized_response(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.perspective_error = ProviderProblem("provider_failure")
    response = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload())
    assert response.status_code == 502
    assert len(harness.gateway.calls) == 1
    assert "provider_failure" not in response.text


def test_malformed_or_unsafe_output_is_rejected(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.perspective_result = {
        "alternatives": [{"alternative": "This will improve your mental health.", "factual_basis": "Claim."}],
        "limitation": "Coursework prototype; not therapy or medical advice.",
    }
    response = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload())
    assert response.status_code == 502
    assert len(harness.gateway.calls) == 1


def test_more_than_two_generated_alternatives_is_rejected(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.perspective_result = {
        "alternatives": [
            {"alternative": f"Bounded alternative {index}.", "factual_basis": "Only supplied facts are used."}
            for index in range(3)
        ],
        "limitation": "Coursework prototype; not therapy or medical advice.",
    }
    response = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload())
    assert response.status_code == 502
    assert len(harness.gateway.calls) == 1


def test_generated_advice_is_rejected(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.perspective_result = {
        "alternatives": [{
            "alternative": "You should take action on the fictional assignment.",
            "factual_basis": "One fictional card was supplied.",
        }],
        "limitation": "Coursework prototype; not therapy or medical advice.",
    }
    response = harness.request("POST", "/api/perspective/alternatives", json=perspective_payload())
    assert response.status_code == 502
    assert len(harness.gateway.calls) == 1


def test_invalid_input_uses_zero_calls_and_does_not_echo(harness_factory) -> None:
    harness = harness_factory()
    payload = perspective_payload()
    payload["interpretation"] = "private-value" * 40
    response = harness.request("POST", "/api/perspective/alternatives", json=payload)
    assert response.status_code == 422
    assert harness.gateway.calls == []
    assert "private-value" not in response.text
