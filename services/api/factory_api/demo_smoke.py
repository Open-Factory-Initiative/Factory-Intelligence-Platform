from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fastapi.testclient import TestClient

from factory_api.main import create_app

EXPECTED_EVENT_COUNT = 70
EXPECTED_DETECTION_ID = "det_fill_weight_gradual_drift"
EXPECTED_RECOMMENDATION_ID = "rec_fill_weight_gradual_drift"


class DemoSmokeError(Exception):
    pass


@dataclass(frozen=True)
class DemoSmokeResult:
    event_count: int
    evidence_count: int
    recommendation_id: str
    decision: str
    rca_capa_draft_id: str


def run_demo_api_smoke(events_store_path: Path, sentinel_state_dir: Path) -> DemoSmokeResult:
    _require_demo_state(events_store_path, sentinel_state_dir)

    with tempfile.TemporaryDirectory(prefix="factory-demo-api-smoke-") as temp_dir:
        temp_path = Path(temp_dir)
        smoke_events_store = temp_path / events_store_path.name
        smoke_state_dir = temp_path / "sentinel"
        shutil.copy2(events_store_path, smoke_events_store)
        shutil.copytree(sentinel_state_dir, smoke_state_dir)

        client = TestClient(
            create_app(
                events_store_path=smoke_events_store,
                sentinel_state_dir=smoke_state_dir,
            )
        )

        events = _get_json(client, "/events")
        if len(events) != EXPECTED_EVENT_COUNT:
            msg = (
                f"Expected {EXPECTED_EVENT_COUNT} demo events from /events, "
                f"received {len(events)}."
            )
            raise DemoSmokeError(msg)

        detections = _get_json(client, "/sentinel/detections")
        detection = _find_item(detections, "detection_id", EXPECTED_DETECTION_ID)
        if detection["status"] != "recommendation_created":
            msg = (
                f"Expected detection {EXPECTED_DETECTION_ID} status "
                f"'recommendation_created', received {detection['status']!r}."
            )
            raise DemoSmokeError(msg)

        evidence = _get_json(
            client,
            f"/sentinel/detections/{EXPECTED_DETECTION_ID}/evidence",
        )
        if not evidence:
            msg = f"Expected evidence for detection {EXPECTED_DETECTION_ID}, received none."
            raise DemoSmokeError(msg)

        recommendations = _get_json(client, "/recommendations")
        recommendation = _find_item(
            recommendations,
            "recommendation_id",
            EXPECTED_RECOMMENDATION_ID,
        )
        if recommendation["requires_approval"] is not True:
            msg = f"Expected recommendation {EXPECTED_RECOMMENDATION_ID} to require approval."
            raise DemoSmokeError(msg)

        decision = _post_json(
            client,
            f"/recommendations/{EXPECTED_RECOMMENDATION_ID}/defer",
            {
                "reviewer": "demo_smoke_test",
                "reason": "Backend demo smoke test confirms decision endpoint works.",
            },
        )
        if decision["decision"] != "deferred":
            msg = f"Expected deferred decision response, received {decision['decision']!r}."
            raise DemoSmokeError(msg)
        if decision["recommendation_id"] != EXPECTED_RECOMMENDATION_ID:
            msg = "Decision response did not include the expected recommendation ID."
            raise DemoSmokeError(msg)
        if "timestamp" not in decision:
            msg = "Decision response did not include timestamp for UI confirmation."
            raise DemoSmokeError(msg)

        draft = _get_json(
            client,
            f"/reports/rca-capa-drafts/{EXPECTED_DETECTION_ID}",
        )
        required_draft_fields = {
            "title",
            "problem_statement",
            "evidence_summary",
            "recommended_containment",
            "capa_placeholder",
            "human_review_required",
        }
        missing_draft_fields = required_draft_fields.difference(draft)
        if missing_draft_fields:
            msg = f"RCA/CAPA draft missing fields: {sorted(missing_draft_fields)}."
            raise DemoSmokeError(msg)
        if draft["human_review_required"] is not True:
            msg = "RCA/CAPA draft must be marked human_review_required."
            raise DemoSmokeError(msg)

        return DemoSmokeResult(
            event_count=len(events),
            evidence_count=len(evidence),
            recommendation_id=recommendation["recommendation_id"],
            decision=decision["decision"],
            rca_capa_draft_id=draft["detection_id"],
        )


def _require_demo_state(events_store_path: Path, sentinel_state_dir: Path) -> None:
    if not events_store_path.is_file():
        msg = (
            f"Missing demo events store: {events_store_path}. "
            "Run make demo-data, make demo-ingest, and make demo-sentinel-run first."
        )
        raise DemoSmokeError(msg)
    if not sentinel_state_dir.is_dir():
        msg = (
            f"Missing demo Sentinel state directory: {sentinel_state_dir}. "
            "Run make demo-sentinel-run first."
        )
        raise DemoSmokeError(msg)

    required_state_files = (
        "detections.json",
        "evidence.json",
        "recommendations.json",
    )
    missing_state_files = [
        filename
        for filename in required_state_files
        if not (sentinel_state_dir / filename).is_file()
    ]
    if missing_state_files:
        msg = (
            f"Demo Sentinel state is missing files: {missing_state_files}. "
            "Run make demo-sentinel-run first."
        )
        raise DemoSmokeError(msg)


def _get_json(client: TestClient, path: str):
    response = client.get(path)
    if response.status_code != 200:
        msg = f"GET {path} failed with HTTP {response.status_code}: {response.text}"
        raise DemoSmokeError(msg)
    return response.json()


def _post_json(client: TestClient, path: str, payload: dict):
    response = client.post(path, json=payload)
    if response.status_code != 200:
        msg = f"POST {path} failed with HTTP {response.status_code}: {response.text}"
        raise DemoSmokeError(msg)
    return response.json()


def _find_item(items: list[dict], key: str, expected_value: str) -> dict:
    for item in items:
        if item.get(key) == expected_value:
            return item
    msg = f"Expected item with {key}={expected_value!r}, received {items!r}."
    raise DemoSmokeError(msg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the backend demo API smoke test.")
    parser.add_argument(
        "--events-store",
        type=Path,
        default=Path(".local/storage/fill_weight_drift_demo_events.jsonl"),
        help="Path to the ingested demo event store.",
    )
    parser.add_argument(
        "--sentinel-state-dir",
        type=Path,
        default=Path(".local/storage/fill_weight_drift_demo_sentinel"),
        help="Path to the demo Sentinel state directory.",
    )
    args = parser.parse_args(argv)

    try:
        result = run_demo_api_smoke(args.events_store, args.sentinel_state_dir)
    except DemoSmokeError as exc:
        print(f"demo api smoke failed: {exc}", file=sys.stderr)
        return 1

    print("demo api smoke passed")
    print(f"events: {result.event_count}")
    print(f"evidence_items: {result.evidence_count}")
    print(f"recommendation: {result.recommendation_id}")
    print(f"decision: {result.decision}")
    print(f"rca_capa_draft: {result.rca_capa_draft_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
