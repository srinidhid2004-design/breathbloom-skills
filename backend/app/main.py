"""FastAPI application factory for the complete BreathBloom backend."""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .database import Repository, get_database_status
from .errors import (
    APIError,
    DATABASE_FAILURE_MESSAGE,
    GENERIC_INVALID_MESSAGE,
    INVALID_REQUEST_MESSAGE,
)
from .gemini import GeminiGateway
from .schemas import (
    ConversationCreate,
    DemoResetRequest,
    ModelActionRequest,
    PreferenceUpdate,
    SessionAction,
    SessionStart,
    SessionStatus,
)
from .services import BreathBloomService


def _error(status_code: int, outcome: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"outcome": outcome, "message": message},
    )


def create_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")

    def service(request: Request) -> BreathBloomService:
        return request.app.state.service

    @router.get("/health")
    def health(request: Request) -> dict[str, Any]:
        backend = service(request)
        return {
            "service": "ok",
            "database": get_database_status(backend.settings.database_path),
            "gemini_api_key": backend.settings.gemini_api_key_status,
        }

    @router.get("/preferences")
    def get_preferences(request: Request) -> dict[str, Any]:
        return service(request).get_preferences()

    @router.put("/preferences")
    def update_preferences(request: Request, payload: PreferenceUpdate) -> dict[str, Any]:
        return service(request).update_preferences(payload)

    @router.post("/sessions")
    def start_session(request: Request, payload: SessionStart) -> JSONResponse:
        body = service(request).start_session(payload)
        status_code = 200 if body["outcome"] == "duplicate_request" else 201
        return JSONResponse(status_code=status_code, content=body)

    @router.patch("/sessions/{session_id}")
    def update_session(
        request: Request,
        session_id: str,
        payload: SessionAction,
    ) -> dict[str, Any]:
        return service(request).update_session(session_id, payload)

    @router.get("/sessions")
    def list_sessions(
        request: Request,
        cursor: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=20),
        status: SessionStatus | None = None,
    ) -> dict[str, Any]:
        return service(request).list_sessions(cursor, limit, status.value if status else None)

    @router.get("/sessions/{session_id}")
    def get_session(request: Request, session_id: str) -> dict[str, Any]:
        return service(request).get_session(session_id)

    @router.post("/conversations")
    def create_conversation(request: Request, payload: ConversationCreate) -> JSONResponse:
        body = service(request).create_conversation(payload)
        status_code = 200 if body["outcome"] == "duplicate_request" else 201
        return JSONResponse(status_code=status_code, content=body)

    @router.get("/conversations/{conversation_id}/messages")
    def list_messages(
        request: Request,
        conversation_id: str,
        cursor: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=20),
    ) -> dict[str, Any]:
        return service(request).list_messages(conversation_id, cursor, limit)

    @router.post("/conversations/{conversation_id}/messages")
    def request_model(
        request: Request, conversation_id: str, payload: ModelActionRequest
    ) -> JSONResponse:
        status_code, body = service(request).request_model(conversation_id, payload)
        return JSONResponse(status_code=status_code, content=body)

    @router.post("/demo/reset")
    def reset_demo(request: Request, payload: DemoResetRequest) -> dict[str, Any]:
        return service(request).reset_demo(payload)

    return router


def create_app(
    settings: Settings | None = None,
    gateway: GeminiGateway | None = None,
) -> FastAPI:
    """Build the app without loading secrets, creating files, or opening SQLite."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        runtime_settings = settings or get_settings()
        repository = Repository(runtime_settings.database_path)
        try:
            repository.initialize()
        except (OSError, sqlite3.Error) as exc:
            application.state.startup_error = exc
        application.state.service = BreathBloomService(repository, runtime_settings, gateway)
        yield

    application = FastAPI(
        title="BreathBloom API",
        description="Local API for a fictional coursework prototype.",
        version="0.2.0",
        lifespan=lifespan,
    )

    @application.exception_handler(APIError)
    async def api_error_handler(_request: Request, exc: APIError) -> JSONResponse:
        return _error(exc.status_code, exc.outcome, exc.message)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        if request.method == "POST" and request.url.path.endswith("/messages"):
            return _error(422, "invalid_request", INVALID_REQUEST_MESSAGE)
        return _error(422, "invalid_request", GENERIC_INVALID_MESSAGE)

    @application.exception_handler(sqlite3.Error)
    async def database_error_handler(_request: Request, _exc: sqlite3.Error) -> JSONResponse:
        return _error(503, "database_failure", DATABASE_FAILURE_MESSAGE)

    application.include_router(create_api_router())
    return application


app = create_app()
