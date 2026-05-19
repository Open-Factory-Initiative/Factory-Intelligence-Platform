from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from factory_ingestion.ingest import IngestionResult, ingest_jsonl
from factory_ingestion.storage import JsonlEventStore

VALIDATION_EXAMPLE_LIMIT = 3


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and ingest factory event JSONL.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--events-store", type=Path, default=Path(".local/storage/events.jsonl"))
    parser.add_argument(
        "--dead-letter", type=Path, default=Path(".local/storage/dead_letter.jsonl")
    )
    args = parser.parse_args(argv)

    store = JsonlEventStore(args.events_store)
    try:
        result = ingest_jsonl(args.input, store=store, dead_letter_path=args.dead_letter)
    except (FileNotFoundError, IsADirectoryError) as exc:
        parser.error(str(exc))

    print(
        format_ingestion_summary(
            result,
            input_path=args.input,
            events_store_path=args.events_store,
            dead_letter_path=args.dead_letter,
        )
    )
    return 0


def format_ingestion_summary(
    result: IngestionResult,
    *,
    input_path: Path,
    events_store_path: Path,
    dead_letter_path: Path,
) -> str:
    lines = [
        "ingestion summary",
        f"input_file: {input_path}",
        f"accepted_events: {result.accepted_count}",
        f"rejected_events: {result.rejected_count}",
        f"dead_letter_count: {result.dead_letter_count}",
        f"accepted_output: {events_store_path}",
        f"dead_letter_output: {dead_letter_path}",
    ]
    examples = _validation_error_examples(dead_letter_path)
    if examples:
        lines.append("validation_error_examples:")
        lines.extend(f"- {example}" for example in examples)
    return "\n".join(lines)


def _validation_error_examples(dead_letter_path: Path) -> list[str]:
    if not dead_letter_path.exists():
        return []
    examples: list[str] = []
    with dead_letter_path.open(encoding="utf-8") as dead_letter:
        for line in dead_letter:
            if not line.strip():
                continue
            record = json.loads(line)
            examples.append(_format_dead_letter_example(record))
            if len(examples) >= VALIDATION_EXAMPLE_LIMIT:
                break
    return examples


def _format_dead_letter_example(record: dict) -> str:
    line_number = record.get("line_number", "unknown")
    error = str(record.get("error", "validation error"))
    details = record.get("errors") or []
    if details:
        first_detail = details[0]
        path = first_detail.get("path", "<event>")
        message = first_detail.get("message", error)
        return f"line {line_number}: {path}: {message}"
    return f"line {line_number}: {error}"


if __name__ == "__main__":
    raise SystemExit(main())
