from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKLIST = REPO_ROOT / "docs" / "demo" / "PRE_DEMO_CHECKLIST.md"
MANUFACTURER_RUNBOOK = REPO_ROOT / "docs" / "demo" / "MANUFACTURER_DEMO_RUNBOOK.md"


def _content() -> str:
    return CHECKLIST.read_text(encoding="utf-8")


def test_pre_demo_checklist_exists_and_is_linked_from_runbook() -> None:
    assert CHECKLIST.exists()
    assert "docs/demo/PRE_DEMO_CHECKLIST.md" in MANUFACTURER_RUNBOOK.read_text(
        encoding="utf-8"
    )


def test_pre_demo_checklist_covers_required_readiness_items() -> None:
    content = _content()

    required_items = [
        "git status --short",
        "make setup",
        "cd apps/web && npm install",
        "make demo",
        "demo api smoke passed",
        "make api",
        "EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl",
        "SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel",
        "npm run dev",
        "det_fill_weight_gradual_drift",
        "rec_fill_weight_gradual_drift",
        "Recommendation action was tested with a reviewer and reason.",
        "Decision feedback shows who reviewed it, the decision, and the reason.",
        "RCA/CAPA draft preview is visible",
        "docs/demo/MANUFACTURER_DEMO_RUNBOOK.md",
        "The demo script has been reviewed.",
    ]

    for item in required_items:
        assert item in content


def test_pre_demo_checklist_covers_demo_scope_and_human_review_caveats() -> None:
    content = _content()

    required_caveats = [
        "simulator-backed demo data",
        "advisory, human-reviewed decision support",
        "does not connect to real plant systems",
        "change equipment parameters",
        "release product",
        "create CAPAs",
        "write to QMS/MES",
        "site approval workflows",
        "not a production readiness checklist",
        "not a security review checklist",
    ]

    for caveat in required_caveats:
        assert caveat in content
