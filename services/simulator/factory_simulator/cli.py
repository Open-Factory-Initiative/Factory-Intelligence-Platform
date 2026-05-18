from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from factory_simulator.generator import SCENARIOS, generate_events


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic factory simulator events.")
    parser.add_argument("--scenario", choices=SCENARIOS, default="normal")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--count", type=int, default=24)
    parser.add_argument(
        "--duration-minutes",
        type=int,
        dest="duration_minutes",
        help="Generate one sample per simulated minute; overrides --count.",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    count = args.duration_minutes if args.duration_minutes is not None else args.count
    try:
        events = generate_events(args.scenario, seed=args.seed, count=count)
    except ValueError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as output:
        for event in events:
            output.write(json.dumps(event.model_dump(mode="json"), sort_keys=True))
            output.write("\n")

    print(
        f"wrote {len(events)} events to {args.output} "
        f"(scenario={args.scenario}, seed={args.seed}, count={count})"
    )


if __name__ == "__main__":
    main()
