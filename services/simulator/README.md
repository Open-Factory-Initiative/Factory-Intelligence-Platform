# Synthetic Factory Simulator

Generates deterministic simulator events for the Process Sentinel MVP.

Example:

```bash
python -m factory_simulator.cli --scenario gradual_drift --output .local/events/gradual_drift.jsonl
```

Generate the normal operation baseline:

```bash
python -m factory_simulator.cli --scenario normal --seed 42 --count 24 --output .local/events/normal.jsonl
```

The normal scenario emits deterministic process measurements and inline quality
checks within the configured operating and specification ranges. Use it as the
clean baseline dataset for ingestion, validation, and Process Sentinel tests
that should not produce quality drift.

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
