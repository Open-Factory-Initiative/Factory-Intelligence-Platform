from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
README = REPO_ROOT / "services" / "process-sentinel" / "README.md"


def _content() -> str:
    return README.read_text(encoding="utf-8")


def test_process_sentinel_readme_documents_epic_11_assumptions() -> None:
    content = _content()

    required_terms = [
        "MVP Detection Assumptions",
        "normal",
        "gradual_drift",
        "sudden_excursion",
        "fill_weight",
        "filler_nozzle_pressure",
        "source_event_ids",
        "recommendations remain advisory",
        "human review",
        "does not perform autonomous action",
    ]

    for term in required_terms:
        assert term in content


def test_process_sentinel_readme_documents_queryable_outputs() -> None:
    content = _content()

    required_terms = [
        "detections.json",
        "evidence.json",
        "recommendations.json",
        "/sentinel/detections",
        "/sentinel/detections/{detection_id}/evidence",
        "/recommendations",
        "make sentinel-run",
    ]

    for term in required_terms:
        assert term in content
