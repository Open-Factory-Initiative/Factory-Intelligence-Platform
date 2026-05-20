# Demo Troubleshooting Guide

## Purpose

Use this guide when the simulator-backed manufacturer demo does not show the
expected Process Sentinel workflow. It covers local demo preparation, API and
Workbench startup, stale generated state, empty RCA/CAPA drafts, and governed
recommendation review feedback.

This guide is only for simulator-backed demo issues. It does not cover
production incidents, real plant connectors, cloud deployment, validated audit
records, QMS/MES integrations, or site-specific compliance validation.

## Known-Good Demo Reset

When in doubt, return to the deterministic demo state from the repository root:

```bash
make demo
```

That command runs:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make demo-api-smoke
```

Expected output:

```text
wrote 70 events to .local/events/fill_weight_drift_demo.jsonl (scenario=fill_weight_drift_demo, seed=120, count=30)
accepted_events: 70
rejected_events: 0
dead_letter_count: 0
sentinel complete: detections=1 evidence=2 recommendations=1
demo api smoke passed
```

Then start the API and Workbench:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

```bash
cd apps/web
npm run dev
```

## Quick Diagnosis

Check the demo path in this order:

1. `make demo` completes with 70 accepted events and one detection.
2. `http://127.0.0.1:8000/docs` opens.
3. `http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift`
   returns the expected detection.
4. `http://127.0.0.1:3000` opens the Operations Workbench.
5. The recommendation page can approve, reject, or defer
   `rec_fill_weight_gradual_drift` with a reviewer and reason.
6. The RCA/CAPA draft page opens for `det_fill_weight_gradual_drift`.

## Missing Dependencies

### Symptoms

- `.venv/bin/python: no such file or directory`
- `No module named factory_simulator`, `factory_ingestion`,
  `process_sentinel`, or `factory_api`
- `npm: command not found`
- `next: command not found`
- `Cannot find module` when starting the Workbench

### Recovery

From the repository root:

```bash
make setup
```

From the Workbench directory:

```bash
cd apps/web
npm install
```

Then retry:

```bash
make demo
```

## No Detections

### Symptoms

- `make demo-sentinel-run` prints `detections=0`.
- `/sentinel/detections` returns an empty list.
- The Workbench detection list has no Process Sentinel case.
- The recommendation queue is empty because no detection was created.

### Common causes

- The demo data was not generated before ingestion.
- The ingested file is from the `normal` scenario instead of
  `fill_weight_drift_demo`.
- `EVENTS_STORE` points to `.local/storage/events.jsonl` instead of
  `.local/storage/fill_weight_drift_demo_events.jsonl`.
- `SENTINEL_STATE_DIR` points to an old or unrelated state directory.
- Local generated files under `.local/` were edited by hand.

### Reproduce intentionally

This creates a no-detection case by ingesting normal simulator data into the
demo event-store path:

```bash
make demo-reset
make simulate SCENARIO=normal SEED=120 COUNT=30 OUTPUT=.local/events/fill_weight_drift_demo.jsonl
make demo-ingest
make demo-sentinel-run
```

Expected result:

```text
sentinel complete: detections=0 evidence=0 recommendations=0
```

### Recovery

Regenerate the deterministic drift demo:

```bash
make demo
```

Confirm:

```text
sentinel complete: detections=1 evidence=2 recommendations=1
```

## API Not Running

### Symptoms

- `http://127.0.0.1:8000/docs` does not open.
- `curl http://127.0.0.1:8000/health` cannot connect.
- Workbench pages show an API connection message.
- Recommendation decisions fail because the browser cannot reach the backend.

### Reproduce intentionally

Stop the API terminal, then run:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/docs
```

Expected result when the API is down:

```text
000
```

### Recovery

Start the API from the repository root with the demo event store and Sentinel
state:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Then open:

```text
http://127.0.0.1:8000/docs
```

If port `8000` is already in use, stop the other local process before the demo
so the expected URLs stay consistent.

## Frontend Cannot Reach API

### Symptoms

- `http://127.0.0.1:3000` opens, but pages show an API connection message.
- The Workbench API base URL does not match the running FastAPI port.
- Recommendation decision buttons submit but return a connection error.

### Common causes

