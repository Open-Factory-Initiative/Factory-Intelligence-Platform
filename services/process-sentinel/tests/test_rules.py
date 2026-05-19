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
    assert detection.summary == (
        "Advisory: fill weight is trending upward, which may move the affected "
        "work order toward the upper quality limit."
    )
    assert "root cause" not in detection.summary.lower()
    assert "caused by" not in detection.summary.lower()
    assert detection.severity == "medium"
    assert detection.related_work_order_id == "WO-DEMO-1007"
    assert detection.related_asset_ids == ["filler_f_201"]
    assert detection.confidence > 0.7
    assert len(evidence) >= 2
    assert [item.timestamp for item in evidence] == sorted(item.timestamp for item in evidence)
    assert [item.evidence_type for item in evidence] == ["process_signal", "quality_result"]
    assert all(item.title for item in evidence)
    assert all(item.description for item in evidence)
    assert all(item.source_event_ids for item in evidence)
    assert all(0.0 <= item.score <= 1.0 for item in evidence)
    assert "Baseline average" in evidence[0].description
    assert "recent average" in evidence[0].description
    assert "process signal" in evidence[1].description
    assert "quality" in evidence[1].title.lower()
    assert recommendation.status == "needs_review"
    assert recommendation.requires_approval is True
    assert recommendation.evidence_ids == [item.evidence_id for item in evidence]
    assert draft is not None
    assert draft.detection_id == detection.detection_id
    assert draft.title == f"RCA/CAPA draft for {detection.summary}"
    assert draft.problem_statement == detection.summary
    assert draft.evidence_summary == [item.description for item in evidence]
    assert draft.recommended_containment == recommendation.recommended_action
    assert "root cause" in draft.capa_placeholder
    assert "corrective action" in draft.capa_placeholder
    assert "preventive action" in draft.capa_placeholder
    assert draft.human_review_required is True
