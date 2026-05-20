# Manufacturer Demo Runbook

## Purpose

This runbook prepares and guides an 8-10 minute manufacturer demo of the Factory
Intelligence Platform MVP. The demo is a simulator-backed Process Sentinel
workflow:

```text
Synthetic Factory Simulator
-> Ingestion Worker
-> Factory Event Store
-> Process Sentinel Drift Detection
-> Evidence Timeline
-> Governed Recommendation Queue
-> Operations Workbench
-> RCA/CAPA Draft Preview
```

All data in this runbook is simulator-backed demo data. It does not represent a
real plant, customer, batch record, or production system.

Recommendations shown in the demo are advisory and human-reviewed. The demo does
not perform autonomous control, QMS writeback, MES writeback, equipment
writeback, product disposition, or compliance validation.

## Prerequisites

- Git, Make, Python 3.12 or newer, and Node.js installed locally.
- Repository cloned and opened at the repository root.
- Python development environment installed with `make setup`.
- Web dependencies installed with `cd apps/web && npm install`.
- Local ports `8000` and `3000` available.
- No real plant systems, customer data, or production credentials connected.

## Pre-Call Checklist

Run the detailed pre-demo checklist 15-30 minutes before the call:

```text
docs/demo/PRE_DEMO_CHECKLIST.md
```

At minimum, confirm:

1. Pull the latest demo branch or main branch you plan to show.
2. Confirm the worktree has no unrelated local changes.
3. Run the one-command demo setup from the repository root.
4. Start the API.
5. Start the Operations Workbench.
6. Open the expected URLs in browser tabs.
7. Confirm the detection, evidence, recommendation, decision controls, and
   RCA/CAPA draft preview load.
8. Keep terminal tabs ready with `docs/DEMO_RUNBOOK.md` for technical fallback
   details and `docs/demo/TROUBLESHOOTING.md` for demo failure recovery.

## Exact Demo Commands

Run the full deterministic preparation command from the repository root:

```bash
make demo
```

`make demo` runs:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make demo-api-smoke
```

Expected output snippets:

```text
wrote 70 events to .local/events/fill_weight_drift_demo.jsonl (scenario=fill_weight_drift_demo, seed=120, count=30)
ingestion summary
accepted_events: 70
rejected_events: 0
dead_letter_count: 0
sentinel complete: detections=1 evidence=2 recommendations=1
demo api smoke passed
```

Expected demo IDs:

```text
Detection: det_fill_weight_gradual_drift
Recommendation: rec_fill_weight_gradual_drift
```

Start the API in a second terminal:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Start the Workbench in a third terminal:

```bash
cd apps/web
npm run dev
```

## Manual Step Commands

Use these only when you need to explain or troubleshoot the pipeline one step at
a time:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make demo-api-smoke
```

Expected files:

- `.local/events/fill_weight_drift_demo.jsonl`
- `.local/storage/fill_weight_drift_demo_events.jsonl`
- `.local/storage/fill_weight_drift_demo_dead_letter.jsonl`
- `.local/storage/fill_weight_drift_demo_sentinel/`

The accepted event store should contain 70 rows. The dead-letter file should
exist and contain 0 rows.

## Expected URLs

API:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/sentinel/detections
http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift
http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift/evidence
http://127.0.0.1:8000/recommendations
http://127.0.0.1:8000/recommendations/rec_fill_weight_gradual_drift
http://127.0.0.1:8000/reports/rca-capa-drafts/det_fill_weight_gradual_drift
```

Workbench:

```text
http://127.0.0.1:3000
http://127.0.0.1:3000/detections
http://127.0.0.1:3000/detections/det_fill_weight_gradual_drift
http://127.0.0.1:3000/recommendations?detection_id=det_fill_weight_gradual_drift
http://127.0.0.1:3000/rca-capa-draft?detection_id=det_fill_weight_gradual_drift
```

## Expected Demo Path

Open the Workbench overview first:

```text
http://127.0.0.1:3000
```

Expected story:

- The site is Greenville Demo Site.
- The line is Line 2 in Packaging Area.
- The work order is `WO-DEMO-1007`.
- The affected asset is `filler_f_201` / Filler F-201.
- Process Sentinel flags one medium-severity drift detection.
- The evidence timeline shows fill-weight drift and matching quality results.
- The governed recommendation is in `needs_review`.
- A reviewer can approve, reject, or defer the recommendation with a reason.
- The RCA/CAPA page shows draft investigation language for human review.

## 8-10 Minute Talk Track

### 0:00-1:00 - Set the boundary

"This is a simulator-backed local demo of the Factory Intelligence Platform MVP.
It is not connected to a real plant. The goal is to show the decision-support
workflow: detect a process drift, explain it with evidence, route a governed
recommendation, and draft investigation language for a human to review."

### 1:00-2:00 - Explain the generated scenario

"The simulator generated a deterministic packaging-line scenario for Greenville
Demo Site. In this run, the fill-weight signal gradually trends upward during
work order `WO-DEMO-1007`, and quality checks begin moving in the same
direction."

Show:

```text
make demo
```

Call out the expected output:

```text
accepted_events: 70
sentinel complete: detections=1 evidence=2 recommendations=1
```

### 2:00-3:30 - Show the overview and detection

Open:

```text
http://127.0.0.1:3000
http://127.0.0.1:3000/detections/det_fill_weight_gradual_drift
```

"Process Sentinel is not just showing an alert. It is tying the signal to the
site, area, line, work order, batch, and affected asset so the reviewer knows
where to investigate."

### 3:30-5:00 - Explain the evidence timeline

"The evidence timeline is what makes this reviewable. The first item compares
baseline and recent fill-weight averages. The second item shows that quality
checks are moving in the same direction. These are cited from the simulator
events generated for the demo."

Emphasize that the evidence is traceable demo data, not a production batch
record.

### 5:00-6:30 - Show the governed recommendation

Open:

```text
http://127.0.0.1:3000/recommendations?detection_id=det_fill_weight_gradual_drift
```

"The platform creates an advisory recommendation, but it does not act on the
factory. A human reviewer must approve, reject, or defer it and provide a
reason."

Use a demo reviewer such as `quality_engineer_demo` and a reason such as:

```text
Evidence supports checking filler calibration before release review.
```

### 6:30-7:30 - Show decision feedback

"After the human review, the Workbench shows the decision feedback so the user
can see who reviewed it, what decision was made, and why. In the MVP this is a
local demo audit trail, not an electronic signature or production quality
record."

### 7:30-8:30 - Show the RCA/CAPA draft preview

Open:

```text
http://127.0.0.1:3000/rca-capa-draft?detection_id=det_fill_weight_gradual_drift
```

"This page drafts investigation language from the detection, evidence, and
recommendation. It is meant to reduce blank-page work for the quality or
operations team. It still requires human review and does not create or close a
CAPA."

### 8:30-10:00 - Ask for manufacturer feedback

"The next useful discussion is not whether this exact simulated line is your
line. It is whether the workflow matches how your team investigates drift, what
evidence would make the recommendation credible, and what approvals would be
needed before any real site pilot."

## What Not To Claim

Do not claim:

- The platform is production ready.
- The platform is validated, certified, regulatory approved, or GxP ready.
- The demo connects to real plant systems.
- The demo uses real customer, batch, or equipment data.
- Recommendations are automatically executed.
- The platform changes machine parameters, releases product, closes deviations,
  creates CAPAs, or writes to QMS/MES systems.
- The demo replaces quality engineers, operators, maintenance teams, or site
  approval workflows.
- The local audit trail is an electronic signature or a validated production
  audit record.

Use these phrases instead:

- "simulator-backed demo data"
- "human-reviewed decision support"
- "governed recommendations"
- "advisory recommendation"
- "validation-aware workflow direction"
- "future site validation work would be required before production use"

## Troubleshooting

For the full demo troubleshooting guide, including no detections, API down,
frontend API connection issues, stale local state, missing dependencies, empty
RCA/CAPA drafts, and recommendation decision feedback, see
`docs/demo/TROUBLESHOOTING.md`.

### No detection appears

Run a clean deterministic setup:

```bash
make demo
```

Confirm the output includes:

```text
accepted_events: 70
dead_letter_count: 0
sentinel complete: detections=1 evidence=2 recommendations=1
```

If not, verify that the commands are using the demo event store:

```text
.local/storage/fill_weight_drift_demo_events.jsonl
```

and the demo Sentinel state directory:

```text
.local/storage/fill_weight_drift_demo_sentinel
```

### API page does not open

Confirm the API is running with the demo state:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

Then open:

```text
http://127.0.0.1:8000/docs
```

If port `8000` is already in use, stop the other process before the demo so the
expected URLs stay consistent.

### Workbench shows an API connection message

Confirm the API is running on:

```text
http://127.0.0.1:8000
```

Restart the Workbench after setting a custom API URL only if you intentionally
run the API on another port:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

For the manufacturer demo, prefer the default `8000` API port.

### Recommendation decision fails

Confirm both services are running:

```text
API: http://127.0.0.1:8000
Workbench: http://127.0.0.1:3000
```

Use a non-empty reviewer and reason. The demo API accepts local browser origins
for the Workbench by default.

### RCA/CAPA page is empty

Re-run:

```bash
make demo
```

Then open:

```text
http://127.0.0.1:3000/rca-capa-draft?detection_id=det_fill_weight_gradual_drift
```

The draft depends on the demo detection, evidence, and recommendation state
created by Process Sentinel.

## Post-Demo Discussion Prompts

Use these after the scripted demo:

- Which process or quality signals would be most valuable for a first pilot?
- Which evidence would your team need before trusting a recommendation?
- Who should review, approve, reject, or defer recommendations?
- What would the investigation handoff look like in your current deviation,
  RCA, or CAPA workflow?
- Which systems would be read-only sources in a first site pilot?
- What data must stay on site, and what data must never leave the site?
- What audit trail, validation package, or change-control evidence would your
  quality team expect before production use?
- What would make the workflow useful even before any writeback integration?
- Which parts of the demo felt credible, and which felt unlike your operation?

## Related Technical Runbook

For deeper command details, API payload examples, and generated file paths, see
`docs/DEMO_RUNBOOK.md`.
