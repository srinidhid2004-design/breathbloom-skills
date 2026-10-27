"""Foundation tests for safe application construction and health reporting."""

import asyncio

from httpx import ASGITransport, AsyncClient

from app.config import PROJECT_ROOT, get_settings
from app.main import create_app


def request_health():
    async def request():
        transport = ASGITransport(app=create_app())
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/api/health")

    return asyncio.run(request())


def test_application_constructs_with_health_route(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    get_settings.cache_clear()

    response = request_health()

    assert response.status_code == 200
    assert response.json() == {
        "service": "ok",
        "database": "not initialized",
        "gemini_api_key": "not configured",
    }


def test_health_reports_configured_without_exposing_secret(monkeypatch) -> None:
    secret = "fictional-test-secret-that-must-not-leak"
    monkeypatch.setenv("GEMINI_API_KEY", secret)
    get_settings.cache_clear()

    response = request_health()
    response_text = response.text

    assert response.status_code == 200
    assert response.json()["gemini_api_key"] == "configured"
    assert secret not in response_text
    assert str(PROJECT_ROOT) not in response_text
    assert "environment" not in response_text.lower()
    assert "private" not in response_text.lower()


def test_health_route_is_the_only_foundation_api_route() -> None:
    paths = set(create_app().openapi()["paths"])

    assert paths == {"/api/health"}
