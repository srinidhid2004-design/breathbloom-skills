"""Bounded Gemini contracts: one attempt, fixed model, no provider fallback."""

from __future__ import annotations

import json
import re
from typing import Any, Protocol, TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from .config import GEMINI_MAX_OUTPUT_TOKENS, GEMINI_MODEL, GEMINI_TIMEOUT_MS, Settings
from .schemas import GroundedHistoryAnswer, HistoryQueryProposal, PerspectiveAlternativesOutput


class ProviderProblem(Exception):
    def __init__(self, safe_error_code: str, status_code: int = 502) -> None:
        super().__init__(safe_error_code)
        self.safe_error_code = safe_error_code
        self.status_code = status_code


class GeminiGateway(Protocol):
    def perspective(self, context: dict[str, Any]) -> PerspectiveAlternativesOutput: ...
    def propose_history_query(self, question: str) -> HistoryQueryProposal: ...
    def answer_history(self, context: dict[str, Any]) -> GroundedHistoryAnswer: ...


FORBIDDEN_OUTPUT = (
    "diagnos", "therapy", "therapeutic", "medical advice", "treatment",
    "cure", "improve your mental health", "monitoring you", "crisis",
    "call 911", "call 988", "text 988", "you feel", "you are anxious",
    "you should", "you need to", "you must", "i recommend", "my advice",
    "will help you", "take action",
)


def _safe_text(value: str) -> bool:
    lowered = value.casefold()
    return (
        value == value.strip()
        and not re.search(r"<[^>]+>|https?://|www\.", value, re.IGNORECASE)
        and not any(term in lowered for term in FORBIDDEN_OUTPUT)
    )


def validate_perspective(value: Any) -> PerspectiveAlternativesOutput:
    try:
        output = value if isinstance(value, PerspectiveAlternativesOutput) else PerspectiveAlternativesOutput.model_validate(value)
    except ValidationError as exc:
        raise ProviderProblem("malformed_response") from exc
    if any(not _safe_text(item.alternative) or not _safe_text(item.factual_basis) for item in output.alternatives):
        raise ProviderProblem("malformed_response")
    return output


def validate_query_proposal(value: Any) -> HistoryQueryProposal:
    try:
        return value if isinstance(value, HistoryQueryProposal) else HistoryQueryProposal.model_validate(value)
    except ValidationError as exc:
        raise ProviderProblem("malformed_response") from exc


def validate_grounded_answer(value: Any) -> GroundedHistoryAnswer:
    try:
        output = value if isinstance(value, GroundedHistoryAnswer) else GroundedHistoryAnswer.model_validate(value)
    except ValidationError as exc:
        raise ProviderProblem("malformed_response") from exc
    if not _safe_text(output.answer):
        raise ProviderProblem("malformed_response")
    return output


T = TypeVar("T", bound=BaseModel)


class GoogleGeminiGateway:
    """Construct the official SDK client only for an accepted configured request."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _generate(self, *, purpose: str, context: Any, schema: type[T]) -> T:
        key = "" if self.settings.gemini_api_key is None else self.settings.gemini_api_key.get_secret_value().strip()
        if not key:
            raise ProviderProblem("missing_configuration", 503)
        instructions = {
            "perspective": (
                "Return only the exact JSON schema. Offer one or two brief alternative interpretations "
                "and a factual basis for each. Do not give advice, diagnose, infer emotion or crisis, "
                "claim effectiveness, select an action, or navigate the application."
            ),
            "history_sql": (
                "Return only the exact JSON schema. For saved FocusBloom records, propose one bounded "
                "parameterized SELECT using one approved table, WHERE profile_id = :profile_id, and a "
                "final LIMIT no greater than 20. Use bound parameters for other values. No CTE, join, "
                "subquery, comment, schema access, or mutation. Mark unrelated requests out_of_scope."
            ),
            "history_answer": (
                "Return only the exact JSON schema. Answer solely from the supplied numbered rows and "
                "cite each used row number. State when information is absent. Do not infer motivation, "
                "emotion, diagnosis, effectiveness, improvement, treatment, or advice."
            ),
        }[purpose]
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
                contents=f"{instructions}\n\nApproved bounded context:\n{json.dumps(context, separators=(',', ':'), sort_keys=True)}",
                config=types.GenerateContentConfig(
                    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise ProviderProblem("timeout", 504) from exc
        except errors.APIError as exc:
            if exc.code == 401:
                raise ProviderProblem("authentication_failure") from exc
            if exc.code == 403:
                raise ProviderProblem("permission_failure") from exc
            if exc.code == 429:
                raise ProviderProblem("rate_limit_failure", 429) from exc
            raise ProviderProblem("provider_failure") from exc
        except ProviderProblem:
            raise
        except Exception as exc:
            raise ProviderProblem("provider_failure") from exc
        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            try:
                return parsed if isinstance(parsed, schema) else schema.model_validate(parsed)
            except ValidationError as exc:
                raise ProviderProblem("malformed_response") from exc
        raw = getattr(response, "text", None)
        if not isinstance(raw, str):
            raise ProviderProblem("malformed_response")
        try:
            return schema.model_validate_json(raw)
        except ValidationError as exc:
            raise ProviderProblem("malformed_response") from exc

    def perspective(self, context: dict[str, Any]) -> PerspectiveAlternativesOutput:
        return validate_perspective(self._generate(purpose="perspective", context=context, schema=PerspectiveAlternativesOutput))

    def propose_history_query(self, question: str) -> HistoryQueryProposal:
        return validate_query_proposal(self._generate(purpose="history_sql", context={"question": question}, schema=HistoryQueryProposal))

    def answer_history(self, context: dict[str, Any]) -> GroundedHistoryAnswer:
        return validate_grounded_answer(self._generate(purpose="history_answer", context=context, schema=GroundedHistoryAnswer))
