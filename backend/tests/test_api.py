"""Preference, deterministic session, history, and reset API tests."""

import sqlite3
from uuid import uuid4

from conftest import create_conversation, start_payload


def new_id() -> str:
    return str(uuid4())


def test_preference_read_update_duplicate_and_reset(harness_factory) -> None:
    harness = harness_factory()
    initial = harness.request("GET", "/api/preferences").json()["preferences"]
    assert (initial["motion_mode"], initial["guidance_level"], initial["version"]) == (
        "gentle",
        "standard",
        1,
    )
    request_id = new_id()
    payload = {
        "motion_mode": "none",
        "guidance_level": "minimal",
        "expected_version": 1,
        "idempotency_key": request_id,
    }
    changed = harness.request("PUT", "/api/preferences", json=payload)
    duplicate = harness.request("PUT", "/api/preferences", json=payload)
    assert changed.json()["preferences"]["version"] == 2
    assert duplicate.json()["outcome"] == "duplicate_request"

    reset_key = new_id()
    reset_payload = {
        "confirmation": "RESET FICTIONAL BREATHBLOOM DATA",
        "expected_reset_version": 0,
        "idempotency_key": reset_key,
    }
    reset = harness.request("POST", "/api/demo/reset", json=reset_payload)
    repeated = harness.request("POST", "/api/demo/reset", json=reset_payload)
    assert reset.json()["reset_version"] == 1
    assert repeated.json()["outcome"] == "duplicate_request"
    restored = harness.request("GET", "/api/preferences").json()["preferences"]
    assert (restored["motion_mode"], restored["guidance_level"], restored["source"]) == (
        "gentle",
        "standard",
        "reset",
    )


def test_session_start_stop_history_and_idempotency(harness_factory) -> None:
    harness = harness_factory()
    client_id, request_id = new_id(), new_id()
    payload = start_payload(client_id, request_id)
    started = harness.request("POST", "/api/sessions", json=payload)
    repeated = harness.request("POST", "/api/sessions", json=payload)
    assert started.status_code == 201
    assert repeated.status_code == 200
    assert repeated.json()["outcome"] == "duplicate_request"
    session_id = started.json()["session"]["session_id"]

    action_id = new_id()
    stop = {
        "action": "stop",
        "expected_version": 1,
        "idempotency_key": action_id,
        "observed_active_duration_ms": 15500,
        "paused_duration_ms": 0,
        "wall_clock_duration_ms": 15500,
        "completed_cycles": 1,
        "ending_phase": "exhale",
        "phase_elapsed_ms": 1500,
        "ended_at": "2026-10-27T16:00:15.500Z",
    }
    stopped = harness.request("PATCH", f"/api/sessions/{session_id}", json=stop)
    duplicate_stop = harness.request("PATCH", f"/api/sessions/{session_id}", json=stop)
    assert stopped.json()["session"]["status"] == "stopped"
    assert duplicate_stop.json()["outcome"] == "duplicate_request"
    assert len(harness.request("GET", "/api/sessions").json()["sessions"]) == 1
    assert harness.request("GET", f"/api/sessions/{session_id}").json()["session"]["status"] == "stopped"

    setup = harness.request(
        "PATCH",
        f"/api/sessions/{session_id}",
        json={
            "action": "save_next_time_setup",
            "expected_version": 2,
            "idempotency_key": new_id(),
            "next_time_setup": "change_motion",
        },
    )
    assert setup.json()["session"]["next_time_setup"] == "change_motion"


