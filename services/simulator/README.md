# Synthetic Factory Simulator

Generates deterministic simulator events for the Process Sentinel MVP.

Example:

```bash
make simulate SCENARIO=gradual_drift OUTPUT=.local/events/gradual_drift.jsonl
```

## CLI Usage

Generate simulator JSONL without writing Python code:

```bash
make simulate \
  SCENARIO=gradual_drift \
  SEED=42 \
  DURATION_MINUTES=24 \
  OUTPUT=.local/events/gradual_drift.jsonl
```

Supported options:

- `--scenario`: one of `normal`, `gradual_drift`, or `sudden_excursion`.
- `--output`: JSONL output path. Parent directories are created automatically.
- `--seed`: deterministic random seed. Defaults to `42`.
- `--count`: number of simulated samples to generate. Defaults to `24`.
- `--duration-minutes`: duration-style sample count; overrides `--count`.

The CLI prints a summary with the event count, output path, scenario, seed, and
effective count. Invalid scenario names are rejected before any output file is
written.

For direct module execution outside `make`, set `PYTHONPATH` to include
`packages/factory-events` and `services/simulator`.

Generate the normal operation baseline:

```bash
make simulate SCENARIO=normal SEED=42 COUNT=24 OUTPUT=.local/events/normal.jsonl
```

The normal scenario emits deterministic process measurements and inline quality
checks within the configured operating and specification ranges. Use it as the
clean baseline dataset for ingestion, validation, and Process Sentinel tests
that should not produce quality drift.

Generate the gradual drift scenario:

```bash
make simulate SCENARIO=gradual_drift SEED=42 COUNT=24 OUTPUT=.local/events/gradual_drift.jsonl
```

The gradual drift scenario starts with a stable baseline period, then slowly
increases fill weight and nozzle pressure. Inline quality checks continue after
the process drift begins, with the first quality concern delayed until the drift
has moved far enough to exceed specification. Use this scenario for Process
Sentinel tests that need early drift evidence before a quality failure.

## Seeded Output

Use `SEED` through `make simulate` or `--seed` through the CLI to reproduce
simulator output exactly for tests, demos, and issue debugging:

```bash
make simulate SCENARIO=gradual_drift SEED=42 OUTPUT=.local/events/gradual_drift.jsonl
```

The same scenario, seed, count, and start time produce identical event payloads.
Changing the seed changes the generated noise while preserving valid Factory
Event payloads and the scenario's expected behavior.

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

Current generated scenarios are:

- `normal`
- `gradual_drift`
- `sudden_excursion`

The scenario type format also reserves `noisy_sensor` for a future simulator
scenario, but event generation for that scenario is not implemented yet.

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
