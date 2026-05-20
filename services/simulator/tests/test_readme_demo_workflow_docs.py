from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
README = REPO_ROOT / "README.md"


def _content() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_has_run_the_demo_section_with_commands_and_links() -> None:
    content = _content()

    required_terms = [
        "## Run the demo",
        "make demo",
        "make demo-reset",
        "make demo-data",
        "make demo-ingest",
        "make demo-sentinel-run",
        "make demo-api-smoke",
        (
            "make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl "
            "SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel"
        ),
        "cd apps/web",
        "npm run dev",
        "http://127.0.0.1:3000",
        "docs/DEMO_RUNBOOK.md",
        "docs/demo/MANUFACTURER_DEMO_RUNBOOK.md",
        "docs/demo/PRE_DEMO_CHECKLIST.md",
        "docs/demo/TROUBLESHOOTING.md",
    ]

    for term in required_terms:
        assert term in content


def test_readme_demo_section_explains_expected_outputs_and_proof_points() -> None:
    content = _content()

    required_terms = [
        "accepted_events: 70",
        "dead_letter_count: 0",
        "sentinel complete: detections=1 evidence=2 recommendations=1",
        "demo api smoke passed",
        "det_fill_weight_gradual_drift",
        "rec_fill_weight_gradual_drift",
        "deterministic synthetic factory scenario is generated and ingested",
        "one clear fill-weight drift detection",
        "readable evidence timeline",
        "governed recommendation",
        "human approve, reject, or defer",
        "RCA/CAPA draft preview",
    ]

    for term in required_terms:
        assert term in content


def test_readme_demo_section_preserves_demo_boundaries_and_post_demo_scope() -> None:
    content = _content()

    required_terms = [
        "simulator-backed",
        "does not connect to a real plant",
        "Recommendations are advisory and human-reviewed",
        "does not perform autonomous control",
        "QMS/MES writeback",
        "compliance validation",
        "Post-demo work is still separate",
        "does not prove production readiness",
        "validated GxP use",
        "authentication/RBAC",
        "enterprise audit controls",
        "real plant integration",
        "cloud deployment",
        "closed-loop industrial writeback",
    ]

    for term in required_terms:
        assert term in content
