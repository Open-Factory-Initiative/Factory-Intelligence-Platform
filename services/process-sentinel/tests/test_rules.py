from __future__ import annotations

from factory_simulator import generate_events
from process_sentinel import run_sentinel


def test_normal_scenario_does_not_create_detection() -> None:
    result = run_sentinel(generate_events("normal", seed=42, count=24))

    assert result.detections == []
    assert result.recommendations == []


def test_gradual_drift_creates_evidence_backed_recommendation() -> None:
    result = run_sentinel(generate_events("gradual_drift", seed=42, count=24))

    detection = next(item for item in result.detections if item.detection_type == "quality_drift")
    recommendation = next(
        item for item in result.recommendations if item.detection_id == detection.detection_id
    )

    assert detection.severity == "medium"
    assert detection.confidence > 0.7
    assert recommendation.status == "needs_review"
    assert recommendation.requires_approval is True
    assert recommendation.evidence_ids


def test_sudden_excursion_creates_high_severity_detection() -> None:
    result = run_sentinel(generate_events("sudden_excursion", seed=42, count=24))

    detection = next(
        item for item in result.detections if item.detection_type == "process_excursion"
    )

    assert detection.severity == "high"
    assert detection.confidence == 0.9


def test_missing_data_does_not_create_false_positive() -> None:
    result = run_sentinel(generate_events("gradual_drift", seed=42, count=6))

    assert result.detections == []
