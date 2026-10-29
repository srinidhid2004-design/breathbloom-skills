"""Sanitized application errors shared by routes and services."""


class APIError(Exception):
    def __init__(self, status_code: int, outcome: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.outcome = outcome
        self.message = message


INVALID_REQUEST_MESSAGE = "The request did not match the documented FocusBloom API contract."
DATABASE_FAILURE_MESSAGE = "FocusBloom could not access its fictional coursework records."
MISSING_CONFIGURATION_MESSAGE = (
    "The optional Gemini feature is not configured. The application-owned activities, "
    "saved records, and Support information remain available."
)
MODEL_FAILURE_MESSAGE = (
    "The optional Gemini request could not be completed. Your local work remains available."
)
QUERY_REJECTED_MESSAGE = (
    "That history question could not be answered with the approved read-only record query."
)
NO_MATCH_MESSAGE = "No saved FocusBloom records matched that history question."
