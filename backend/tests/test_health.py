"""Health, route-surface, and construction-side-effect tests."""

from pathlib import Path

from pydantic import SecretStr

from app.config import Settings
from app.main import create_app


def test_health_reports_database_and_key_without_private_values(harness_factory) -> None:
    harness = harness_factory(configured=True)
    response = harness.request("GET", "/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "ok",
        "database": "available",
        "gemini_api_key": "configured",
    }
    assert "fictional-test-key" not in response.text
    assert str(harness.database_path) not in response.text


def test_health_reports_missing_key(harness_factory) -> None:
    response = harness_factory(configured=False).request("GET", "/api/health")
    assert response.json()["gemini_api_key"] == "not configured"


def test_application_construction_does_not_open_database(tmp_path: Path) -> None:
    database_path = tmp_path / "not-created.sqlite3"
    settings = Settings(
        _env_file=None,
        database_path=database_path,
        gemini_api_key=SecretStr("construction-only-fake"),
    )

    application = create_app(settings=settings)

    assert not database_path.exists()
    assert not hasattr(application.state, "service")


def test_exact_eleven_api_operations(harness_factory) -> None:
    schema = harness_factory().app.openapi()
    operations = {
        (method.upper(), path)
        for path, methods in schema["paths"].items()
        for method in methods
        if method.lower() in {"get", "put", "post", "patch"}
    }
    assert operations == {
        ("GET", "/api/health"),
        ("GET", "/api/preferences"),
        ("PUT", "/api/preferences"),
        ("POST", "/api/sessions"),
        ("PATCH", "/api/sessions/{session_id}"),
        ("GET", "/api/sessions"),
        ("GET", "/api/sessions/{session_id}"),
        ("POST", "/api/conversations"),
        ("GET", "/api/conversations/{conversation_id}/messages"),
        ("POST", "/api/conversations/{conversation_id}/messages"),
        ("POST", "/api/demo/reset"),
    }
