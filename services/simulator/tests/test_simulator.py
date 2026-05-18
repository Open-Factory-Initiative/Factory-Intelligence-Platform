from __future__ import annotations

import pytest
from factory_simulator import (
    SCENARIOS,
    SUPPORTED_SCENARIO_TYPES,
    ScenarioDefinition,
    generate_events,
    scenario_definition_for,
)
from pydantic import ValidationError


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
    assert SCENARIOS == ("normal", "gradual_drift", "sudden_excursion")
    assert SUPPORTED_SCENARIO_TYPES == (
        "normal",
        "gradual_drift",
        "sudden_excursion",
        "noisy_sensor",
    )


def test_simulator_output_is_deterministic_for_seed() -> None:
    first = generate_events("gradual_drift", seed=42, count=12)
    second = generate_events("gradual_drift", seed=42, count=12)

    assert [event.model_dump(mode="json") for event in first] == [
        event.model_dump(mode="json") for event in second
    ]


def test_gradual_drift_trends_fill_weight_upward() -> None:
    events = generate_events("gradual_drift", seed=42, count=24)
    fill_values = [
        event.payload.value
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "fill_weight"
    ]

    assert max(fill_values[-6:]) - min(fill_values[:6]) > 3.0


def test_sudden_excursion_contains_known_out_of_spec_quality_result() -> None:
    events = generate_events("sudden_excursion", seed=42, count=15)
    quality_results = [
        event.payload.result
        for event in events
        if event.event_type == "quality.measurement.recorded"
    ]

    assert "fail" in quality_results
