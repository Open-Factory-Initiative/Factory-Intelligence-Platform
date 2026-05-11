from __future__ import annotations

import argparse
from pathlib import Path

from factory_ingestion.storage import JsonlEventStore

from process_sentinel.rules import run_sentinel
from process_sentinel.storage import SentinelStateStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Process Sentinel drift detection.")
    parser.add_argument("--events-store", type=Path, default=Path(".local/storage/events.jsonl"))
    parser.add_argument("--state-dir", type=Path, default=Path(".local/storage/sentinel"))
    args = parser.parse_args()

    events = JsonlEventStore(args.events_store).list_events()
    result = run_sentinel(events)
    SentinelStateStore(args.state_dir).save_run_result(result)

    print(
        "sentinel complete: "
        f"detections={len(result.detections)} "
        f"evidence={len(result.evidence_items)} "
        f"recommendations={len(result.recommendations)} "
        f"state_dir={args.state_dir}"
    )


if __name__ == "__main__":
    main()
