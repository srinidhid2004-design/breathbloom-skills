"""Sanitized application errors shared by routes and services."""


class APIError(Exception):
    """An error safe to expose through the public API."""

    def __init__(self, status_code: int, outcome: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.outcome = outcome
        self.message = message


INVALID_REQUEST_MESSAGE = (
    "BreathBloom only supports the listed coursework requests. No model request "
    "was made. You can continue the breathing practice or open Support information "
    "at any time."
)

GENERIC_INVALID_MESSAGE = "The request did not match the documented BreathBloom API contract."
DATABASE_FAILURE_MESSAGE = "BreathBloom could not access its fictional coursework records."
