from __future__ import annotations

from factory_simulator import generate_events


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