- API is not running.
- API is running on `8001`, but the Workbench is still configured for `8000`.
- Workbench was started before `NEXT_PUBLIC_API_BASE_URL` was changed.
- Browser-side calls are using a local origin not allowed by the API CORS
  configuration.

### Recovery

For the manufacturer demo, prefer the default API port:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Start the Workbench:

```bash
cd apps/web
npm run dev
```

Only use a custom API port when you are intentionally debugging a port conflict:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

Restart the Workbench after changing `NEXT_PUBLIC_API_BASE_URL`.

## Stale Local State

### Symptoms

- The Workbench shows zero pending recommendations after a previous approval,
  rejection, or deferral.
- `make demo-api-smoke` passes, but the browser is looking at older generated
  state.
- Detection timestamps or recommendation status differ from the expected demo
  story.
- Local files under `.local/` were edited during manual testing.

### Reproduce intentionally

Run a recommendation decision against the local API:

```bash
curl -s -X POST \
  http://127.0.0.1:8000/recommendations/rec_fill_weight_gradual_drift/defer \
  -H 'content-type: application/json' \
  --data '{"reviewer":"quality_engineer_demo","reason":"Intentional stale-state check."}'
```

The recommendation status may no longer be `needs_review` in that running API
state.

### Recovery

Reset every generated demo file and rebuild the expected state:

```bash
make demo
```

If an API server was already running, stop and restart it after the reset:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Refresh the Workbench browser tab after the API restart.

## Empty RCA/CAPA Draft

### Symptoms

- `/rca-capa-draft?detection_id=det_fill_weight_gradual_drift` shows an empty
  state or API error.
- The API endpoint for the draft returns a not-found response.
- Detection detail loads, but the RCA/CAPA draft preview has no problem
  statement, evidence summary, or recommended containment.

### Common causes

- Process Sentinel has not run yet.
- The detection ID is wrong.
- The API is reading a Sentinel state directory that does not contain evidence
  or recommendation records for the demo detection.
- The demo data was replaced with a no-detection scenario.

### Recovery

Rebuild the demo state:

```bash
make demo
```

Confirm the API endpoint returns a draft:

```bash
curl -s http://127.0.0.1:8000/reports/rca-capa-drafts/det_fill_weight_gradual_drift
```

Expected fields include:

- `problem_statement`
- `evidence_summary`
- `recommended_containment`
- `capa_placeholder`

The draft is advisory decision support only. It does not create, close, or
submit a CAPA.

## Recommendation Decision Not Updating

### Symptoms

- Approve, reject, or defer appears to do nothing.
- The Workbench does not show reviewer, decision, reason, or timestamp feedback.
- The recommendation remains in the previous state after the reviewer submits a
  decision.

### Common causes

- API is not running.
- Workbench is pointed at the wrong API base URL.
- Reviewer or reason is empty.
- The recommendation was already reviewed in stale local state.
- The browser is showing an older rendered page after local state changed.

### Recovery

Confirm the API can record a decision:

```bash
curl -s -X POST \
  http://127.0.0.1:8000/recommendations/rec_fill_weight_gradual_drift/defer \
  -H 'content-type: application/json' \
  --data '{"reviewer":"quality_engineer_demo","reason":"Demo troubleshooting check."}'
```

Expected response fields:

- `recommendation_id`
- `reviewer`
- `decision`
- `reason`
- `created_at`

If the API decision works but the Workbench does not update, restart the
Workbench and refresh the browser. If the recommendation was already reviewed,
run:

```bash
make demo
```

Then restart the API and Workbench.

## Simulator-Backed Demo vs Production Concerns

Keep these categories separate during troubleshooting:

| Demo issue | Production concern |
| --- | --- |
| Missing local `.venv` or `node_modules` | Production dependency packaging |
| Port `8000` or `3000` conflict | Production ingress or service discovery |
| Stale `.local/` generated JSONL state | Durable database migration or backup |
| No detection because the wrong simulator scenario was used | Real process-model validation |
| Browser cannot reach local API | Site network, VPN, firewall, or identity controls |
| Local recommendation decision does not refresh | Validated audit trail or electronic signature |
| Empty local RCA/CAPA draft | QMS integration or production CAPA workflow |

Do not present any local recovery step as a production incident response. The
manufacturer demo remains simulator-backed, advisory, and human-reviewed.
