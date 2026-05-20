from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNBOOK = REPO_ROOT / "docs" / "demo" / "MANUFACTURER_DEMO_RUNBOOK.md"
README = REPO_ROOT / "README.md"
WEB_README = REPO_ROOT / "apps" / "web" / "README.md"


def _content() -> str:
    return RUNBOOK.read_text(encoding="utf-8")


def test_manufacturer_demo_runbook_exists_and_is_linked() -> None:
    assert RUNBOOK.exists()

    runbook_path = "docs/demo/MANUFACTURER_DEMO_RUNBOOK.md"
    assert runbook_path in README.read_text(encoding="utf-8")
    assert "../../docs/demo/MANUFACTURER_DEMO_RUNBOOK.md" in WEB_README.read_text(
        encoding="utf-8"
    )


def test_manufacturer_demo_runbook_covers_required_demo_commands_and_outputs() -> None:
    content = _content()

    expected_terms = [
        "make demo",
        "make demo-reset",
        "make demo-data",
        "make demo-ingest",
        "make demo-sentinel-run",
        "make demo-api-smoke",
        "make api",
        "EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl",
        "SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel",
        "cd apps/web",
        "npm run dev",
        "wrote 70 events",
        "accepted_events: 70",
        "rejected_events: 0",
        "dead_letter_count: 0",
        "sentinel complete: detections=1 evidence=2 recommendations=1",
        "demo api smoke passed",
    ]

    for term in expected_terms:
        assert term in content


def test_manufacturer_demo_runbook_covers_expected_urls_and_artifacts() -> None:
    content = _content()

    expected_terms = [
        "http://127.0.0.1:8000/docs",
        "http://127.0.0.1:8000/sentinel/detections",
        "http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift",
        (
            "http://127.0.0.1:8000/sentinel/detections/"
            "det_fill_weight_gradual_drift/evidence"
        ),
        "http://127.0.0.1:8000/recommendations",
        "http://127.0.0.1:8000/recommendations/rec_fill_weight_gradual_drift",
        (
            "http://127.0.0.1:8000/reports/rca-capa-drafts/"
            "det_fill_weight_gradual_drift"
        ),
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3000/detections",
        "http://127.0.0.1:3000/detections/det_fill_weight_gradual_drift",
        (
            "http://127.0.0.1:3000/recommendations?detection_id="
            "det_fill_weight_gradual_drift"
        ),
        (
            "http://127.0.0.1:3000/rca-capa-draft?detection_id="
            "det_fill_weight_gradual_drift"
        ),
        "det_fill_weight_gradual_drift",
        "rec_fill_weight_gradual_drift",
        "WO-DEMO-1007",
        "filler_f_201",
    ]

    for term in expected_terms:
        assert term in content


def test_manufacturer_demo_runbook_covers_safety_script_and_feedback_requirements() -> None:
    content = _content()

    required_phrases = [
        "simulator-backed demo data",
        "advisory and human-reviewed",
        "Pre-Call Checklist",
        "8-10 Minute Talk Track",
        "What Not To Claim",
        "Troubleshooting",
        "Post-Demo Discussion Prompts",
        "human-reviewed decision support",
        "governed recommendations",
        "future site validation work would be required before production use",
        "not perform autonomous control",
        "does not create or close",
    ]

    for phrase in required_phrases:
        assert phrase in content
