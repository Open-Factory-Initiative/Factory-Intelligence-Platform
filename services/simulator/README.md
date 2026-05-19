# Synthetic Factory Simulator

Generates deterministic simulator events for the Process Sentinel MVP.

The simulator is the first source in the local MVP path:

```text
Synthetic Factory Simulator
-> Ingestion Worker
-> Factory Event Store
-> Process Sentinel
```

Use it to create repeatable Factory Event JSONL files for local development,
tests, demos, and Process Sentinel workflows without connecting to real plant
systems.

## Available Scenarios

Current generated scenarios:

| Scenario | Purpose | Typical output path |
| --- | --- | --- |
| `normal` | Stable baseline operation with process and quality values inside limits. | `.local/events/normal.jsonl` |
| `gradual_drift` | Process signals gradually move away from baseline before a delayed quality concern. | `.local/events/gradual_drift.jsonl` |
| `sudden_excursion` | Short process excursion that creates an out-of-spec quality result. | `.local/events/sudden_excursion.jsonl` |

The scenario type format also reserves `noisy_sensor` for a future simulator
scenario, but event generation for that scenario is not implemented yet.

## Run With Make

The recommended local entry point is `make simulate`, which sets the required
Python import path for this monorepo:

```bash
make simulate \
  SCENARIO=gradual_drift \
  SEED=42 \
  COUNT=24 \
  OUTPUT=.local/events/gradual_drift.jsonl
```

Useful variables:

- `SCENARIO`: `normal`, `gradual_drift`, or `sudden_excursion`. Defaults to `gradual_drift`.
- `SEED`: deterministic random seed. Defaults to `42`.
- `COUNT`: number of simulated samples. Defaults to `24`.
- `DURATION_MINUTES`: duration-style sample count. When set, it overrides `COUNT`.
- `OUTPUT`: JSONL output path. Defaults to `.local/events/$(SCENARIO).jsonl`.

Examples:

```bash
make simulate SCENARIO=normal OUTPUT=.local/events/normal.jsonl
make simulate SCENARIO=gradual_drift SEED=42 COUNT=24 OUTPUT=.local/events/gradual_drift.jsonl
make simulate SCENARIO=sudden_excursion SEED=7 DURATION_MINUTES=15 OUTPUT=.local/events/sudden_excursion.jsonl
```

## Direct CLI Usage

Direct module execution is available when `PYTHONPATH` includes the shared event
contracts and simulator service:

```bash
PYTHONPATH=packages/factory-events:services/simulator \
  .venv/bin/python -m factory_simulator.cli \
  --scenario gradual_drift \
  --seed 42 \
  --count 24 \
  --output .local/events/gradual_drift.jsonl
```

CLI options:

- `--scenario`: one of `normal`, `gradual_drift`, or `sudden_excursion`.
- `--output`: JSONL output path. Parent directories are created automatically.
- `--seed`: deterministic random seed. Defaults to `42`.
- `--count`: number of simulated samples to generate. Defaults to `24`.
- `--duration-minutes`: duration-style sample count; overrides `--count`.

The CLI prints a summary with the event count, output path, scenario, seed, and
effective count. Invalid scenario names are rejected before any output file is
written.

## Seeded Output

Use `SEED` through `make simulate` or `--seed` through the CLI to reproduce
simulator output exactly for tests, demos, and issue debugging:

```bash
make simulate SCENARIO=gradual_drift SEED=42 OUTPUT=.local/events/gradual_drift.jsonl
```

The same scenario, seed, count, and start time produce identical event payloads.
Changing the seed changes the generated noise while preserving valid Factory
Event payloads and the scenario's expected behavior.

## Output Format

Simulator output is newline-delimited JSON (`.jsonl`). Each line is one
serialized Factory Event envelope that validates against
`packages/factory-events`.

For each simulated sample, the generator emits:

- Two process measurement events: fill weight and filler nozzle pressure.
- One quality measurement event every third sample.

For example, `COUNT=24` writes 56 events: 48 process measurements and 8 quality
measurements.

Output directories are created automatically. The default local convention is
`.local/events/<scenario>.jsonl`.

## Connect Simulator Output To Ingestion

After generating JSONL, pass the same path to ingestion:

```bash
make simulate SCENARIO=gradual_drift OUTPUT=.local/events/gradual_drift.jsonl
make ingest INPUT=.local/events/gradual_drift.jsonl
```

Ingestion validates each line against the shared Factory Event contracts,
appends accepted events to the local JSONL event store, and writes invalid
records to the dead-letter file. The accepted event store is then used by
Process Sentinel:

```bash
make sentinel-run
```

The default paths are:

- Generated simulator output: `.local/events/<scenario>.jsonl`
- Accepted event store: `.local/storage/events.jsonl`
- Dead-letter records: `.local/storage/dead_letter.jsonl`

## Scenario Definition Format

Scenario definitions live in `factory_simulator.scenarios`. They describe the
demo factory context before events are generated, so scenario behavior can stay
consistent across tests, docs, CLI usage, and future fixture work.

The format includes:

- Scenario metadata: name, type, description, default seed, default count, and duration.
- Line context: site, area, line, work order, and optional batch.
- Assets: stable asset IDs, names, and asset types.
- Process tags: signal ID, signal name, asset, unit, baseline value, normal range, target, drift or excursion parameters, and noise band.
- Quality markers: measurement name, asset, unit, specification limits, sample cadence, and failure severity.
- Output settings: current output format and default local path.

Example scenario definition shape:

```json
{
  "metadata": {
    "name": "gradual_drift",
    "scenario_type": "gradual_drift",
    "description": "Fill weight and nozzle pressure drift upward after a stable baseline.",
    "default_seed": 42,
    "default_count": 24,
    "duration_minutes": 24
  },
  "line_context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "work_order_id": "wo_1001"
  },
  "assets": [
    {
      "asset_id": "asset_filler_1",
      "asset_name": "Filler 1",
      "asset_type": "filler"
    },
    {
      "asset_id": "asset_checkweigher_1",
      "asset_name": "Checkweigher 1",
      "asset_type": "checkweigher"
    }
  ],
  "process_tags": [
    {
      "signal_id": "fill_weight",
      "signal_name": "Fill Weight",
      "asset_id": "asset_filler_1",
      "unit": "g",
      "baseline_value": 500.0,
      "normal_min": 495.0,
      "normal_max": 505.0,
      "target_value": 500.0,
      "drift_per_step": 0.33,
      "noise_band": 0.25
    }
  ],
  "quality_markers": [
    {
      "measurement_name": "Final Fill Weight",
      "asset_id": "asset_checkweigher_1",
      "unit": "g",
      "spec_min": 495.0,
      "spec_max": 505.0,
      "every_n_samples": 3,
      "severity_on_fail": "high"
    }
  ],
  "output": {
    "format": "jsonl",
    "default_path": ".local/events/gradual_drift.jsonl"
  }
}
```
