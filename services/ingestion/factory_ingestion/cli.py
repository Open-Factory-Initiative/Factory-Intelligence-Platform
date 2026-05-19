from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from factory_ingestion.ingest import ingest_jsonl
from factory_ingestion.storage import JsonlEventStore


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
        "ingestion complete: "
        f"accepted={result.accepted_count} rejected={result.rejected_count} "
        f"dead_letter_count={result.dead_letter_count} "
        f"events_store={args.events_store} dead_letter={args.dead_letter}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
