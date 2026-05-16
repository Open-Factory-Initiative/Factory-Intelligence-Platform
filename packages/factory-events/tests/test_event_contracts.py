from __future__ import annotations

import json
from pathlib import Path

import pytest
from factory_events import (
    BatchEvent,
    FactoryEvent,
    ProcessSignalEvent,
    QualityEvent,
    UnsupportedEventTypeError,
    WorkOrderEvent,
    validate_event,
)
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "packages" / "test-fixtures"
EXAMPLES = REPO_ROOT / "examples" / "events"

VALID_EVENT_FIXTURES = [
    ("base_factory_event.json", FactoryEvent, "process.measurement.recorded"),
    ("process_measurement_recorded.json", ProcessSignalEvent, "process.measurement.recorded"),
    ("process_temperature_signal.json", ProcessSignalEvent, "process.measurement.recorded"),
    ("process_pressure_signal.json", ProcessSignalEvent, "process.measurement.recorded"),
    ("quality_measurement_recorded.json", QualityEvent, "quality.measurement.recorded"),
    ("quality_in_spec_result.json", QualityEvent, "quality.measurement.recorded"),
    ("quality_out_of_spec_result.json", QualityEvent, "quality.measurement.recorded"),
    ("quality_visual_inspection.json", QualityEvent, "quality.measurement.recorded"),
    ("batch_started.json", BatchEvent, "production.batch.started"),
    ("batch_completed.json", BatchEvent, "production.batch.completed"),
    ("work_order_started.json", WorkOrderEvent, "production.work_order.started"),
    ("work_order_completed.json", WorkOrderEvent, "production.work_order.completed"),
]

INVALID_EVENT_FIXTURES = [
    ("missing_event_id.json", ("event_id",), "Field required"),
    ("process_signal_missing_tag_name.json", ("tag_name",), "Field required"),
    ("process_signal_invalid_value.json", ("value",), "valid number"),
    ("quality_missing_check_type.json", ("quality_check_type",), "Field required"),
    ("quality_invalid_severity.json", ("severity",), "low"),
    ("batch_missing_lot_id.json", ("lot_id",), "Field required"),
    ("work_order_invalid_status.json", ("status",), "planned"),
]

EXAMPLE_EVENT_FILES = [
    ("base_factory_event.json", FactoryEvent, "process.measurement.recorded"),
    ("process_signal_event.json", ProcessSignalEvent, "process.measurement.recorded"),
    ("quality_event.json", QualityEvent, "quality.measurement.recorded"),
    ("batch_event.json", BatchEvent, "production.batch.started"),
    ("work_order_event.json", WorkOrderEvent, "production.work_order.started"),
]


def load_fixture(path: Path) -> dict:
    return json.loads(path.read_text())


@pytest.mark.parametrize(
    ("fixture_name", "typed_model", "expected_event_type"),
    VALID_EVENT_FIXTURES,
)
def test_valid_event_fixtures_pass_public_and_typed_contracts(
    fixture_name: str,
    typed_model: type[FactoryEvent],
    expected_event_type: str,
) -> None:
    event = load_fixture(FIXTURES / "valid-events" / fixture_name)

    public_event = validate_event(event)
    typed_event = typed_model.model_validate(event)

    assert public_event.event_type == expected_event_type
    assert typed_event.event_type == expected_event_type


@pytest.mark.parametrize(
    ("fixture_name", "expected_location", "expected_message"),
    INVALID_EVENT_FIXTURES,
)
def test_invalid_event_fixtures_report_clear_validation_errors(
    fixture_name: str,
    expected_location: tuple[str, ...],
    expected_message: str,
) -> None:
    event = load_fixture(FIXTURES / "invalid-events" / fixture_name)

    with pytest.raises(ValidationError) as error:
        validate_event(event)

    errors = error.value.errors()
    assert any(
        tuple(item["loc"]) == expected_location and expected_message in item["msg"]
        for item in errors
    )


@pytest.mark.parametrize(
    ("example_name", "typed_model", "expected_event_type"),
    EXAMPLE_EVENT_FILES,
)
def test_example_event_payloads_validate_against_contracts(
    example_name: str,
    typed_model: type[FactoryEvent],
    expected_event_type: str,
) -> None:
    event = load_fixture(EXAMPLES / example_name)

    public_event = validate_event(event)
    typed_event = typed_model.model_validate(event)

    assert public_event.event_type == expected_event_type
    assert typed_event.event_type == expected_event_type
    assert public_event.metadata.simulated is True


