# Demo Runbook

## Demo Data Pack

The manufacturer demo uses the deterministic `fill_weight_drift_demo` simulator
scenario. The data is simulator-backed and safe for local development; it does
not represent a real plant, customer, or production system.

### One-Command Demo Setup

Use the demo-specific Make targets from the repository root when preparing for
a manufacturer call:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
```

`make demo-reset` clears only the generated local demo files:

- `.local/events/fill_weight_drift_demo.jsonl`
- `.local/storage/fill_weight_drift_demo_events.jsonl`
- `.local/storage/fill_weight_drift_demo_dead_letter.jsonl`
- `.local/storage/fill_weight_drift_demo_sentinel/`

Those paths live under `.local/`, which is ignored by Git. The reset target does
not drop a production database, remove source files, or clean real plant data.

The demo targets print the next command to run after each step. After
`make demo-sentinel-run`, start the API against the demo state with:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### Seeded Scenario

```bash
make demo-data
```

Expected simulator output:

```text
wrote 70 events to .local/events/fill_weight_drift_demo.jsonl (scenario=fill_weight_drift_demo, seed=120, count=30)
```

### Demo Names And IDs

| Concept | Demo value |
| --- | --- |
| Site | `greenville_demo_site` / Greenville Demo Site |
| Area | `packaging_area` / Packaging Area |
| Line | `line_2` / Line 2 |
| Product | `ofi_demo_beverage` / OFI Demo Beverage |
| Work order | `WO-DEMO-1007` |
| Batch | `BATCH-DEMO-1007` |
| Affected asset | `filler_f_201` / Filler F-201 |
| Quality check asset | `checkweigher_cw_201` / Checkweigher CW-201 |
| Process tags | `fill_weight`, `filler_nozzle_pressure` |
| Expected detection | `det_fill_weight_gradual_drift` |
| Expected recommendation | `rec_fill_weight_gradual_drift` |

### Expected Event Shape

The generated data includes process measurement events and quality measurement
events. Each event includes source metadata, simulator trace metadata, site,
area, line, work order, batch, asset context, and readable process or quality
payload fields for UI cards.

### Local Demo Path

```bash
make demo-ingest
make demo-sentinel-run
```

### Demo Ingestion Verification

Run ingestion after `make demo-data`:

```bash
make demo-ingest
```

Expected ingestion summary:

```text
ingestion summary
input_file: .local/events/fill_weight_drift_demo.jsonl
accepted_events: 70
rejected_events: 0
dead_letter_count: 0
accepted_output: .local/storage/fill_weight_drift_demo_events.jsonl
dead_letter_output: .local/storage/fill_weight_drift_demo_dead_letter.jsonl
```

Verify the local files:

```bash
test -f .local/storage/fill_weight_drift_demo_events.jsonl
test -f .local/storage/fill_weight_drift_demo_dead_letter.jsonl
wc -l .local/storage/fill_weight_drift_demo_events.jsonl
wc -l .local/storage/fill_weight_drift_demo_dead_letter.jsonl
```

The accepted event store should contain 70 rows. The dead-letter file should
exist and contain 0 rows for the deterministic demo data. If an invalid row is
added during manual testing, ingestion should keep processing valid rows and
write the invalid row to the dead-letter file.

Expected Process Sentinel output includes:

```text
sentinel complete: detections=1 evidence=2 recommendations=1
```

### Expected Demo Detection

The deterministic demo run should produce one Process Sentinel detection:

| Field | Expected value |
| --- | --- |
| Detection ID | `det_fill_weight_gradual_drift` |
| API list endpoint | `/sentinel/detections` |
| API detail endpoint | `/sentinel/detections/det_fill_weight_gradual_drift` |
| Summary | Advisory: fill weight is trending upward, which may move the affected work order toward the upper quality limit. |
| Severity | `medium` |
| Confidence | Greater than `0.7` |
| Related work order | `WO-DEMO-1007` |
| Related asset IDs | `filler_f_201` |

After `make demo-sentinel-run`, start the API with the demo state and query the
detection:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Then open or request:

```text
http://127.0.0.1:8000/sentinel/detections
http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift
```

### Expected Demo Evidence Timeline

The demo detection evidence endpoint should return a chronological timeline:

```text
http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift/evidence
```

Expected evidence items:

| Order | Evidence type | Title | What it shows |
| --- | --- | --- | --- |
| 1 | `process_signal` | Recent fill weight average is higher than baseline | Baseline and recent fill-weight averages, source process event IDs, and a score. |
| 2 | `quality_result` | Recent quality checks are near the upper spec limit | Recent quality checks moving in the same direction as the process signal, source quality event IDs, and a score. |

Each evidence item includes:

- `evidence_id`
- `detection_id`
- `evidence_type`
- `timestamp`
- `title`
- `description`
- `source_event_ids`
- `score`

The UI/API contract, empty state, and error state are documented in
`docs/EVIDENCE_TIMELINE_API_CONTRACT.md`.

### Troubleshooting Demo Ingestion

If no detections appear during demo prep, first confirm that the demo is using
the deterministic data path end to end:

| Item | Expected value |
| --- | --- |
| Demo event file | `.local/events/fill_weight_drift_demo.jsonl` |
| Demo accepted event store | `.local/storage/fill_weight_drift_demo_events.jsonl` |
| Demo dead-letter file | `.local/storage/fill_weight_drift_demo_dead_letter.jsonl` |
| Demo Sentinel state | `.local/storage/fill_weight_drift_demo_sentinel/` |
| Generated event count | `70` |
| Accepted event count | `70` |
| Rejected event count | `0` |
| Dead-letter row count | `0` |
| Expected Sentinel result | `detections=1 evidence=2 recommendations=1` |

Use a clean reset and retry when local state is stale, manually edited, or
pointing at an older scenario:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
```

Then verify the generated files:

```bash
wc -l .local/events/fill_weight_drift_demo.jsonl
wc -l .local/storage/fill_weight_drift_demo_events.jsonl
wc -l .local/storage/fill_weight_drift_demo_dead_letter.jsonl
```

Common ingestion failure cases:

- The input file is missing because `make demo-data` was not run first.
- `accepted_events` is `0` or lower than `70` because the command used the
  wrong input file, scenario, seed, or count.
- `rejected_events` or `dead_letter_count` is non-zero because at least one
  JSONL row is malformed or does not match the shared factory event contracts.
- Process Sentinel reads the wrong event store because `EVENTS_STORE` points to
  `.local/storage/events.jsonl` instead of the demo accepted event store.
- Old Sentinel state is being inspected after reruns instead of
  `.local/storage/fill_weight_drift_demo_sentinel/` from the latest run.
- The local files were hand-edited. Reset and regenerate instead of repairing
  generated `.local/` files by hand.

When rejected events appear, inspect the summary and the dead-letter file:

```bash
head -n 3 .local/storage/fill_weight_drift_demo_dead_letter.jsonl
```

The demo reset only clears generated local demo files under `.local/`. It does
not remove source files, clean production databases, or interact with real plant
systems.
