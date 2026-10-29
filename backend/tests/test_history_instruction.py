"""Prompt 10D alignment between the history instruction and unchanged validator."""

from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from app.config import Settings
from app.gemini import GoogleGeminiGateway
from app.rag import QueryRejected, validate_query


EXAMPLE_SQL = (
    "SELECT activity_type, COUNT(*) AS session_count FROM activity_sessions "
    "WHERE profile_id = :profile_id AND status = :status GROUP BY activity_type "
    "ORDER BY session_count DESC LIMIT 20"
)


def test_history_instruction_matches_validator_and_example_is_accepted(monkeypatch) -> None:
    captured: dict = {}

    class FakeModels:
        def generate_content(self, *, model, contents, config):
            captured.update(contents=contents, config=config)
            return SimpleNamespace(parsed={
                "outcome": "query",
                "intent": "Count completed sessions by activity type.",
                "sql": EXAMPLE_SQL,
                "parameters": {"status": "completed"},
            })

    class FakeClient:
        def __init__(self, *, api_key, http_options):
            self.models = FakeModels()

    monkeypatch.setattr("app.gemini.genai.Client", FakeClient)
    proposal = GoogleGeminiGateway(
        Settings(_env_file=None, gemini_api_key=SecretStr("fictional-test-key"))
    ).propose_history_query("Which activity did I complete most often?")

    instruction = captured["contents"].split("\n\nApproved bounded context:", 1)[0]
    for required in (
        "activity_sessions", "perspective_artifacts", "next_step_seeds", "preferences",
        "profile_id = :profile_id", "never put profile_id in the parameters object",
        "COUNT, MIN, or MAX", "GROUP BY", "ORDER BY", "LIMIT from 1 through 20",
        "Do not use literal or quoted values", "CTEs", "joins", "comments", "schema access",
    ):
        assert required in instruction
    assert proposal.parameters == {"status": "completed"}
    assert "profile_id" not in proposal.parameters
    validated = validate_query(proposal.sql or "", proposal.parameters)
    assert validated.table == "activity_sessions"
    assert validated.columns == ("activity_type", "session_count")


@pytest.mark.parametrize(("sql", "parameters"), [
    (
        "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id "
        "AND status='completed' LIMIT 20",
        {},
    ),
    ("DELETE FROM activity_sessions WHERE profile_id=:profile_id LIMIT 20", {}),
    (
        "SELECT activity_sessions.session_id FROM activity_sessions JOIN preferences "
        "USING(profile_id) WHERE profile_id=:profile_id LIMIT 20",
        {},
    ),
    (
        "WITH saved AS (SELECT session_id FROM activity_sessions) SELECT session_id "
        "FROM saved WHERE profile_id=:profile_id LIMIT 20",
        {},
    ),
    (
        "SELECT session_id FROM activity_sessions WHERE profile_id=:profile_id "
        "-- fictional comment\nLIMIT 20",
        {},
    ),
    ("SELECT name FROM sqlite_master WHERE name=:profile_id LIMIT 20", {}),
    (
        "SELECT private_note FROM activity_sessions WHERE profile_id=:profile_id LIMIT 20",
        {},
    ),
])
def test_history_instruction_forbidden_forms_remain_rejected(sql, parameters) -> None:
    with pytest.raises(QueryRejected):
        validate_query(sql, parameters)