def test_valid_process_measurement_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_measurement_recorded.json")

    validated = validate_event(event)

    assert validated.event_type == "process.measurement.recorded"
    assert validated.payload.signal_id == "fill_weight"
    assert validated.payload.tag_name == "asset_filler_1.fill_weight"
    assert validated.payload.normal_min == 495.0
    assert validated.payload.normal_max == 505.0
    assert validated.payload.target_value == 500.0
    assert validated.metadata.simulated is True


def test_valid_temperature_process_signal_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_temperature_signal.json")

    validated = validate_event(event)
    process_signal = ProcessSignalEvent.model_validate(event)

    assert validated.event_type == "process.measurement.recorded"
    assert process_signal.payload.signal_id == "filler_temperature"
    assert process_signal.payload.tag_name == "asset_filler_1.filler_temperature"
    assert process_signal.payload.value == 68.4
    assert process_signal.payload.unit == "deg_c"
    assert process_signal.payload.quality == "good"
    assert process_signal.payload.normal_min == 65.0
    assert process_signal.payload.normal_max == 72.0
    assert process_signal.payload.target_value == 68.0


def test_valid_pressure_process_signal_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_pressure_signal.json")

    validated = ProcessSignalEvent.model_validate(event)

    assert validated.payload.signal_id == "filler_nozzle_pressure"
    assert validated.payload.tag_name == "asset_filler_1.filler_nozzle_pressure"
    assert validated.payload.value == 2.12
    assert validated.payload.unit == "bar"
    assert validated.payload.quality == "good"
    assert validated.payload.normal_min is None
    assert validated.payload.normal_max is None
    assert validated.payload.target_value is None


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
    assert validated.payload.tag_name == "asset_filler_1.fill_weight"


def test_valid_quality_measurement_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_measurement_recorded.json")

    validated = validate_event(event)

    assert validated.event_type == "quality.measurement.recorded"
    assert validated.context.batch_id == "batch_demo_1001"
    assert validated.context.work_order_id == "wo_1001"
    assert validated.payload.quality_check_type == "inline_check"
    assert validated.payload.value == 501.0
    assert validated.payload.result_status == "pass"
    assert validated.payload.result == "pass"
    assert validated.payload.severity == "low"
    assert validated.payload.spec_min == 495.0
    assert validated.payload.spec_max == 505.0


def test_valid_in_spec_quality_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_in_spec_result.json")

    validated = validate_event(event)
    quality_event = QualityEvent.model_validate(event)

    assert validated.event_type == "quality.measurement.recorded"
    assert quality_event.context.batch_id == "batch_demo_1001"
    assert quality_event.context.work_order_id == "wo_1001"
    assert quality_event.payload.quality_check_type == "inline_check"
    assert quality_event.payload.value == 501.0
    assert quality_event.payload.result_status == "pass"
    assert quality_event.payload.severity == "low"
    assert quality_event.payload.spec_min == 495.0
    assert quality_event.payload.spec_max == 505.0


def test_valid_out_of_spec_quality_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_out_of_spec_result.json")

    validated = QualityEvent.model_validate(event)

    assert validated.context.batch_id == "batch_demo_1001"
    assert validated.context.work_order_id == "wo_1001"
    assert validated.payload.quality_check_type == "inspection"
    assert validated.payload.value == 509.8
    assert validated.payload.result_status == "fail"
    assert validated.payload.result == "fail"
    assert validated.payload.severity == "high"


def test_quality_event_allows_missing_optional_specification_limits() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_visual_inspection.json")

    validated = QualityEvent.model_validate(event)

    assert validated.payload.quality_check_type == "inspection"
    assert validated.payload.result_status == "pass"
    assert validated.payload.spec_min is None
    assert validated.payload.spec_max is None


def test_valid_batch_started_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "batch_started.json")

    validated = validate_event(event)
    batch_event = BatchEvent.model_validate(event)

    assert validated.event_type == "production.batch.started"
    assert batch_event.payload.batch_id == "batch_demo_1001"
    assert batch_event.payload.lot_id == "lot_demo_20260101"
    assert batch_event.payload.product_id == "prod_demo_tablets"
    assert batch_event.payload.material_id == "mat_demo_blend"
    assert batch_event.payload.work_order_id == "wo_1001"
    assert batch_event.payload.previous_status == "planned"
    assert batch_event.payload.status == "started"


