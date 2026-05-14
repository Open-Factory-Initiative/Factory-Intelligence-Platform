from __future__ import annotations

from datetime import UTC, datetime, timedelta
from random import Random
from typing import Literal

from factory_events import (
    EventContext,
    EventEnvelope,
    EventMetadata,
    EventSource,
    ProcessMeasurementPayload,
    QualityMeasurementPayload,
)

ScenarioName = Literal["normal", "gradual_drift", "sudden_excursion"]
SCENARIOS: tuple[ScenarioName, ...] = ("normal", "gradual_drift", "sudden_excursion")

DEMO_CONTEXT = {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "asset_id": "asset_filler_1",
    "work_order_id": "wo_1001",
}

DEMO_ASSETS = (
    "asset_filler_1",
    "asset_checkweigher_1",
    "asset_case_packer_1",
)


def generate_events(
    scenario: ScenarioName,
    *,
    seed: int = 42,
    count: int = 24,
    start: datetime | None = None,
) -> list[EventEnvelope]:
    if scenario not in SCENARIOS:
        msg = f"unsupported scenario: {scenario}"
        raise ValueError(msg)
    if count < 6:
        msg = "count must be at least 6 so drift windows are meaningful"
        raise ValueError(msg)

    rng = Random(seed)
    start_time = start or datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    events: list[EventEnvelope] = []

    for index in range(count):
        timestamp = start_time + timedelta(minutes=index)
        fill_weight = _fill_weight_for_scenario(scenario, index, rng)
        pressure = _pressure_for_scenario(scenario, index, rng)
        events.append(
            _process_event(
                event_id=f"evt_{scenario}_fill_{index:04d}",
                source_event_id=f"sim-{scenario}-fill-{index:04d}",
                trace_id=f"trace_{scenario}_{index:04d}",
                timestamp=timestamp,
                signal_id="fill_weight",
                signal_name="Fill Weight",
                value=fill_weight,
                unit="g",
                asset_id="asset_filler_1",
            )
        )
        events.append(
            _process_event(
                event_id=f"evt_{scenario}_pressure_{index:04d}",
                source_event_id=f"sim-{scenario}-pressure-{index:04d}",
                trace_id=f"trace_{scenario}_{index:04d}",
                timestamp=timestamp,
                signal_id="filler_nozzle_pressure",
                signal_name="Filler Nozzle Pressure",
                value=pressure,
                unit="bar",
                asset_id="asset_filler_1",
            )
        )

        if index % 3 == 2:
            result = "pass" if 495.0 <= fill_weight <= 505.0 else "fail"
            events.append(
                _quality_event(
                    event_id=f"evt_{scenario}_quality_{index:04d}",
                    source_event_id=f"sim-{scenario}-quality-{index:04d}",
                    trace_id=f"trace_{scenario}_{index:04d}",
                    timestamp=timestamp + timedelta(seconds=20),
                    value=round(fill_weight + rng.uniform(-0.2, 0.2), 3),
                    result=result,
                )
            )

    return events


def _fill_weight_for_scenario(scenario: ScenarioName, index: int, rng: Random) -> float:
    noise = rng.uniform(-0.25, 0.25)
    if scenario == "normal":
        return round(500.0 + noise, 3)
    if scenario == "gradual_drift":
        drift = max(0, index - 7) * 0.33
        return round(500.0 + drift + noise, 3)
    if 10 <= index <= 12:
        return round(509.5 + rng.uniform(-0.5, 0.5), 3)
    return round(500.0 + noise, 3)


def _pressure_for_scenario(scenario: ScenarioName, index: int, rng: Random) -> float:
    noise = rng.uniform(-0.04, 0.04)
    if scenario == "gradual_drift":
        return round(2.1 + max(0, index - 7) * 0.025 + noise, 3)
    if scenario == "sudden_excursion" and 10 <= index <= 12:
        return round(2.8 + rng.uniform(-0.08, 0.08), 3)
    return round(2.1 + noise, 3)


def _process_event(
    *,
    event_id: str,
    source_event_id: str,
    trace_id: str,
    timestamp: datetime,
    signal_id: str,
    signal_name: str,
    value: float,
    unit: str,
    asset_id: str,
) -> EventEnvelope:
    context = DEMO_CONTEXT | {"asset_id": asset_id}
    return EventEnvelope(
        event_id=event_id,
        event_type="process.measurement.recorded",
        schema_version="1.0.0",
        timestamp=timestamp,
        source=EventSource(
            system="factory-simulator",
            adapter="simulator",
            source_event_id=source_event_id,
        ),
        context=EventContext(**context),
        payload=ProcessMeasurementPayload(
            signal_id=signal_id,
            signal_name=signal_name,
            tag_name=f"{asset_id}.{signal_id}",
            value=value,
            unit=unit,
            quality="good",
        ),
        metadata=EventMetadata(simulated=True, trace_id=trace_id),
    )


def _quality_event(
    *,
    event_id: str,
    source_event_id: str,
    trace_id: str,
    timestamp: datetime,
    value: float,
    result: Literal["pass", "fail"],
) -> EventEnvelope:
    return EventEnvelope(
        event_id=event_id,
        event_type="quality.measurement.recorded",
        schema_version="1.0.0",
        timestamp=timestamp,
        source=EventSource(
            system="factory-simulator",
            adapter="simulator",
            source_event_id=source_event_id,
        ),
        context=EventContext(**DEMO_CONTEXT),
        payload=QualityMeasurementPayload(
            quality_check_type="inline_check",
            measurement_name="Final Fill Weight",
            value=value,
            unit="g",
            result_status=result,
            result=result,
            severity="high" if result == "fail" else "low",
            spec_min=495.0,
            spec_max=505.0,
        ),
        metadata=EventMetadata(simulated=True, trace_id=trace_id),
    )