def test_completion_requires_exact_deterministic_boundary(harness_factory) -> None:
    harness = harness_factory()
    started = harness.request(
        "POST", "/api/sessions", json=start_payload(new_id(), new_id())
    ).json()["session"]
    session_id = started["session_id"]
    invalid = {
        "action": "complete",
        "expected_version": 1,
        "idempotency_key": new_id(),
        "observed_active_duration_ms": 59000,
        "paused_duration_ms": 0,
        "wall_clock_duration_ms": 59000,
        "completed_cycles": 5,
        "ending_phase": "exhale",
        "phase_elapsed_ms": 5000,
        "ended_at": "2026-10-27T16:00:59.000Z",
    }
    rejected = harness.request("PATCH", f"/api/sessions/{session_id}", json=invalid)
    assert rejected.status_code == 409
    assert harness.request("GET", f"/api/sessions/{session_id}").json()["session"]["version"] == 1

    valid = dict(invalid)
    valid.update(
        idempotency_key=new_id(),
        observed_active_duration_ms=60000,
        wall_clock_duration_ms=60000,
        completed_cycles=6,
        phase_elapsed_ms=6000,
        ended_at="2026-10-27T16:01:00.000Z",
    )
    completed = harness.request("PATCH", f"/api/sessions/{session_id}", json=valid)
    assert completed.status_code == 200
    assert completed.json()["session"]["status"] == "completed"


def test_invalid_transition_and_timing_do_not_mutate(harness_factory) -> None:
    harness = harness_factory()
    session = harness.request(
        "POST", "/api/sessions", json=start_payload(new_id(), new_id())
    ).json()["session"]
    pause = {
        "action": "pause",
        "expected_version": 1,
        "idempotency_key": new_id(),
        "observed_active_duration_ms": 4000,
        "paused_duration_ms": 100,
        "wall_clock_duration_ms": 4000,
        "completed_cycles": 0,
        "ending_phase": "exhale",
        "phase_elapsed_ms": 0,
    }
    response = harness.request("PATCH", f"/api/sessions/{session['session_id']}", json=pause)
    assert response.status_code == 409
    unchanged = harness.request("GET", f"/api/sessions/{session['session_id']}").json()["session"]
    assert (unchanged["status"], unchanged["version"]) == ("active", 1)


def test_sessions_persist_across_application_lifespans(harness_factory) -> None:
    harness = harness_factory()
    created = harness.request(
        "POST", "/api/sessions", json=start_payload(new_id(), new_id())
    ).json()["session"]
    # Harness requests enter a fresh application lifespan, exercising safe reopen.
    loaded = harness.request("GET", f"/api/sessions/{created['session_id']}")
    assert loaded.json()["session"]["session_id"] == created["session_id"]


def test_reset_removes_only_fixed_profile_children_and_preserves_schema(harness_factory) -> None:
    harness = harness_factory()
    harness.request("POST", "/api/sessions", json=start_payload(new_id(), new_id()))
    conversation_id = create_conversation(harness, new_id())
    model_response = harness.request(
        "POST",
        f"/api/conversations/{conversation_id}/messages",
        json={"request_kind": "introduction", "idempotency_key": new_id()},
    )
    assert model_response.status_code == 201
    reset = harness.request(
        "POST",
        "/api/demo/reset",
        json={
            "confirmation": "RESET FICTIONAL BREATHBLOOM DATA",
            "expected_reset_version": 0,
            "idempotency_key": new_id(),
        },
    )
    assert reset.json()["deleted"]["sessions"] == 1
    assert reset.json()["deleted"]["conversations"] == 1
    assert reset.json()["deleted"]["messages"] == 2
    assert harness.request("GET", "/api/sessions").json()["sessions"] == []
    assert harness.request(
        "GET", f"/api/conversations/{conversation_id}/messages"
    ).status_code == 404
    with sqlite3.connect(harness.database_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM demo_profiles").fetchone()[0] == 1


def test_unknown_fields_return_sanitized_contract_error(harness_factory) -> None:
    harness = harness_factory()
    response = harness.request(
        "POST", "/api/sessions", json={**start_payload(new_id(), new_id()), "diagnosis": "none"}
    )
    assert response.status_code == 422
    assert response.json() == {
        "outcome": "invalid_request",
        "message": "The request did not match the documented BreathBloom API contract.",
    }
    assert "diagnosis" not in response.text

    bad_timestamp = start_payload(new_id(), new_id())
    bad_timestamp["started_at"] = "2026-10-27T16:00:00.0Z"
    timestamp_response = harness.request("POST", "/api/sessions", json=bad_timestamp)
    assert timestamp_response.status_code == 422
    assert timestamp_response.json()["outcome"] == "invalid_request"
