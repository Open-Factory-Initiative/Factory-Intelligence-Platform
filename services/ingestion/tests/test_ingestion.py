from __future__ import annotations

import json
from pathlib import Path

import pytest
from factory_ingestion import (
    IncomingEventValidationError,
    JsonlEventStore,
    ingest_jsonl,
    validate_incoming_event,
)
from factory_ingestion.cli import main as ingestion_cli_main
from factory_simulator import generate_events


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row))
            output.write("\n")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def jsonl_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line]


def simulator_event(event_type: str) -> dict:
    return next(
        event.model_dump(mode="json")
        for event in generate_events("normal", count=6)
        if event.event_type == event_type
    )


def example_event(file_name: str) -> dict:
    path = Path("examples/events") / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def test_ingestion_persists_valid_simulator_events(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    events = [event.model_dump(mode="json") for event in generate_events("normal", count=6)]
    write_jsonl(input_path, events)
    store = JsonlEventStore(tmp_path / "store.jsonl")

    result = ingest_jsonl(input_path, store=store, dead_letter_path=tmp_path / "dead_letter.jsonl")

    assert result.accepted_count == len(events)
    assert result.rejected_count == 0
    assert len(store.list_events()) == len(events)
    assert len(jsonl_lines(store.path)) == len(events)


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
    assert len(read_jsonl(store.path)) == 1
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
    assert not store.path.exists()
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


def test_local_event_store_preserves_valid_jsonl_event_data(tmp_path: Path) -> None:
    store = JsonlEventStore(tmp_path / "store.jsonl")
    raw_event = simulator_event("process.measurement.recorded")
    event = validate_incoming_event(raw_event)

    store.append(event)

    stored_rows = read_jsonl(store.path)
    assert len(stored_rows) == 1
    assert stored_rows[0] == event.model_dump(mode="json")
    assert validate_incoming_event(stored_rows[0]).event_id == event.event_id


def test_local_event_store_skips_duplicate_event_ids_for_repeatable_runs(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    events = [event.model_dump(mode="json") for event in generate_events("normal", count=6)]
    write_jsonl(input_path, events)
    store = JsonlEventStore(tmp_path / "store.jsonl")

    first_result = ingest_jsonl(input_path, store=store, dead_letter_path=tmp_path / "dead_1.jsonl")
    second_result = ingest_jsonl(
        input_path,
        store=store,
        dead_letter_path=tmp_path / "dead_2.jsonl",
    )

    assert first_result.accepted_count == len(events)
    assert second_result.accepted_count == len(events)
    assert len(store.list_events()) == len(events)
    assert len(jsonl_lines(store.path)) == len(events)


def test_validation_accepts_valid_process_signal_event() -> None:
    raw_event = simulator_event("process.measurement.recorded")

    event = validate_incoming_event(raw_event)

    assert event.event_type == "process.measurement.recorded"
    assert event.payload.signal_id == raw_event["payload"]["signal_id"]


def test_validation_rejects_invalid_process_signal_event() -> None:
    raw_event = simulator_event("process.measurement.recorded")
    raw_event["payload"] = raw_event["payload"] | {"quality": "offline"}

    with pytest.raises(IncomingEventValidationError) as exc_info:
        validate_incoming_event(raw_event)

    assert "shared factory event schema" in str(exc_info.value)
    assert any(issue.path == "quality" for issue in exc_info.value.issues)


def test_validation_accepts_valid_quality_event() -> None:
    raw_event = simulator_event("quality.measurement.recorded")

    event = validate_incoming_event(raw_event)

    assert event.event_type == "quality.measurement.recorded"
    assert event.payload.measurement_name == raw_event["payload"]["measurement_name"]


def test_validation_rejects_invalid_quality_event() -> None:
    raw_event = simulator_event("quality.measurement.recorded")
    raw_event["payload"] = raw_event["payload"] | {"spec_min": 10.0, "spec_max": 1.0}

    with pytest.raises(IncomingEventValidationError) as exc_info:
        validate_incoming_event(raw_event)

    assert any(
        "spec_min must be less than spec_max" in issue.message
        for issue in exc_info.value.issues
    )


@pytest.mark.parametrize(
    ("file_name", "event_type"),
    [
        ("batch_event.json", "production.batch.started"),
        ("work_order_event.json", "production.work_order.started"),
    ],
)
def test_validation_accepts_implemented_batch_and_work_order_events(
    file_name: str,
    event_type: str,
) -> None:
    raw_event = example_event(file_name)

    event = validate_incoming_event(raw_event)

    assert event.event_type == event_type


def test_validation_rejects_missing_required_base_fields() -> None:
    raw_event = simulator_event("process.measurement.recorded")
    del raw_event["event_id"]
    del raw_event["timestamp"]

    with pytest.raises(IncomingEventValidationError) as exc_info:
        validate_incoming_event(raw_event)

    issue_paths = {issue.path for issue in exc_info.value.issues}
    assert {"event_id", "timestamp"} <= issue_paths


def test_ingestion_dead_letter_includes_structured_validation_errors(tmp_path: Path) -> None:
    input_path = tmp_path / "events.jsonl"
    invalid_event = simulator_event("process.measurement.recorded")
    invalid_event["payload"] = invalid_event["payload"] | {"quality": "offline"}
    write_jsonl(input_path, [invalid_event])
    store = JsonlEventStore(tmp_path / "store.jsonl")
    dead_letter_path = tmp_path / "dead_letter.jsonl"

    result = ingest_jsonl(input_path, store=store, dead_letter_path=dead_letter_path)

    dead_letter = read_jsonl(dead_letter_path)[0]
    assert result.accepted_count == 0
    assert store.list_events() == []
    assert dead_letter["errors"][0]["path"] == "quality"
    assert dead_letter["errors"][0]["input"] == "offline"
