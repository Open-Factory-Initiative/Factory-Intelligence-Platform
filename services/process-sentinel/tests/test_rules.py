from __future__ import annotations

from factory_simulator import generate_events
from process_sentinel import run_sentinel
from process_sentinel.storage import SentinelStateStore


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


def test_fill_weight_drift_demo_supports_detection_recommendation_and_rca_draft(tmp_path):
    result = run_sentinel(generate_events("fill_weight_drift_demo", seed=120, count=30))

    detection = next(item for item in result.detections if item.detection_type == "quality_drift")
    recommendation = next(
        item for item in result.recommendations if item.detection_id == detection.detection_id
    )
    evidence = [
        item for item in result.evidence_items if item.detection_id == detection.detection_id
    ]
    store = SentinelStateStore(tmp_path)
    store.save_run_result(result)
    draft = store.build_rca_capa_draft(detection.detection_id)

    assert [item.detection_type for item in result.detections] == ["quality_drift"]
    assert detection.detection_id == "det_fill_weight_gradual_drift"
    assert detection.related_work_order_id == "wo_demo_fill_weight_1001"
    assert detection.related_asset_ids == ["asset_filler_1"]
    assert detection.confidence > 0.7
    assert len(evidence) >= 2
    assert recommendation.status == "needs_review"
    assert recommendation.requires_approval is True
    assert recommendation.evidence_ids == [item.evidence_id for item in evidence]
    assert draft is not None
    assert draft.detection_id == detection.detection_id
    assert draft.evidence_summary
    assert draft.recommended_containment == recommendation.recommended_action
