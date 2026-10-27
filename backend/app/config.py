"""Lazy, backend-only configuration for the BreathBloom coursework prototype."""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
GEMINI_MODEL = "gemini-3.5-flash-lite"


class Settings(BaseSettings):
    """Private runtime settings loaded only when the backend requests them."""

    gemini_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_path(self) -> Path:
        """Return the ignored SQLite path without creating or opening it."""

        return PROJECT_ROOT / "data" / "app.sqlite3"

    @property
    def gemini_api_key_status(self) -> str:
        """Expose configuration state, never the secret value."""

        if self.gemini_api_key is None:
            return "not configured"
        return "configured" if self.gemini_api_key.get_secret_value().strip() else "not configured"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings lazily and cache them for the backend process."""

    return Settings()
