"""Exact route surface and deterministic activity/persistence API tests."""

from pathlib import Path
from uuid import uuid4

from pydantic import SecretStr

from app.config import Settings
from app.main import create_app
from conftest import create_session, session_payload


EXPECTED_OPERATIONS = {
    ("GET", "/api/health"), ("GET", "/api/preferences"), ("PUT", "/api/preferences"),
    ("GET", "/api/focus-activities"), ("POST", "/api/activity-sessions"),
    ("PATCH", "/api/activity-sessions/{session_id}"),
    ("POST", "/api/activity-sessions/{session_id}/events"),
    ("GET", "/api/activity-sessions"), ("GET", "/api/activity-sessions/{session_id}"),
    ("POST", "/api/perspective/alternatives"), ("POST", "/api/perspective-artifacts"),
    ("GET", "/api/perspective-artifacts"),
    ("DELETE", "/api/perspective-artifacts/{artifact_id}"),
    ("POST", "/api/next-step-seeds"), ("GET", "/api/next-step-seeds"),
    ("DELETE", "/api/next-step-seeds/{seed_id}"), ("POST", "/api/conversations"),
    ("GET", "/api/conversations/{conversation_id}/messages"),
    ("POST", "/api/conversations/{conversation_id}/messages"),
    ("POST", "/api/garden-guide/history-questions"), ("DELETE", "/api/demo/saved-text"),
    ("POST", "/api/demo/reset"),
}


def test_exact_twenty_two_operations(harness_factory) -> None:
    schema = harness_factory().app.openapi()
    operations = {
        (method.upper(), path) for path, methods in schema["paths"].items()
        for method in methods if method.lower() in {"get", "put", "post", "patch", "delete"}
    }
    assert operations == EXPECTED_OPERATIONS
    assert len(operations) == 22


def test_app_construction_has_no_database_side_effect(tmp_path: Path) -> None:
    path = tmp_path / "not-created.sqlite3"
    app = create_app(Settings(_env_file=None, database_path=path, gemini_api_key=SecretStr("fake")))
    assert not path.exists()
    assert not hasattr(app.state, "service")


def test_health_is_sanitized_and_reports_version_two(harness_factory) -> None:
    harness = harness_factory()
    response = harness.request("GET", "/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "service": "ok", "schema_version": 2, "database": "available",
        "gemini_api_key": "configured",
    }
    assert "fictional-test-key" not in response.text
    assert str(harness.database_path) not in response.text


def test_catalog_has_seven_no_typing_focus_activities(harness_factory) -> None:
    body = harness_factory().request("GET", "/api/focus-activities").json()
    assert len(body["activities"]) == 7
    assert body["controls"] == ["Show me", "Skip this", "Stop", "Support"]
    assert all(item["activity_type"] != "perspective_studio" for item in body["activities"])


def test_activity_session_event_and_terminal_flow(harness_factory) -> None:
    harness = harness_factory()
    session = create_session(harness)
    event = harness.request(
        "POST", f"/api/activity-sessions/{session['session_id']}/events",
        json={
            "client_event_id": str(uuid4()), "ordinal": 0, "event_type": "started",
            "happened_at": "2026-10-28T14:00:00.000Z", "elapsed_ms": 0, "payload": {},
        },
    )
    assert event.status_code == 201
    completed = harness.request(
        "PATCH", f"/api/activity-sessions/{session['session_id']}",
        json={
            "action": "complete", "expected_version": 1, "idempotency_key": str(uuid4()),
            "ended_at": "2026-10-28T14:00:30.000Z", "duration_ms": 30000,
            "perspective_progress": "none", "model_status": "skipped",
        },
    )
    assert completed.status_code == 200
    assert completed.json()["session"]["status"] == "completed"
    detail = harness.request("GET", f"/api/activity-sessions/{session['session_id']}").json()
    assert detail["events"][0]["event_type"] == "started"
    assert harness.request("GET", "/api/activity-sessions?status=completed").json()["sessions"][0]["duration_ms"] == 30000


def test_session_creation_is_idempotent_and_conflicts_on_changed_input(harness_factory) -> None:
    harness = harness_factory()
    client_id = str(uuid4())
    payload = session_payload(client_id=client_id)
    first = harness.request("POST", "/api/activity-sessions", json=payload)
    repeated = harness.request("POST", "/api/activity-sessions", json=payload)
    changed = {**payload, "difficulty": "challenge"}
    conflict = harness.request("POST", "/api/activity-sessions", json=changed)
    assert first.status_code == 201
    assert repeated.status_code == 200 and repeated.json()["outcome"] == "duplicate_request"
    assert conflict.status_code == 409


