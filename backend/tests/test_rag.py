"""Adversarial SQL validation, read-only execution, grounding, and call counts."""

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from app.database import DEMO_PROFILE_ID, Repository
from app.gemini import ProviderProblem
from app.rag import QueryRejected, execute_read_only, validate_query
from app.schemas import GroundedHistoryAnswer, HistoryQueryProposal
from conftest import create_conversation, create_history_request, create_session


SAFE_SQL = (
    "SELECT session_id, activity_type, status, duration_ms FROM activity_sessions "
    "WHERE profile_id = :profile_id ORDER BY started_at DESC LIMIT 20"
)


def test_validator_accepts_one_scoped_bounded_select() -> None:
    query = validate_query(SAFE_SQL, {})
    assert query.table == "activity_sessions"
    assert query.parameters == {"profile_id": DEMO_PROFILE_ID}
    assert len(query.columns) == 4


@pytest.mark.parametrize("sql", [
    "WITH x AS (SELECT * FROM activity_sessions) SELECT * FROM x LIMIT 20",
    "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id LIMIT 20; DELETE FROM activity_sessions",
    "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id -- comment\n LIMIT 20",
    "SELECT name FROM sqlite_master WHERE name=:profile_id LIMIT 20",
    "SELECT session_id FROM activity_sessions WHERE profile_id='focusbloom-fictional-demo' LIMIT 20",
    "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id",
    "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id LIMIT 21",
    "SELECT session_id FROM activity_sessions JOIN preferences USING(profile_id) WHERE profile_id=:profile_id LIMIT 20",
    "SELECT load_extension(:value) FROM activity_sessions WHERE profile_id=:profile_id LIMIT 20",
    "PRAGMA table_info(activity_sessions)",
])
def test_validator_rejects_adversarial_sql(sql: str) -> None:
    with pytest.raises(QueryRejected):
        validate_query(sql, {"value": "x"} if ":value" in sql else {})


def test_validator_requires_exact_bound_parameter_set() -> None:
    sql = (
        "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id "
        "AND status=:status LIMIT 20"
    )
    assert validate_query(sql, {"status": "completed"}).parameters["status"] == "completed"
    with pytest.raises(QueryRejected):
        validate_query(sql, {})
    with pytest.raises(QueryRejected):
        validate_query(SAFE_SQL, {"unused": "x"})


def test_read_only_executor_returns_bounded_rows_without_mutation(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "rag.sqlite3")
    repository.initialize()
    repository.create_session({
        "client_session_id": str(uuid4()), "activity_type": "different_leaf",
        "started_at": "2026-10-28T14:00:00.000Z", "difficulty": "standard",
        "motion_mode": "standard", "guidance_level": "standard",
    })
    result = execute_read_only(repository.database_path, validate_query(SAFE_SQL, {}))
    assert result.columns == ("session_id", "activity_type", "status", "duration_ms")
    assert result.rows[0][1:] == ("different_leaf", "active", 0)
    with repository.connect(read_only=True) as connection:
        assert connection.execute("SELECT COUNT(*) FROM activity_sessions").fetchone()[0] == 1


def test_sqlite_authorizer_denies_unvalidated_schema_read(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "authorizer.sqlite3")
    repository.initialize()
    valid = validate_query(SAFE_SQL, {})
    object.__setattr__(valid, "sql", "SELECT name FROM sqlite_master WHERE name=:profile_id LIMIT 20")
    with pytest.raises(Exception):
        execute_read_only(repository.database_path, valid)


def test_history_success_uses_exactly_two_calls_and_persists_grounded_answer(harness_factory) -> None:
    harness = harness_factory()
    create_session(harness)
    conversation_id = create_conversation(harness)
    request_id = create_history_request(harness, conversation_id)
    response = harness.request(
        "POST", "/api/garden-guide/history-questions", json={"request_id": request_id}
    )
    assert response.status_code == 200
    assert response.json()["outcome"] == "success"
    assert response.json()["row_references"] == [1]
    assert [call[0] for call in harness.gateway.calls] == ["history_sql", "history_answer"]
    messages = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant"]


