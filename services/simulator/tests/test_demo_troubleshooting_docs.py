from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TROUBLESHOOTING = REPO_ROOT / "docs" / "demo" / "TROUBLESHOOTING.md"
MANUFACTURER_RUNBOOK = REPO_ROOT / "docs" / "demo" / "MANUFACTURER_DEMO_RUNBOOK.md"
TECHNICAL_RUNBOOK = REPO_ROOT / "docs" / "DEMO_RUNBOOK.md"
README = REPO_ROOT / "README.md"
WEB_README = REPO_ROOT / "apps" / "web" / "README.md"


def _content() -> str:
    return TROUBLESHOOTING.read_text(encoding="utf-8")


def test_demo_troubleshooting_guide_exists_and_is_linked() -> None:
    assert TROUBLESHOOTING.exists()

    expected_links = [
        (README, "docs/demo/TROUBLESHOOTING.md"),
        (WEB_README, "../../docs/demo/TROUBLESHOOTING.md"),
        (MANUFACTURER_RUNBOOK, "docs/demo/TROUBLESHOOTING.md"),
        (TECHNICAL_RUNBOOK, "docs/demo/TROUBLESHOOTING.md"),
    ]

    for path, link in expected_links:
        assert link in path.read_text(encoding="utf-8")


def test_demo_troubleshooting_guide_covers_required_failure_modes() -> None:
    content = _content()

    required_sections = [
        "Missing Dependencies",
        "No Detections",
        "API Not Running",
        "Frontend Cannot Reach API",
        "Stale Local State",
        "Empty RCA/CAPA Draft",
        "Recommendation Decision Not Updating",
        "Simulator-Backed Demo vs Production Concerns",
    ]

    for section in required_sections:
        assert section in content


def test_demo_troubleshooting_guide_includes_reset_and_recovery_commands() -> None:
    content = _content()

    required_commands = [
        "make setup",
        "npm install",
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
        "NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 npm run dev",
        "curl -s -o /dev/null -w \"%{http_code}\" http://127.0.0.1:8000/docs",
        "curl -s -X POST",
    ]

    for command in required_commands:
        assert command in content


def test_demo_troubleshooting_guide_labels_demo_boundaries() -> None:
    content = _content()

    required_terms = [
        "simulator-backed demo issues",
        "production incidents",
        "real plant connectors",
        "cloud deployment",
        "validated audit",
        "QMS/MES integrations",
        "site-specific compliance validation",
        "advisory",
        "human-reviewed",
    ]

    for term in required_terms:
        assert term in content
