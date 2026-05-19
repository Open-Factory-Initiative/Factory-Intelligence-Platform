from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import fmean

import pytest
from factory_events import (
    ProcessMeasurementPayload,
    QualityMeasurementPayload,
    validate_event,
)
from factory_simulator import (
    SCENARIOS,
    SUPPORTED_SCENARIO_TYPES,
    ScenarioDefinition,
    generate_events,
    scenario_definition_for,
)
from factory_simulator.cli import main as simulator_cli_main
from factory_simulator.generator import GRADUAL_DRIFT_BASELINE_SAMPLES
from pydantic import ValidationError


def expected_event_count(sample_count: int) -> int:
    return (sample_count * 2) + (sample_count // 3)


def test_valid_normal_scenario_definition_describes_generation_format() -> None:
    definition = scenario_definition_for("normal")

    assert definition.metadata.name == "normal"
    assert definition.metadata.scenario_type == "normal"
    assert definition.metadata.default_seed == 42
    assert definition.metadata.default_count >= 6
    assert definition.line_context.site_id == "site_demo"
    assert {asset.asset_id for asset in definition.assets} >= {
        "asset_filler_1",
        "asset_checkweigher_1",
    }
    assert {tag.signal_id for tag in definition.process_tags} == {
        "fill_weight",
        "filler_nozzle_pressure",
    }
    assert definition.quality_markers[0].measurement_name == "Final Fill Weight"
    assert definition.output.format == "jsonl"


def test_valid_gradual_drift_scenario_definition_includes_drift_parameters() -> None:
    definition = scenario_definition_for("gradual_drift")

    drift_by_signal = {
        tag.signal_id: tag.drift_per_step
        for tag in definition.process_tags
        if tag.drift_per_step is not None
    }

    assert definition.metadata.scenario_type == "gradual_drift"
    assert drift_by_signal == {
        "fill_weight": 0.33,
        "filler_nozzle_pressure": 0.025,
    }


def test_valid_sudden_excursion_scenario_definition_includes_excursion_parameters() -> None:
    definition = scenario_definition_for("sudden_excursion")

    excursion_by_signal = {
        tag.signal_id: tag.excursion_value
        for tag in definition.process_tags
        if tag.excursion_value is not None
    }

    assert definition.metadata.scenario_type == "sudden_excursion"
    assert excursion_by_signal == {
        "fill_weight": 509.5,
        "filler_nozzle_pressure": 2.8,
    }


def test_scenario_definition_rejects_missing_required_fields() -> None:
    payload = scenario_definition_for("normal").model_dump(mode="json")
    del payload["metadata"]["name"]

    with pytest.raises(ValidationError, match="name"):
        ScenarioDefinition.model_validate(payload)


def test_scenario_definition_rejects_invalid_scenario_type() -> None:
    payload = scenario_definition_for("normal").model_dump(mode="json")
    payload["metadata"]["scenario_type"] = "unsupported"

    with pytest.raises(ValidationError, match="scenario_type"):
        ScenarioDefinition.model_validate(payload)


def test_scenario_format_lists_current_and_future_supported_types() -> None:
    assert SCENARIOS == (
        "normal",
        "gradual_drift",
        "sudden_excursion",
        "fill_weight_drift_demo",
    )
    assert SUPPORTED_SCENARIO_TYPES == (
        "normal",
        "gradual_drift",
        "sudden_excursion",
        "noisy_sensor",
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_same_seed_and_scenario_produce_identical_output(scenario: str) -> None:
    first = generate_events(scenario, seed=42, count=12)
    second = generate_events(scenario, seed=42, count=12)

    assert [event.model_dump(mode="json") for event in first] == [
        event.model_dump(mode="json") for event in second
    ]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_different_seeds_produce_different_valid_output(scenario: str) -> None:
    seed_42_events = generate_events(scenario, seed=42, count=12)
    seed_43_events = generate_events(scenario, seed=43, count=12)

    assert [event.model_dump(mode="json") for event in seed_42_events] != [
        event.model_dump(mode="json") for event in seed_43_events
    ]
    for event in seed_43_events:
        validated = validate_event(event.model_dump(mode="json"))
        assert validated.event_id == event.event_id


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario_events_have_expected_count_and_timing(scenario: str) -> None:
    start = datetime(2026, 2, 1, 8, 0, tzinfo=UTC)
    sample_count = 12
    events = generate_events(scenario, seed=42, count=sample_count, start=start)

    process_events = [
        event for event in events if event.event_type == "process.measurement.recorded"
    ]
    quality_events = [
        event for event in events if event.event_type == "quality.measurement.recorded"
    ]

    assert len(events) == expected_event_count(sample_count)
    assert len(process_events) == sample_count * 2
    assert len(quality_events) == sample_count // 3
    assert {event.timestamp for event in process_events} == {
        start + timedelta(minutes=index) for index in range(sample_count)
    }
    assert [event.timestamp for event in quality_events] == [
        start + timedelta(minutes=index, seconds=20)
        for index in range(2, sample_count, 3)
    ]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenario_events_are_valid_factory_events_with_stable_ids(scenario: str) -> None:
    events = generate_events(scenario, seed=42, count=12)
    event_ids = [event.event_id for event in events]
    trace_ids = {event.metadata.trace_id for event in events}

    assert len(event_ids) == len(set(event_ids))
    assert all(event.source.system == "factory-simulator" for event in events)
    assert all(event.source.adapter == "simulator" for event in events)
    assert all(event.metadata.simulated for event in events)
    assert all(trace_id.startswith(f"trace_{scenario}_") for trace_id in trace_ids)
    for event in events:
        validated = validate_event(event.model_dump(mode="json"))
        assert validated.event_id == event.event_id


def test_simulator_output_is_deterministic_for_seed() -> None:
    first = generate_events("gradual_drift", seed=42, count=12)
    second = generate_events("gradual_drift", seed=42, count=12)

    assert [event.model_dump(mode="json") for event in first] == [
        event.model_dump(mode="json") for event in second
    ]


def test_normal_scenario_output_is_deterministic_for_seed() -> None:
    first = generate_events("normal", seed=42, count=12)
    second = generate_events("normal", seed=42, count=12)

    assert [event.model_dump(mode="json") for event in first] == [
        event.model_dump(mode="json") for event in second
    ]


def test_normal_scenario_generates_expected_event_count() -> None:
    events = generate_events("normal", seed=42, count=12)

    process_events = [
        event for event in events if event.event_type == "process.measurement.recorded"
    ]
    quality_events = [
        event for event in events if event.event_type == "quality.measurement.recorded"
    ]

    assert len(events) == 28
    assert len(process_events) == 24
    assert len(quality_events) == 4


def test_normal_scenario_events_validate_against_factory_event_schema() -> None:
    events = generate_events("normal", seed=42, count=12)

    for event in events:
        validated = validate_event(event.model_dump(mode="json"))
        assert validated.event_id == event.event_id


def test_normal_scenario_values_remain_in_expected_ranges() -> None:
    definition = scenario_definition_for("normal")
    tags_by_signal = {tag.signal_id: tag for tag in definition.process_tags}
    quality_marker = definition.quality_markers[0]
    events = generate_events("normal", seed=42, count=24)

    for event in events:
        payload = event.payload
        if event.event_type == "process.measurement.recorded":
            assert isinstance(payload, ProcessMeasurementPayload)
            tag = tags_by_signal[payload.signal_id]
            assert tag.normal_min is not None
            assert tag.normal_max is not None
            assert tag.normal_min <= payload.value <= tag.normal_max
            assert payload.normal_min == tag.normal_min
            assert payload.normal_max == tag.normal_max
            assert payload.target_value == tag.target_value
        if event.event_type == "quality.measurement.recorded":
            assert isinstance(payload, QualityMeasurementPayload)
            assert quality_marker.spec_min <= payload.value <= quality_marker.spec_max
            assert payload.result == "pass"
            assert payload.spec_min == quality_marker.spec_min
            assert payload.spec_max == quality_marker.spec_max


def test_normal_scenario_can_be_written_as_jsonl(tmp_path: Path) -> None:
    output_path = tmp_path / "normal.jsonl"
    events = generate_events("normal", seed=42, count=12)

    with output_path.open("w", encoding="utf-8") as output:
        for event in events:
            output.write(json.dumps(event.model_dump(mode="json"), sort_keys=True))
            output.write("\n")

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(events)
    for line in lines:
        validate_event(json.loads(line))


def test_cli_writes_normal_scenario_jsonl(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "normal.jsonl"

    simulator_cli_main(
        [
            "--scenario",
            "normal",
            "--seed",
            "7",
            "--count",
            "6",
            "--output",
            str(output_path),
        ]
    )

    stdout = capsys.readouterr().out
    lines = output_path.read_text(encoding="utf-8").splitlines()

    assert "wrote 14 events" in stdout
    assert "scenario=normal" in stdout
    assert "seed=7" in stdout
    assert len(lines) == 14
    for line in lines:
        validate_event(json.loads(line))


def test_cli_writes_gradual_drift_with_duration_minutes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "gradual_drift.jsonl"

    simulator_cli_main(
        [
            "--scenario",
            "gradual_drift",
            "--seed",
            "42",
            "--duration-minutes",
            "9",
            "--output",
            str(output_path),
        ]
    )

    stdout = capsys.readouterr().out
    lines = output_path.read_text(encoding="utf-8").splitlines()

    assert "wrote 21 events" in stdout
    assert "count=9" in stdout
    assert len(lines) == 21
    for line in lines:
        validate_event(json.loads(line))


def test_cli_rejects_invalid_scenario_name(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "invalid.jsonl"

    with pytest.raises(SystemExit) as exc_info:
        simulator_cli_main(
            [
                "--scenario",
                "missing",
                "--output",
                str(output_path),
            ]
        )

    stderr = capsys.readouterr().err
    assert exc_info.value.code == 2
    assert "invalid choice" in stderr
    assert "normal" in stderr
    assert not output_path.exists()


def test_gradual_drift_trends_fill_weight_upward() -> None:
    events = generate_events("gradual_drift", seed=42, count=24)
    fill_values = [
        event.payload.value
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "fill_weight"
    ]

    assert max(fill_values[-6:]) - min(fill_values[:6]) > 3.0


def test_gradual_drift_starts_after_baseline_period() -> None:
    definition = scenario_definition_for("gradual_drift")
    fill_weight_tag = next(
        tag for tag in definition.process_tags if tag.signal_id == "fill_weight"
    )
    events = generate_events("gradual_drift", seed=42, count=24)
    fill_values = [
        event.payload.value
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "fill_weight"
    ]

    baseline_values = fill_values[:GRADUAL_DRIFT_BASELINE_SAMPLES]
    drift_values = fill_values[GRADUAL_DRIFT_BASELINE_SAMPLES:]

    assert fill_weight_tag.normal_min is not None
    assert fill_weight_tag.normal_max is not None
    assert all(
        fill_weight_tag.normal_min <= value <= fill_weight_tag.normal_max
        for value in baseline_values
    )
    assert drift_values[0] > fmean(baseline_values)
    assert drift_values[-1] - fmean(baseline_values) > 4.0


def test_gradual_drift_quality_concern_occurs_after_drift_begins() -> None:
    events = generate_events("gradual_drift", seed=42, count=24)
    fill_events = [
        event
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "fill_weight"
    ]
    quality_events = [
        event for event in events if event.event_type == "quality.measurement.recorded"
    ]
    drift_start_time = fill_events[GRADUAL_DRIFT_BASELINE_SAMPLES].timestamp
    failing_quality_events = [
        event for event in quality_events if event.payload.result == "fail"
    ]

    assert failing_quality_events
    assert all(event.payload.result == "pass" for event in quality_events[:-1])
    assert failing_quality_events[0].timestamp > drift_start_time


def test_gradual_drift_events_validate_against_factory_event_schema() -> None:
    events = generate_events("gradual_drift", seed=42, count=24)

    for event in events:
        validated = validate_event(event.model_dump(mode="json"))
        assert validated.event_id == event.event_id


def test_sudden_excursion_process_signals_spike_then_recover() -> None:
    definition = scenario_definition_for("sudden_excursion")
    pressure_tag = next(
        tag
        for tag in definition.process_tags
        if tag.signal_id == "filler_nozzle_pressure"
    )
    events = generate_events("sudden_excursion", seed=42, count=15)
    pressure_values = [
        event.payload.value
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "filler_nozzle_pressure"
    ]

    assert pressure_tag.normal_max is not None
    assert max(pressure_values[10:13]) > pressure_tag.normal_max
    assert all(value <= pressure_tag.normal_max for value in pressure_values[:10])
    assert all(value <= pressure_tag.normal_max for value in pressure_values[13:])


def test_sudden_excursion_contains_known_out_of_spec_quality_result() -> None:
    events = generate_events("sudden_excursion", seed=42, count=15)
    quality_results = [
        event.payload.result
        for event in events
        if event.event_type == "quality.measurement.recorded"
    ]

    assert "fail" in quality_results


def test_fill_weight_drift_demo_definition_tells_single_line_story() -> None:
    definition = scenario_definition_for("fill_weight_drift_demo")

    assert definition.metadata.name == "fill_weight_drift_demo"
    assert definition.metadata.scenario_type == "gradual_drift"
    assert definition.metadata.default_seed == 120
    assert definition.metadata.default_count == 30
    assert definition.line_context.site_id == "site_demo"
    assert definition.line_context.area_id == "area_packaging"
    assert definition.line_context.line_id == "line_1"
    assert definition.line_context.work_order_id == "wo_demo_fill_weight_1001"
    assert definition.product.product_id == "prod_demo_oral_solution"
    assert definition.product.product_name == "Demo Oral Solution"
    assert [asset.asset_id for asset in definition.assets] == ["asset_filler_1"]
    assert definition.quality_markers[0].asset_id == "asset_filler_1"
    assert definition.output.default_path == ".local/events/fill_weight_drift_demo.jsonl"


def test_fill_weight_drift_demo_output_is_deterministic_for_seed() -> None:
    first = generate_events("fill_weight_drift_demo", seed=120, count=30)
    second = generate_events("fill_weight_drift_demo", seed=120, count=30)

    assert [event.model_dump(mode="json") for event in first] == [
        event.model_dump(mode="json") for event in second
    ]


def test_fill_weight_drift_demo_has_baseline_drift_and_delayed_quality_concern() -> None:
    events = generate_events("fill_weight_drift_demo", seed=120, count=30)
    fill_events = [
        event
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "fill_weight"
    ]
    quality_events = [
        event for event in events if event.event_type == "quality.measurement.recorded"
    ]
    pressure_values = [
        event.payload.value
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "filler_nozzle_pressure"
    ]
    fill_values = [event.payload.value for event in fill_events]
    baseline_values = fill_values[:GRADUAL_DRIFT_BASELINE_SAMPLES]
    drift_values = fill_values[GRADUAL_DRIFT_BASELINE_SAMPLES:]
    failing_quality_events = [
        event for event in quality_events if event.payload.result == "fail"
    ]

    assert len(events) == expected_event_count(30)
    assert all(495.0 <= value <= 505.0 for value in baseline_values)
    assert drift_values[-1] - fmean(baseline_values) > 6.0
    assert max(pressure_values) <= 2.6
    assert failing_quality_events
    assert all(event.payload.result == "pass" for event in quality_events[:4])
    assert (
        failing_quality_events[0].timestamp
        > fill_events[GRADUAL_DRIFT_BASELINE_SAMPLES].timestamp
    )
    assert {event.context.site_id for event in events} == {"site_demo"}
    assert {event.context.area_id for event in events} == {"area_packaging"}
    assert {event.context.line_id for event in events} == {"line_1"}
    assert {event.context.work_order_id for event in events} == {"wo_demo_fill_weight_1001"}
    assert {event.context.asset_id for event in events} == {"asset_filler_1"}


def test_cli_writes_fill_weight_drift_demo_jsonl(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_path = tmp_path / "fill_weight_drift_demo.jsonl"

    simulator_cli_main(
        [
            "--scenario",
            "fill_weight_drift_demo",
            "--seed",
            "120",
            "--count",
            "30",
            "--output",
            str(output_path),
        ]
    )

    stdout = capsys.readouterr().out
    lines = output_path.read_text(encoding="utf-8").splitlines()

    assert "wrote 70 events" in stdout
    assert "scenario=fill_weight_drift_demo" in stdout
    assert "seed=120" in stdout
    assert len(lines) == 70
    for line in lines:
        validate_event(json.loads(line))