def test_history_no_match_uses_one_call_and_creates_no_answer(harness_factory) -> None:
    harness = harness_factory()
    conversation_id = create_conversation(harness)
    request_id = create_history_request(harness, conversation_id)
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 200
    assert response.json()["outcome"] == "history_no_match"
    assert [call[0] for call in harness.gateway.calls] == ["history_sql"]
    assert len(harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]) == 1


def test_rejected_query_uses_one_call_and_never_executes_mutation(harness_factory) -> None:
    harness = harness_factory()
    create_session(harness)
    harness.gateway.query_result = HistoryQueryProposal(
        outcome="query", intent="Unapproved mutation.",
        sql="DELETE FROM activity_sessions WHERE profile_id=:profile_id LIMIT 20", parameters={},
    )
    conversation_id = create_conversation(harness)
    request_id = create_history_request(harness, conversation_id)
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 422
    assert response.json()["outcome"] == "history_query_rejected"
    assert [call[0] for call in harness.gateway.calls] == ["history_sql"]
    assert len(harness.request("GET", "/api/activity-sessions").json()["sessions"]) == 1


def test_out_of_scope_uses_one_call(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.query_result = HistoryQueryProposal(
        outcome="out_of_scope", intent="This is not a saved-record question.", sql=None, parameters={}
    )
    request_id = create_history_request(harness, create_conversation(harness))
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 422
    assert len(harness.gateway.calls) == 1


def test_missing_configuration_uses_zero_calls(harness_factory) -> None:
    harness = harness_factory(configured=False)
    request_id = create_history_request(harness, create_conversation(harness))
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 503
    assert harness.gateway.calls == []


def test_invalid_grounding_uses_two_calls_and_stores_no_assistant(harness_factory) -> None:
    harness = harness_factory()
    create_session(harness)
    harness.gateway.answer_result = GroundedHistoryAnswer(
        answer="A non-retrieved row says something else.", row_references=[2],
        limitation="Coursework prototype; factual saved records only.",
    )
    conversation_id = create_conversation(harness)
    request_id = create_history_request(harness, conversation_id)
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 502
    assert len(harness.gateway.calls) == 2
    messages = harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"]
    assert [message["role"] for message in messages] == ["user"]


def test_second_provider_failure_uses_two_calls_without_retry(harness_factory) -> None:
    harness = harness_factory()
    create_session(harness)
    harness.gateway.answer_error = ProviderProblem("timeout", 504)
    request_id = create_history_request(harness, create_conversation(harness))
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 504
    assert [call[0] for call in harness.gateway.calls] == ["history_sql", "history_answer"]


def test_invalid_question_uses_zero_calls_and_is_not_stored(harness_factory) -> None:
    harness = harness_factory()
    conversation_id = create_conversation(harness)
    response = harness.request(
        "POST", f"/api/conversations/{conversation_id}/messages",
        json={"idempotency_key": str(uuid4()), "question": "x" * 301},
    )
    assert response.status_code == 422
    assert harness.gateway.calls == []
    assert harness.request("GET", f"/api/conversations/{conversation_id}/messages").json()["messages"] == []


def test_request_one_provider_failure_is_sanitized_and_one_call(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.query_error = ProviderProblem("provider_failure")
    request_id = create_history_request(harness, create_conversation(harness))
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 502
    assert len(harness.gateway.calls) == 1
    assert "provider_failure" not in response.text


def test_malformed_query_proposal_uses_one_call(harness_factory) -> None:
    harness = harness_factory()
    harness.gateway.query_result = {"outcome": "query", "unexpected": "field"}
    request_id = create_history_request(harness, create_conversation(harness))
    response = harness.request("POST", "/api/garden-guide/history-questions", json={"request_id": request_id})
    assert response.status_code == 502
    assert [call[0] for call in harness.gateway.calls] == ["history_sql"]


def test_completed_history_request_is_not_run_twice(harness_factory) -> None:
    harness = harness_factory()
    create_session(harness)
    request_id = create_history_request(harness, create_conversation(harness))
    assert harness.request(
        "POST", "/api/garden-guide/history-questions", json={"request_id": request_id}
    ).status_code == 200
    repeated = harness.request(
        "POST", "/api/garden-guide/history-questions", json={"request_id": request_id}
    )
    assert repeated.json()["outcome"] == "duplicate_request"
    assert len(harness.gateway.calls) == 2
