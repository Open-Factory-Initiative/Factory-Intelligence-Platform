from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from factory_events import EventEnvelope, UnsupportedEventTypeError, validate_event
from pydantic import ValidationError


class EventStore(Protocol):
    def append(self, event: EventEnvelope) -> None:
        ...


@dataclass(frozen=True)
class IngestionResult:
    accepted_count: int
    rejected_count: int


def ingest_jsonl(input_path: Path, *, store: EventStore, dead_letter_path: Path) -> IngestionResult:
    accepted = 0
    rejected = 0
    dead_letter_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(encoding="utf-8") as input_file, dead_letter_path.open(
        "w", encoding="utf-8"
    ) as dead_letter:
        for line_number, line in enumerate(input_file, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue
            try:
                raw_event = json.loads(raw_line)
                event = validate_event(raw_event)
            except (json.JSONDecodeError, UnsupportedEventTypeError, ValidationError) as exc:
                rejected += 1
                dead_letter.write(
                    json.dumps(
                        {
                            "line_number": line_number,
                            "error": str(exc),
                            "raw": raw_line,
                        },
                        sort_keys=True,
                    )
                )
                dead_letter.write("\n")
                continue

            store.append(event)
            accepted += 1

    return IngestionResult(accepted_count=accepted, rejected_count=rejected)

