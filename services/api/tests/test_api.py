from __future__ import annotations

from pathlib import Path

from factory_api.main import create_app
from factory_ingestion.storage import JsonlEventStore
from factory_simulator import generate_events
from fastapi.testclient import TestClient
from process_sentinel import SentinelStateStore, run_sentinel


def seed_state(tmp_path: Path) -> tuple[Path, Path]:
    events_store_path = tmp_path / "events.jsonl"
    state_dir = tmp_path / "sentinel"
    events = generate_events("fill_weight_drift_demo", seed=120, count=30)
    event_store = JsonlEventStore(events_store_path)
    for event in events:
        event_store.append(event)
    SentinelStateStore(state_dir).save_run_result(run_sentinel(events))
    return events_store_path, state_dir


def test_health_endpoint(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_event_and_detection_query_endpoints(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )

    events_response = client.get("/events?event_type=process.measurement.recorded")
    detections_response = client.get("/sentinel/detections")

    assert events_response.status_code == 200
    assert len(events_response.json()) > 0
    assert detections_response.status_code == 200
    assert detections_response.json()[0]["status"] == "recommendation_created"


def test_demo_detection_detail_endpoint_exposes_expected_lookup_fields(
    tmp_path: Path,
) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )

    list_response = client.get("/sentinel/detections")
    detail_response = client.get("/sentinel/detections/det_fill_weight_gradual_drift")

    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert [item["detection_id"] for item in list_response.json()] == [
        "det_fill_weight_gradual_drift"
    ]
    assert detail_response.json()["detection_id"] == "det_fill_weight_gradual_drift"
    assert detail_response.json()["summary"] == (
        "Advisory: fill weight is trending upward, which may move the affected "
        "work order toward the upper quality limit."
    )
    assert "root cause" not in detail_response.json()["summary"].lower()
    assert "caused by" not in detail_response.json()["summary"].lower()
    assert detail_response.json()["severity"] == "medium"
    assert detail_response.json()["confidence"] > 0.7
    assert detail_response.json()["related_work_order_id"] == "WO-DEMO-1007"
    assert detail_response.json()["related_asset_ids"] == ["filler_f_201"]


def test_domain_model_query_endpoints(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )

    site_response = client.get("/sites/greenville_demo_site")
    signal_response = client.get("/process-signals/fill_weight")
    quality_response = client.get("/quality-results?batch_id=BATCH-DEMO-1007")
    investigation_response = client.get("/investigations/inv_fill_weight_drift_WO_DEMO_1007")

    assert site_response.status_code == 200
    assert site_response.json()["name"] == "Greenville Demo Site"
    assert signal_response.status_code == 200
    assert signal_response.json()["equipment_id"] == "filler_f_201"
    assert quality_response.status_code == 200
    assert quality_response.json()[0]["batch_id"] == "BATCH-DEMO-1007"
    assert quality_response.json()[0]["related_signal_ids"] == [
        "fill_weight",
        "filler_nozzle_pressure",
    ]
    assert investigation_response.status_code == 200
    assert investigation_response.json()["deviation"]["deviation_id"] == (
        "dev_fill_weight_drift_WO_DEMO_1007"
    )


def test_missing_event_uses_documented_error_shape(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )

    response = client.get("/events/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "event_not_found",
            "message": "Event not found: does-not-exist",
        }
    }


def test_missing_domain_object_uses_documented_error_shape(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )

    response = client.get("/equipment/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "equipment_not_found",
            "message": "Equipment not found: does-not-exist",
        }
    }


def test_recommendation_approval_creates_decision_and_updates_status(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )
    recommendation = client.get("/recommendations").json()[0]

    response = client.post(
        f"/recommendations/{recommendation['recommendation_id']}/approve",
        json={"reviewer": "quality_engineer", "reason": "Evidence supports containment."},
    )
    updated = client.get(f"/recommendations/{recommendation['recommendation_id']}").json()

    assert response.status_code == 200
    assert response.json()["decision"] == "approved"
    assert updated["status"] == "approved"


def test_rca_capa_draft_uses_detection_evidence_and_recommendation(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_state(tmp_path)
    client = TestClient(
        create_app(events_store_path=events_store_path, sentinel_state_dir=state_dir)
    )
    detection = client.get("/sentinel/detections").json()[0]

    response = client.get(f"/reports/rca-capa-drafts/{detection['detection_id']}")

    assert response.status_code == 200
    assert response.json()["detection_id"] == detection["detection_id"]
    assert response.json()["evidence_summary"]
