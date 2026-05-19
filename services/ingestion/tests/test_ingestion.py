from __future__ import annotations

import json
from pathlib import Path

import pytest
from factory_ingestion import JsonlEventStore, ingest_jsonl
from factory_ingestion.cli import main as ingestion_cli_main
from factory_simulator import generate_events


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row))
            output.write("\n")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


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


def test_ingestion_rejects_malformed_json_line(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    valid_event = generate_events("normal", count=6)[0].model_dump(mode="json")
    input_path.write_text(
        "\n".join([json.dumps(valid_event), '{"event_id": "broken"']) + "\n",
        encoding="utf-8",
    )
    store = JsonlEventStore(tmp_path / "store.jsonl")
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingest_jsonl(input_path, store=store, dead_letter_path=dead_letter_path)

    assert result.accepted_count == 1
    assert result.rejected_count == 1
    assert len(store.list_events()) == 1
    dead_letters = read_jsonl(dead_letter_path)
    assert dead_letters[0]["line_number"] == 2
    assert dead_letters[0]["raw"] == '{"event_id": "broken"'


def test_ingestion_rejects_schema_invalid_event(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    invalid_event = generate_events("normal", count=6)[0].model_dump(mode="json")
    invalid_event["payload"] = invalid_event["payload"] | {"normal_min": 10.0, "normal_max": 2.0}
    write_jsonl(input_path, [invalid_event])
    store = JsonlEventStore(tmp_path / "store.jsonl")
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingest_jsonl(input_path, store=store, dead_letter_path=dead_letter_path)

    assert result.accepted_count == 0
    assert result.rejected_count == 1
    assert store.list_events() == []
    dead_letters = read_jsonl(dead_letter_path)
    assert dead_letters[0]["line_number"] == 1
    assert "normal_min must be less than normal_max" in dead_letters[0]["error"]


def test_ingestion_rejects_non_object_json_line(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    input_path.write_text("[]\n", encoding="utf-8")
    store = JsonlEventStore(tmp_path / "store.jsonl")
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingest_jsonl(input_path, store=store, dead_letter_path=dead_letter_path)

    assert result.accepted_count == 0
    assert result.rejected_count == 1
    assert "factory event object" in dead_letter_path.read_text(encoding="utf-8")


def test_ingestion_handles_empty_file(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    input_path.write_text("", encoding="utf-8")
    store = JsonlEventStore(tmp_path / "store.jsonl")
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingest_jsonl(input_path, store=store, dead_letter_path=dead_letter_path)

    assert result.accepted_count == 0
    assert result.rejected_count == 0
    assert store.list_events() == []
    assert dead_letter_path.read_text(encoding="utf-8") == ""


def test_ingestion_reports_missing_input_file(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "store.jsonl")

    with pytest.raises(FileNotFoundError, match="input file not found"):
        ingest_jsonl(
            tmp_path / "missing.jsonl",
            store=store,
            dead_letter_path=tmp_path / "dead.jsonl",
        )


def test_ingestion_cli_prints_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_path = tmp_path / "events.jsonl"
    events = [event.model_dump(mode="json") for event in generate_events("normal", count=6)]
    write_jsonl(input_path, events)
    events_store = tmp_path / "store.jsonl"
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingestion_cli_main(
        [
            "--input",
            str(input_path),
            "--events-store",
            str(events_store),
            "--dead-letter",
            str(dead_letter_path),
        ]
    )

    output = capsys.readouterr().out
    assert result == 0
    assert f"ingestion complete: accepted={len(events)} rejected=0" in output
    assert len(JsonlEventStore(events_store).list_events()) == len(events)
