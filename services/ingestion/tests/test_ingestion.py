from __future__ import annotations

import json
from pathlib import Path

from factory_ingestion import JsonlEventStore, ingest_jsonl
from factory_simulator import generate_events


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row))
            output.write("\n")


def test_ingestion_persists_valid_simulator_events(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    events = [event.model_dump(mode="json") for event in generate_events("normal", count=6)]
    write_jsonl(input_path, events)
    store = JsonlEventStore(tmp_path / "store.jsonl")

    result = ingest_jsonl(input_path, store=store, dead_letter_path=tmp_path / "dead_letter.jsonl")

    assert result.accepted_count == len(events)
    assert result.rejected_count == 0
    assert len(store.list_events()) == len(events)


def test_ingestion_rejects_invalid_event_and_keeps_processing(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    valid_event = generate_events("normal", count=6)[0].model_dump(mode="json")
    invalid_event = valid_event | {"event_type": "unknown.event"}
    write_jsonl(input_path, [invalid_event, valid_event])
    store = JsonlEventStore(tmp_path / "store.jsonl")
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingest_jsonl(input_path, store=store, dead_letter_path=dead_letter_path)

    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert len(store.list_events()) == 1
    assert "unsupported event_type" in dead_letter_path.read_text()
