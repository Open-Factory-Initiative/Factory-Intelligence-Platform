import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def run_make(target: str, variables: list[str]) -> str:
    result = subprocess.run(
        ["make", target, *variables],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


def test_demo_make_targets_reset_generate_ingest_and_run_sentinel(
    tmp_path: Path,
) -> None:
    demo_output = tmp_path / "events" / "fill_weight_drift_demo.jsonl"
    demo_events_store = tmp_path / "storage" / "fill_weight_drift_demo_events.jsonl"
    demo_dead_letter = tmp_path / "storage" / "fill_weight_drift_demo_dead_letter.jsonl"
    demo_state_dir = tmp_path / "storage" / "fill_weight_drift_demo_sentinel"
    variables = [
        f"DEMO_OUTPUT={demo_output}",
        f"DEMO_EVENTS_STORE={demo_events_store}",
        f"DEMO_DEAD_LETTER={demo_dead_letter}",
        f"DEMO_SENTINEL_STATE_DIR={demo_state_dir}",
    ]

    demo_output.parent.mkdir(parents=True)
    demo_events_store.parent.mkdir(parents=True)
    demo_state_dir.mkdir(parents=True)
    demo_output.write_text("stale simulator output\n", encoding="utf-8")
    demo_events_store.write_text("stale event store\n", encoding="utf-8")
    demo_dead_letter.write_text("stale dead letter\n", encoding="utf-8")
    (demo_state_dir / "detections.json").write_text("[]\n", encoding="utf-8")

    reset_output = run_make("demo-reset", variables)

    assert not demo_output.exists()
    assert not demo_events_store.exists()
    assert not demo_dead_letter.exists()
    assert not demo_state_dir.exists()
    assert "Demo generated state cleared." in reset_output
    assert "Next: make demo-data" in reset_output

    data_output = run_make("demo-data", variables)

    assert demo_output.exists()
    assert len(demo_output.read_text(encoding="utf-8").splitlines()) == 70
    assert "wrote 70 events" in data_output
    assert "Next: make demo-ingest" in data_output

    ingest_output = run_make("demo-ingest", variables)

    assert demo_events_store.exists()
    assert "accepted_events: 70" in ingest_output
    assert "Next: make demo-sentinel-run" in ingest_output

    sentinel_output = run_make("demo-sentinel-run", variables)

    assert (demo_state_dir / "detections.json").exists()
    assert "sentinel complete: detections=1 evidence=2 recommendations=1" in (
        sentinel_output
    )
    assert "Next: make api" in sentinel_output


def test_demo_make_target_prepares_state_and_prints_startup_instructions(
    tmp_path: Path,
) -> None:
    demo_output = tmp_path / "events" / "fill_weight_drift_demo.jsonl"
    demo_events_store = tmp_path / "storage" / "fill_weight_drift_demo_events.jsonl"
    demo_dead_letter = tmp_path / "storage" / "fill_weight_drift_demo_dead_letter.jsonl"
    demo_state_dir = tmp_path / "storage" / "fill_weight_drift_demo_sentinel"
    variables = [
        f"DEMO_OUTPUT={demo_output}",
        f"DEMO_EVENTS_STORE={demo_events_store}",
        f"DEMO_DEAD_LETTER={demo_dead_letter}",
        f"DEMO_SENTINEL_STATE_DIR={demo_state_dir}",
    ]

    output = run_make("demo", variables)

    assert demo_output.exists()
    assert demo_events_store.exists()
    assert demo_dead_letter.exists()
    assert (demo_state_dir / "detections.json").exists()
    assert "demo api smoke passed" in output
    assert "Demo state is ready." in output
    assert "Expected detection ID: det_fill_weight_gradual_drift" in output
    assert "Expected recommendation ID: rec_fill_weight_gradual_drift" in output
    assert (
        f"make api EVENTS_STORE={demo_events_store} "
        f"SENTINEL_STATE_DIR={demo_state_dir}"
    ) in output
    assert "cd apps/web && npm run dev" in output
    assert "http://127.0.0.1:8000/sentinel/detections" in output
    assert (
        "http://127.0.0.1:8000/sentinel/detections/"
        "det_fill_weight_gradual_drift"
    ) in output
    assert "http://127.0.0.1:3000" in output
    assert (
        "http://127.0.0.1:3000/rca-capa-draft?"
        "detection_id=det_fill_weight_gradual_drift"
    ) in output
