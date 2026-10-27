"""FastAPI application factory for the BreathBloom foundation."""

from typing import Literal

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from .config import get_settings
from .database import DatabaseStatus, get_database_status


class HealthResponse(BaseModel):
    """Public-safe foundation status values."""

    service: Literal["ok"]
    database: DatabaseStatus
    gemini_api_key: Literal["configured", "not configured"]


def create_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        settings = get_settings()
        return HealthResponse(
            service="ok",
            database=get_database_status(settings.database_path),
            gemini_api_key=settings.gemini_api_key_status,
        )

    return router


def create_app() -> FastAPI:
    application = FastAPI(
        title="BreathBloom API",
        description="Local API foundation for a fictional coursework prototype.",
        version="0.1.0",
    )
    application.include_router(create_api_router())
    return application


app = create_app()
