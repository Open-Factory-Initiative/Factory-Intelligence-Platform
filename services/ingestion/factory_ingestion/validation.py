from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from factory_events import EventEnvelope, UnsupportedEventTypeError, validate_event
from pydantic import ValidationError


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str
    issue_type: str
    input_value: Any | None = None

    def model_dump(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "path": self.path,
            "message": self.message,
            "type": self.issue_type,
        }
        if self.input_value is not None:
            data["input"] = self.input_value
        return data


class IncomingEventValidationError(ValueError):
    def __init__(self, message: str, issues: tuple[ValidationIssue, ...]) -> None:
        super().__init__(message)
        self.issues = issues

    def model_dump(self) -> dict[str, Any]:
        return {
            "message": str(self),
            "issues": [issue.model_dump() for issue in self.issues],
        }


def validate_incoming_event(raw_event: dict[str, Any]) -> EventEnvelope:
    try:
        return validate_event(raw_event)
    except UnsupportedEventTypeError as exc:
        raise IncomingEventValidationError(
            "event type is not supported by the shared factory event schemas",
            (
                ValidationIssue(
                    path="event_type",
                    message=str(exc),
                    issue_type="unsupported_event_type",
                ),
            ),
        ) from exc
    except ValidationError as exc:
        issues = tuple(
            ValidationIssue(
                path=_format_location(error.get("loc", ())),
                message=str(error.get("msg", "validation error")),
                issue_type=str(error.get("type", "validation_error")),
                input_value=error.get("input"),
            )
            for error in exc.errors()
        )
        raise IncomingEventValidationError(
            _validation_summary(issues),
            issues,
        ) from exc


def _format_location(location: Any) -> str:
    if not location:
        return "<event>"
    if isinstance(location, str):
        return location
    return ".".join(str(part) for part in location)


def _validation_summary(issues: tuple[ValidationIssue, ...]) -> str:
    if not issues:
        return "event failed shared factory event schema validation"
    first_issue = issues[0]
    return (
        "event failed shared factory event schema validation: "
        f"{first_issue.path}: {first_issue.message}"
    )
