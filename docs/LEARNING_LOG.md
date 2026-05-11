# Learning Log

This file should be updated by Codex after each meaningful change.

## Template

```markdown
## YYYY-MM-DD - <task name>

### What changed

### Why it matters

### How it works

### How to run it

### How to test it

### Key files

### What to learn next
```

## 2026-05-09 - First Process Sentinel MVP skeleton

### What changed

Added the first executable backend skeleton: shared factory event contracts,
deterministic simulator scenarios, ingestion validation with dead-letter
handling, Process Sentinel drift rules, FastAPI query/review endpoints, local
developer commands, Docker PostgreSQL config, and backend tests.

### Why it matters

This creates a narrow vertical slice that contributors can run locally without
connecting to real industrial systems. It proves the platform shape before the
web workbench and real connectors are added.

### How it works

The simulator emits normalized event envelopes. Ingestion validates each event
against `packages/factory-events`, stores accepted events in `.local/`, and
writes invalid events to a dead-letter file. Process Sentinel reads the accepted
events, creates detections with evidence and recommendations, and the API serves
that state for review. Approval, rejection, and deferral update demo state and
write audit records.

### How to run it

```bash
make setup
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
make api
```

### How to test it

```bash
make test
make lint
make typecheck
```

### Key files

- `packages/factory-events/factory_events/models.py`
- `services/simulator/factory_simulator/generator.py`
- `services/ingestion/factory_ingestion/ingest.py`
- `services/process-sentinel/process_sentinel/rules.py`
- `services/api/factory_api/main.py`
- `Makefile`

### What to learn next

Build the first web workbench screen over the real API state, then add a
Playwright e2e test for the simulator-to-approval workflow.
