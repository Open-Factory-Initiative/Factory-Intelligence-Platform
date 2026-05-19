# Demo Runbook

## Demo Data Pack

The manufacturer demo uses the deterministic `fill_weight_drift_demo` simulator
scenario. The data is simulator-backed and safe for local development; it does
not represent a real plant, customer, or production system.

### Seeded Scenario

```bash
make simulate \
  SCENARIO=fill_weight_drift_demo \
  SEED=120 \
  COUNT=30 \
  OUTPUT=.local/events/fill_weight_drift_demo.jsonl
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
make ingest \
  INPUT=.local/events/fill_weight_drift_demo.jsonl \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl

make sentinel-run \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Expected Process Sentinel output includes:

```text
sentinel complete: detections=1 evidence=2 recommendations=1
```
