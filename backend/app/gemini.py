"""Bounded Google Gemini gateway with no fallback and one total attempt."""

from __future__ import annotations

import re
from typing import Any, Protocol

import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from .config import (
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_MODEL,
    GEMINI_TIMEOUT_MS,
    Settings,
)
from .schemas import ProviderPayload, RequestKind


class ProviderProblem(Exception):
    """Sanitized provider failure; raw provider details never cross this boundary."""

    def __init__(self, outcome: str, safe_error_code: str, status_code: int, message: str) -> None:
        super().__init__(message)
        self.outcome = outcome
        self.safe_error_code = safe_error_code
        self.status_code = status_code
        self.message = message


class GeminiGateway(Protocol):
    def generate(self, context: str, expected_kind: RequestKind) -> ProviderPayload:
        """Return one validated structured response or raise ProviderProblem."""


SAFE_PROVIDER_MESSAGES = {
    "authentication_failure": "The optional Gemini request could not authenticate.",
    "permission_failure": "The optional Gemini request is not permitted for this project.",
    "quota_failure": "The optional Gemini request is unavailable because its quota was reached.",
    "rate_limit_failure": "The optional Gemini request is temporarily rate limited.",
    "timeout": "The optional Gemini request timed out.",
    "provider_failure": "The optional Gemini request is unavailable.",
    "malformed_response": "The optional Gemini response could not be safely validated.",
}


def provider_problem(outcome: str) -> ProviderProblem:
    status_codes = {
        "authentication_failure": 502,
        "permission_failure": 502,
        "quota_failure": 503,
        "rate_limit_failure": 429,
        "timeout": 504,
        "provider_failure": 502,
        "malformed_response": 502,
    }
    return ProviderProblem(outcome, outcome, status_codes[outcome], SAFE_PROVIDER_MESSAGES[outcome])


def validate_provider_payload(payload: Any, expected_kind: RequestKind) -> ProviderPayload:
    try:
        validated = payload if isinstance(payload, ProviderPayload) else ProviderPayload.model_validate(payload)
    except ValidationError as exc:
        raise provider_problem("malformed_response") from exc

    text = validated.response_text.strip()
    if validated.response_kind is not expected_kind:
        raise provider_problem("malformed_response")
    if not text or text != validated.response_text:
        raise provider_problem("malformed_response")
    if re.search(r"<[^>]+>|https?://|www\.", text, flags=re.IGNORECASE):
        raise provider_problem("malformed_response")

    forbidden_claims = (
        "diagnos",
        "therapy",
        "therapeutic",
        "medical advice",
        "treatment plan",
        "cure",
        "improve your mental health",
        "monitoring you",
        "crisis",
        "call 911",
        "call 988",
        "text 988",
    )
    lowered = text.casefold()
    if any(claim in lowered for claim in forbidden_claims):
        raise provider_problem("malformed_response")
    return validated


class GoogleGeminiGateway:
    """Lazily constructs the official SDK client only for an accepted request."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, context: str, expected_kind: RequestKind) -> ProviderPayload:
        if self.settings.gemini_api_key is None:
            raise RuntimeError("gateway constructed without configuration")
        key = self.settings.gemini_api_key.get_secret_value().strip()
        if not key:
            raise RuntimeError("gateway constructed without configuration")

        instructions = (
            "Return only the requested JSON object. Use only the supplied fictional "
            "coursework facts. Be brief and factual. Do not diagnose, provide therapy "
            "or medical advice, claim improvement, infer emotion or crisis, generate "
            "support resources, or alter application-owned activity state."
        )
        try:
            client = genai.Client(
                api_key=key,
                http_options=types.HttpOptions(
                    timeout=GEMINI_TIMEOUT_MS,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"{instructions}\n\nApproved context:\n{context}",
                config=types.GenerateContentConfig(
                    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                    response_mime_type="application/json",
                    response_schema=ProviderPayload,
                ),
            )
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise provider_problem("timeout") from exc
        except errors.APIError as exc:
            status = (exc.status or "").casefold()
            message = (exc.message or "").casefold()
            if exc.code == 401:
                raise provider_problem("authentication_failure") from exc
            if exc.code == 403:
                raise provider_problem("permission_failure") from exc
            if exc.code == 429 and "quota" in f"{status} {message}":
                raise provider_problem("quota_failure") from exc
            if exc.code == 429:
                raise provider_problem("rate_limit_failure") from exc
            raise provider_problem("provider_failure") from exc
        except Exception as exc:
            raise provider_problem("provider_failure") from exc

        parsed = getattr(response, "parsed", None)
        if parsed is None:
            raw_text = getattr(response, "text", None)
            if not isinstance(raw_text, str):
                raise provider_problem("malformed_response")
            try:
                parsed = ProviderPayload.model_validate_json(raw_text)
            except ValidationError as exc:
                raise provider_problem("malformed_response") from exc
        return validate_provider_payload(parsed, expected_kind)
