# Pre-Demo Checklist

## Purpose

Use this checklist 15-30 minutes before a manufacturer call to confirm the
simulator-backed Process Sentinel demo is ready to show.

This checklist is for the local manufacturer demo only. It is not a production readiness checklist. It is not a security review checklist. It is not a validation package or real plant integration checklist.

It is not:

- A production readiness checklist.
- A security review checklist.
- A validation package.
- A real plant integration checklist.

## Demo Boundaries

- [ ] Say up front that the demo uses simulator-backed demo data.
- [ ] Say recommendations are advisory, human-reviewed decision support.
- [ ] Say the demo does not connect to real plant systems.
- [ ] Say the demo does not change equipment parameters, release product,
      create CAPAs, write to QMS/MES, or replace site approval workflows.

## Environment

- [ ] Repository is on the branch you plan to show.
- [ ] `git status --short` shows no unrelated local changes.
- [ ] Python dependencies are installed with `make setup`.
- [ ] Web dependencies are installed with `cd apps/web && npm install`.
- [ ] Ports `8000` and `3000` are available.

## Demo State

- [ ] Run the deterministic demo setup from the repository root:

```bash
make demo
```

- [ ] Confirm the smoke test passed:

```text
demo api smoke passed
```

- [ ] Confirm the expected generated state is visible in the output:

```text
accepted_events: 70
dead_letter_count: 0
sentinel complete: detections=1 evidence=2 recommendations=1
```

- [ ] Confirm the expected detection and recommendation IDs:

```text
Detection: det_fill_weight_gradual_drift
Recommendation: rec_fill_weight_gradual_drift
```

## Services

- [ ] Start the API from the repository root:

```bash
make api \
  EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl \
  SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

- [ ] Open the API docs:

```text
http://127.0.0.1:8000/docs
```

- [ ] Start the Operations Workbench:

```bash
cd apps/web
npm run dev
```

- [ ] Open the Workbench:

```text
http://127.0.0.1:3000
```

## Demo Path

- [ ] Expected detection is visible:

```text
http://127.0.0.1:3000/detections/det_fill_weight_gradual_drift
```

- [ ] Evidence timeline is visible and tied to simulator-backed demo events.
- [ ] Governed recommendation is visible:

```text
http://127.0.0.1:3000/recommendations?detection_id=det_fill_weight_gradual_drift
```

- [ ] Recommendation action was tested with a reviewer and reason.
- [ ] Decision feedback shows who reviewed it, the decision, and the reason.
- [ ] RCA/CAPA draft preview is visible:

```text
http://127.0.0.1:3000/rca-capa-draft?detection_id=det_fill_weight_gradual_drift
```

- [ ] Demo script and talk track were reviewed in
      `docs/demo/MANUFACTURER_DEMO_RUNBOOK.md`.
- [ ] `docs/demo/TROUBLESHOOTING.md` is open or easy to reach for recovery.

## Ready-To-Show Summary

The call is ready when:

- [ ] The repo is clean.
- [ ] Dependencies are installed.
- [ ] Demo data is generated.
- [ ] The API is running.
- [ ] The frontend is running.
- [ ] The smoke test passed.
- [ ] The expected detection is visible.
- [ ] A recommendation action was tested.
- [ ] The RCA/CAPA draft is visible.
- [ ] The demo script has been reviewed.
- [ ] Simulator-backed and human-review caveats are part of the opening script.
