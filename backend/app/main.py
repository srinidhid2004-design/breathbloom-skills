"""FastAPI application factory for the FocusBloom version-2 backend."""

from __future__ import annotations

import sqlite3
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .database import Repository, get_database_status
from .errors import APIError, DATABASE_FAILURE_MESSAGE, INVALID_REQUEST_MESSAGE
from .gemini import GeminiGateway
from .schemas import (
    ActivityEventCreate, ActivitySessionCreate, ActivitySessionUpdate, ActivityType,
    ConversationCreate, DemoResetRequest, HistoryMessageCreate, HistoryRunRequest,
    NextStepSeedCreate, PerspectiveAlternativesRequest, PerspectiveArtifactCreate,
    PreferenceUpdate, SavedTextDeleteRequest, SessionStatus,
)
from .services import FocusBloomService


def _error(status_code: int, outcome: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"outcome": outcome, "message": message})


def create_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")

    def service(request: Request) -> FocusBloomService:
        return request.app.state.service

    @router.get("/health")
    def health(request: Request) -> dict[str, Any]:
        backend = service(request)
        return {
            "service": "ok", "schema_version": 2,
            "database": get_database_status(backend.settings.database_path),
            "gemini_api_key": backend.settings.gemini_api_key_status,
        }

    @router.get("/preferences")
    def get_preferences(request: Request) -> dict[str, Any]:
        return service(request).get_preferences()

    @router.put("/preferences")
    def update_preferences(request: Request, payload: PreferenceUpdate) -> dict[str, Any]:
        return service(request).update_preferences(payload)

    @router.get("/focus-activities")
    def focus_activities(request: Request) -> dict[str, Any]:
        return service(request).focus_activities()

    @router.post("/activity-sessions")
    def create_session(request: Request, payload: ActivitySessionCreate) -> JSONResponse:
        body = service(request).create_session(payload)
        return JSONResponse(status_code=200 if body["outcome"] == "duplicate_request" else 201, content=body)

    @router.patch("/activity-sessions/{session_id}")
    def update_session(request: Request, session_id: str, payload: ActivitySessionUpdate) -> dict[str, Any]:
        return service(request).update_session(session_id, payload)

    @router.post("/activity-sessions/{session_id}/events")
    def create_event(request: Request, session_id: str, payload: ActivityEventCreate) -> JSONResponse:
        body = service(request).create_event(session_id, payload)
        return JSONResponse(status_code=200 if body["outcome"] == "duplicate_request" else 201, content=body)

    @router.get("/activity-sessions")
    def list_sessions(
        request: Request, cursor: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=20), status: SessionStatus | None = None,
        activity_type: ActivityType | None = None,
    ) -> dict[str, Any]:
        return service(request).list_sessions(
            cursor, limit, status.value if status else None, activity_type.value if activity_type else None
        )

    @router.get("/activity-sessions/{session_id}")
    def get_session(request: Request, session_id: str) -> dict[str, Any]:
        return service(request).get_session(session_id)

    @router.post("/perspective/alternatives")
    def perspective_alternatives(request: Request, payload: PerspectiveAlternativesRequest) -> JSONResponse:
        status, body = service(request).perspective_alternatives(payload)
        return JSONResponse(status_code=status, content=body)

    @router.post("/perspective-artifacts")
    def create_artifact(request: Request, payload: PerspectiveArtifactCreate) -> JSONResponse:
        body = service(request).create_artifact(payload)
        return JSONResponse(status_code=200 if body["outcome"] == "duplicate_request" else 201, content=body)

    @router.get("/perspective-artifacts")
    def list_artifacts(
        request: Request, cursor: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=20)
    ) -> dict[str, Any]:
        return service(request).list_artifacts(cursor, limit)

    @router.delete("/perspective-artifacts/{artifact_id}")
    def delete_artifact(request: Request, artifact_id: str) -> dict[str, Any]:
        return service(request).delete_artifact(artifact_id)

    @router.post("/next-step-seeds")
    def create_seed(request: Request, payload: NextStepSeedCreate) -> JSONResponse:
        body = service(request).create_seed(payload)
        return JSONResponse(status_code=200 if body["outcome"] == "duplicate_request" else 201, content=body)

    @router.get("/next-step-seeds")
    def list_seeds(
        request: Request, cursor: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=20)
    ) -> dict[str, Any]:
        return service(request).list_seeds(cursor, limit)

    @router.delete("/next-step-seeds/{seed_id}")
    def delete_seed(request: Request, seed_id: str) -> dict[str, Any]:
        return service(request).delete_seed(seed_id)

    @router.post("/conversations")
    def create_conversation(request: Request, payload: ConversationCreate) -> JSONResponse:
        body = service(request).create_conversation(payload)
        return JSONResponse(status_code=200 if body["outcome"] == "duplicate_request" else 201, content=body)

    @router.get("/conversations/{conversation_id}/messages")
    def list_messages(
        request: Request, conversation_id: str, cursor: int = Query(default=0, ge=0),
        limit: int = Query(default=20, ge=1, le=20),
    ) -> dict[str, Any]:
        return service(request).list_messages(conversation_id, cursor, limit)

    @router.post("/conversations/{conversation_id}/messages")
    def create_history_message(
        request: Request, conversation_id: str, payload: HistoryMessageCreate
    ) -> JSONResponse:
        body = service(request).create_history_message(conversation_id, payload)
        return JSONResponse(status_code=200 if body["outcome"] == "duplicate_request" else 201, content=body)

    @router.post("/garden-guide/history-questions")
    def run_history(request: Request, payload: HistoryRunRequest) -> JSONResponse:
        status, body = service(request).run_history(payload)
        return JSONResponse(status_code=status, content=body)

    @router.delete("/demo/saved-text")
    def delete_saved_text(request: Request, _payload: SavedTextDeleteRequest) -> dict[str, Any]:
        return service(request).delete_saved_text()

    @router.post("/demo/reset")
    def reset_demo(request: Request, payload: DemoResetRequest) -> dict[str, Any]:
        return service(request).reset_demo(payload)

    return router


def create_app(settings: Settings | None = None, gateway: GeminiGateway | None = None) -> FastAPI:
    """Construct the app without loading credentials or creating a database."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        runtime_settings = settings or get_settings()
        repository = Repository(runtime_settings.database_path)
        repository.initialize()
        application.state.service = FocusBloomService(repository, runtime_settings, gateway)
        yield

    application = FastAPI(
        title="FocusBloom API", description="Local API for a fictional coursework prototype.",
        version="0.3.0", lifespan=lifespan,
    )

    @application.exception_handler(APIError)
    async def api_error_handler(_request: Request, exc: APIError) -> JSONResponse:
        return _error(exc.status_code, exc.outcome, exc.message)

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return _error(422, "invalid_request", INVALID_REQUEST_MESSAGE)

    @application.exception_handler(sqlite3.Error)
    async def database_error_handler(_request: Request, _exc: sqlite3.Error) -> JSONResponse:
        return _error(503, "database_failure", DATABASE_FAILURE_MESSAGE)

    application.include_router(create_api_router())
    return application


app = create_app()