def test_preference_update_rejects_extra_fields_without_echo(harness_factory) -> None:
    harness = harness_factory()
    response = harness.request("PUT", "/api/preferences", json={
        "motion_mode": "standard", "guidance_level": "more", "difficulty": "easy",
        "remember_preferences": True, "expected_version": 1,
        "idempotency_key": str(uuid4()), "private_note": "do-not-echo",
    })
    assert response.status_code == 422
    assert "do-not-echo" not in response.text


def test_preference_update_is_versioned_and_idempotent(harness_factory) -> None:
    harness = harness_factory()
    key = str(uuid4())
    payload = {
        "motion_mode": "no_motion", "guidance_level": "minimal", "difficulty": "easy",
        "remember_preferences": True, "expected_version": 1, "idempotency_key": key,
    }
    first = harness.request("PUT", "/api/preferences", json=payload)
    repeated = harness.request("PUT", "/api/preferences", json=payload)
    assert first.json()["preferences"]["version"] == 2
    assert repeated.json()["outcome"] == "duplicate_request"


def test_all_terminal_activity_states_are_recorded(harness_factory) -> None:
    harness = harness_factory()
    for action, status, duration in (
        ("stop", "stopped", 1200), ("skip", "skipped", 0), ("interrupt", "interrupted", 800)
    ):
        session = create_session(harness)
        response = harness.request(
            "PATCH", f"/api/activity-sessions/{session['session_id']}",
            json={
                "action": action, "expected_version": 1, "idempotency_key": str(uuid4()),
                "ended_at": "2026-10-28T14:00:02.000Z", "duration_ms": duration,
                "perspective_progress": "none", "model_status": "skipped",
            },
        )
        assert response.status_code == 200
        assert response.json()["session"]["status"] == status


def test_explicit_artifact_and_seed_save_then_delete(harness_factory) -> None:
    harness = harness_factory()
    session = create_session(harness, activity_type="perspective_studio")
    artifact_response = harness.request("POST", "/api/perspective-artifacts", json={
        "client_artifact_id": str(uuid4()), "session_id": session["session_id"],
        "interpretation_text": "The fictional assignment result has only one explanation.",
        "supporting_evidence": ["One fictional example was incomplete."],
        "uncertainty": ["Other fictional examples were not reviewed."],
        "alternative_text": "Several explanations remain possible from the available facts.",
        "alternative_source": "user", "observer_mode": "fictional_alex",
    })
    seed_response = harness.request("POST", "/api/next-step-seeds", json={
        "client_seed_id": str(uuid4()), "session_id": session["session_id"],
        "situation_text": "When the fictional worksheet is available",
        "action_text": "review the first visible instruction",
        "formatted_plan": "When the fictional worksheet is available, review the first visible instruction.",
        "source": "template",
    })
    assert artifact_response.status_code == seed_response.status_code == 201
    artifact_id = artifact_response.json()["artifact"]["artifact_id"]
    seed_id = seed_response.json()["seed"]["seed_id"]
    assert len(harness.request("GET", "/api/perspective-artifacts").json()["artifacts"]) == 1
    assert harness.request("DELETE", f"/api/perspective-artifacts/{artifact_id}").status_code == 200
    assert harness.request("DELETE", f"/api/next-step-seeds/{seed_id}").status_code == 200
    detail = harness.request("GET", f"/api/activity-sessions/{session['session_id']}").json()["session"]
    assert detail["alternative_save_state"] == detail["seed_save_state"] == "deleted"


def test_delete_saved_text_retains_session_metadata(harness_factory) -> None:
    harness = harness_factory()
    session = create_session(harness)
    response = harness.request(
        "DELETE", "/api/demo/saved-text",
        json={"confirmation": "DELETE SAVED FOCUSBLOOM TEXT"},
    )
    assert response.status_code == 200
    assert harness.request("GET", f"/api/activity-sessions/{session['session_id']}").status_code == 200


def test_obsolete_breathing_route_is_absent(harness_factory) -> None:
    response = harness_factory().request("POST", "/api/sessions", json={})
    assert response.status_code == 404


def test_complete_reset_route_removes_sessions_and_restores_defaults(harness_factory) -> None:
    harness = harness_factory()
    create_session(harness)
    response = harness.request("POST", "/api/demo/reset", json={
        "confirmation": "RESET FICTIONAL FOCUSBLOOM DATA", "expected_reset_version": 0,
        "idempotency_key": str(uuid4()),
    })
    assert response.status_code == 200
    assert response.json()["reset_version"] == 1
    assert harness.request("GET", "/api/activity-sessions").json()["sessions"] == []
    assert harness.request("GET", "/api/preferences").json()["preferences"]["version"] == 1
