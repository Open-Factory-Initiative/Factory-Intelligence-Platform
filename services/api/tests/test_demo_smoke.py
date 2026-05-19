from __future__ import annotations

from pathlib import Path

from factory_api.demo_smoke import main, run_demo_api_smoke
from factory_ingestion.storage import JsonlEventStore
from factory_simulator import generate_events
from process_sentinel import SentinelStateStore, run_sentinel


def seed_demo_state(tmp_path: Path) -> tuple[Path, Path]:
    events_store_path = tmp_path / "fill_weight_drift_demo_events.jsonl"
    state_dir = tmp_path / "fill_weight_drift_demo_sentinel"
    events = generate_events("fill_weight_drift_demo", seed=120, count=30)
    event_store = JsonlEventStore(events_store_path)
    for event in events:
        event_store.append(event)
    SentinelStateStore(state_dir).save_run_result(run_sentinel(events))
    return events_store_path, state_dir


def test_demo_api_smoke_validates_backend_demo_path(tmp_path: Path) -> None:
    events_store_path, state_dir = seed_demo_state(tmp_path)

    result = run_demo_api_smoke(events_store_path, state_dir)
    recommendation = SentinelStateStore(state_dir).get_recommendation(
        "rec_fill_weight_gradual_drift"
    )

    assert result.event_count == 70
    assert result.evidence_count == 2
    assert result.recommendation_id == "rec_fill_weight_gradual_drift"
    assert result.decision == "deferred"
    assert result.rca_capa_draft_id == "det_fill_weight_gradual_drift"
    assert recommendation is not None
    assert recommendation.status == "needs_review"


def test_demo_api_smoke_fails_clearly_when_state_is_missing(
    tmp_path: Path,
    capsys,
) -> None:
    exit_code = main(
        [
            "--events-store",
            str(tmp_path / "missing_events.jsonl"),
            "--sentinel-state-dir",
            str(tmp_path / "missing_sentinel"),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "demo api smoke failed: Missing demo events store" in captured.err
    assert "Run make demo-data, make demo-ingest, and make demo-sentinel-run first" in (
        captured.err
    )
