# Process Sentinel

Explainable drift detection for the simulator-backed MVP.

Process Sentinel reads accepted unified factory events and creates local,
queryable demo state:

- `detections.json`
- `evidence.json`
- `recommendations.json`

The API exposes those outputs through:

- `/sentinel/detections`
- `/sentinel/detections/{detection_id}`
- `/sentinel/detections/{detection_id}/evidence`
- `/recommendations`

## Run

From the repository root:

```bash
make sentinel-run
```

Or run the service module directly:

```bash
python -m process_sentinel.cli --events-store .local/storage/events.jsonl --state-dir .local/storage/sentinel
```

## MVP Detection Assumptions

The MVP rules are deterministic and explainable. They are designed for local
simulator-backed development, not production release decisions.

- `normal` should not produce drift findings or high-severity false positives.
- `gradual_drift` should produce a medium-severity quality drift detection when
  recent `fill_weight` measurements are at least `2.0` grams above the baseline
  window.
- `sudden_excursion` should produce a high-severity process excursion detection
  when `filler_nozzle_pressure` exceeds the MVP control limit of `2.6`.
- Findings include evidence items with `source_event_ids` so contributors can
  trace each finding back to simulator events.
- Evidence items also carry severity, relevance score, and related asset,
  batch, and work order IDs derived from their source events.
- Process Sentinel recommendations remain advisory and require human review.
- Process Sentinel does not perform autonomous action, equipment writeback,
  product disposition, or QMS/MES updates.

## Current Limitations

- The rules use fixed MVP thresholds instead of learned limits.
- The local state store is JSON file based for development.
- The demo API makes findings queryable, but this is not a validated production
  audit trail.
