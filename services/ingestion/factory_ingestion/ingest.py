from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from factory_events import EventEnvelope

from factory_ingestion.validation import IncomingEventValidationError, validate_incoming_event


class EventStore(Protocol):
    def append(self, event: EventEnvelope) -> None: ...


class InvalidJsonlEventError(ValueError):
    """Raised when a JSONL row is valid JSON but not a factory event object."""


@dataclass(frozen=True)
class IngestionResult:
    accepted_count: int
    rejected_count: int

    @property
    def dead_letter_count(self) -> int:
        return self.rejected_count


def ingest_jsonl(input_path: Path, *, store: EventStore, dead_letter_path: Path) -> IngestionResult:
    if not input_path.exists():
        msg = f"input file not found: {input_path}"
        raise FileNotFoundError(msg)
    if not input_path.is_file():
        msg = f"input path is not a file: {input_path}"
        raise IsADirectoryError(msg)

    accepted = 0
    rejected = 0
    dead_letter_path.parent.mkdir(parents=True, exist_ok=True)

    with (
        input_path.open(encoding="utf-8") as input_file,
        dead_letter_path.open("w", encoding="utf-8") as dead_letter,
    ):
        for line_number, line in enumerate(input_file, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue
            raw_event: Any | None = None
            try:
                raw_event = json.loads(raw_line)
                if not isinstance(raw_event, dict):
                    msg = "JSONL line must contain a factory event object"
                    raise InvalidJsonlEventError(msg)
                event = validate_incoming_event(raw_event)
            except (
                InvalidJsonlEventError,
                json.JSONDecodeError,
                IncomingEventValidationError,
            ) as exc:
                rejected += 1
                validation_errors = []
                if isinstance(exc, IncomingEventValidationError):
                    validation_errors = exc.model_dump()["issues"]
                dead_letter.write(
                    json.dumps(
                        {
                            "error": str(exc),
                            "errors": validation_errors,
                            "line_number": line_number,
                            "payload": raw_event,
                            "raw": raw_line,
                            "recorded_at": datetime.now(UTC).isoformat(),
                            "source_path": str(input_path),
                        },
                        sort_keys=True,
                    )
                )
                dead_letter.write("\n")
                continue

            store.append(event)
            accepted += 1

    return IngestionResult(accepted_count=accepted, rejected_count=rejected)