def test_valid_batch_completed_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "batch_completed.json")

    validated = BatchEvent.model_validate(event)

    assert validated.event_type == "production.batch.completed"
    assert validated.payload.previous_status == "started"
    assert validated.payload.status == "completed"


def test_valid_work_order_started_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "work_order_started.json")

    validated = validate_event(event)
    work_order_event = WorkOrderEvent.model_validate(event)

    assert validated.event_type == "production.work_order.started"
    assert work_order_event.payload.work_order_id == "wo_1001"
    assert work_order_event.payload.product_id == "prod_demo_tablets"
    assert work_order_event.payload.material_id == "mat_demo_blend"
    assert work_order_event.payload.batch_id == "batch_demo_1001"
    assert work_order_event.payload.lot_id == "lot_demo_20260101"
    assert work_order_event.payload.previous_status == "planned"
    assert work_order_event.payload.status == "started"


def test_valid_work_order_completed_event_contract() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "work_order_completed.json")

    validated = WorkOrderEvent.model_validate(event)

    assert validated.event_type == "production.work_order.completed"
    assert validated.payload.previous_status == "started"
    assert validated.payload.status == "completed"


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


def test_process_signal_missing_tag_name_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "process_signal_missing_tag_name.json")

    with pytest.raises(ValidationError, match="tag_name"):
        validate_event(event)


def test_process_signal_missing_value_is_rejected() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_temperature_signal.json")
    del event["payload"]["value"]

    with pytest.raises(ValidationError, match="value"):
        validate_event(event)


def test_process_signal_invalid_value_type_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "process_signal_invalid_value.json")

    with pytest.raises(ValidationError, match="value"):
        validate_event(event)


def test_process_signal_normal_range_requires_min_less_than_max() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_temperature_signal.json")
    event["payload"]["normal_min"] = 72.0
    event["payload"]["normal_max"] = 65.0

    with pytest.raises(ValidationError, match="normal_min must be less than normal_max"):
        validate_event(event)


def test_process_signal_normal_range_requires_both_limits() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "process_temperature_signal.json")
    del event["payload"]["normal_max"]

    with pytest.raises(ValidationError, match="normal_min and normal_max"):
        validate_event(event)


def test_quality_event_missing_check_type_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "quality_missing_check_type.json")

    with pytest.raises(ValidationError, match="quality_check_type"):
        validate_event(event)


def test_quality_event_missing_result_status_is_rejected() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_in_spec_result.json")
    del event["payload"]["result_status"]

    with pytest.raises(ValidationError, match="result_status"):
        validate_event(event)


def test_quality_event_invalid_severity_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "quality_invalid_severity.json")

    with pytest.raises(ValidationError, match="severity"):
        validate_event(event)


def test_quality_event_specification_limits_require_min_less_than_max() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_in_spec_result.json")
    event["payload"]["spec_min"] = 505.0
    event["payload"]["spec_max"] = 495.0

    with pytest.raises(ValidationError, match="spec_min must be less than spec_max"):
        validate_event(event)


def test_quality_event_specification_limits_require_both_bounds() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "quality_in_spec_result.json")
    del event["payload"]["spec_max"]

    with pytest.raises(ValidationError, match="spec_min and spec_max"):
        validate_event(event)


def test_batch_event_missing_required_identifiers_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "batch_missing_lot_id.json")

    with pytest.raises(ValidationError, match="lot_id"):
        validate_event(event)


def test_work_order_event_missing_required_identifiers_is_rejected() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "work_order_started.json")
    del event["payload"]["work_order_id"]

    with pytest.raises(ValidationError, match="work_order_id"):
        validate_event(event)


def test_invalid_batch_status_value_is_rejected() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "batch_started.json")
    event["payload"]["status"] = "running"

    with pytest.raises(ValidationError, match="status"):
        validate_event(event)


def test_invalid_work_order_status_value_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "work_order_invalid_status.json")

    with pytest.raises(ValidationError, match="status"):
        validate_event(event)


def test_batch_event_status_must_match_lifecycle_event_type() -> None:
    event = load_fixture(FIXTURES / "valid-events" / "batch_completed.json")
    event["payload"]["status"] = "started"

    with pytest.raises(ValidationError, match="payload.status must be completed"):
        validate_event(event)


def test_unknown_event_type_is_rejected() -> None:
    event = load_fixture(FIXTURES / "invalid-events" / "unknown_event_type.json")

    with pytest.raises(UnsupportedEventTypeError, match="unsupported event_type: asset.teleported"):
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
