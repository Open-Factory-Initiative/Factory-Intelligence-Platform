from __future__ import annotations

import json
from pathlib import Path

import pytest
from factory_events import FactoryEvent, UnsupportedEventTypeError, validate_event
from pydantic import ValidationError

FIXTURES = Path(__file__).resolve().parents[2] / "test-fixtures"


def load_fixture(path: Path) -> dict:
    return json.loads(path.read_text())


def test_valid_process_measurement_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_measurement_recorded.json")

    validated = validate_event(event)

    assert validated.event_type == "process.measurement.recorded"
    assert validated.payload.signal_id == "fill_weight"
    assert validated.metadata.simulated is True


def test_base_factory_event_contract_supports_batch_and_work_order_refs() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "base_factory_event.json")

    validated = FactoryEvent.model_validate(event)

    assert validated.event_id == "evt_base_000001"
    assert validated.source.system == "factory-simulator"
    assert validated.context.line_id == "line_1"
    assert validated.context.asset_id == "asset_filler_1"
    assert validated.context.batch_id == "batch_demo_1001"
    assert validated.context.work_order_id == "wo_1001"
    assert validated.payload.signal_id == "fill_weight"


def test_valid_quality_measurement_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_measurement_recorded.json")

    validated = validate_event(event)

    assert validated.event_type == "quality.measurement.recorded"
    assert validated.payload.result == "pass"


def test_missing_required_field_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "missing_event_id.json")

    with pytest.raises(ValidationError):
        validate_event(event)


def test_missing_required_metadata_field_is_rejected() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "base_factory_event.json")
    del event["metadata"]["trace_id"]

    with pytest.raises(ValidationError, match="trace_id"):
        validate_event(event)


def test_invalid_payload_reports_payload_validation_error() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "base_factory_event.json")
    del event["payload"]["signal_id"]

    with pytest.raises(ValidationError, match="signal_id"):
        validate_event(event)


def test_unknown_event_type_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "unknown_event_type.json")

    with pytest.raises(UnsupportedEventTypeError):
        validate_event(event)


def test_simulator_event_must_be_marked_simulated() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_measurement_recorded.json")
    event["metadata"]["simulated"] = False

    with pytest.raises(ValidationError, match="simulator events"):
        validate_event(event)


def test_timestamp_must_be_utc() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_measurement_recorded.json")
    event["timestamp"] = "2026-01-01T12:00:00-05:00"

    with pytest.raises(ValidationError, match="UTC"):
        validate_event(event)
