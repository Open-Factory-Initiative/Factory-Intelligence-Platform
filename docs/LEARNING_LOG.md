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

## 2026-05-09 - Post-implementation skeleton audit

### What changed

Reviewed the initial repository foundation against the architecture, MVP scope,
testing, learning-mode, README, planning, and code-review docs. Applied small
reliability fixes only: formatted the Python code, made the API not-found
response match the documented `{"error": ...}` envelope, added a regression test
for that contract, and split the FastAPI startup commands into `make api` and
`make api-reload`.

### Why it matters

The first skeleton is the base that later milestones build on. Keeping setup,
tests, and API contracts reliable now prevents contributors from learning the
wrong workflow or depending on accidental response shapes.

### How it works

The current platform skeleton still follows the simulator-backed path. The
simulator writes normalized event JSONL, ingestion validates those events through
`packages/factory-events` and stores accepted records, Process Sentinel reads the
stored events to create detections, evidence, and recommendations, and FastAPI
serves that state. Human review endpoints update recommendation state and append
approval/audit records; they do not perform industrial writeback.

### How to run it

```bash
make setup
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
make api
```

Use `make api-reload` when local file watching is useful during development.

### How to test it

```bash
.venv/bin/python -m ruff format --check packages services
make lint
make typecheck
make test
make test-unit
make test-integration
make test-contract
make test-e2e
```

`make test-e2e` is still an intentional placeholder until the web workbench is
implemented.

### Key files

- `Makefile`
- `README.md`
- `docs/DEVELOPMENT.md`
- `services/api/factory_api/main.py`
- `services/api/tests/test_api.py`

### What to learn next

The next narrow implementation step should be the shared event contract
milestone: tighten schema fixtures and contract documentation before adding more
simulator or UI behavior.

## 2026-05-11 - Local contributor readiness pass

### What changed

Updated the README with a clearer local setup path and added
`DEVELOPMENT_STATUS.md` to show what works, what is incomplete, and which
commands new contributors should run.

### Why it matters

New contributors need an honest path through the current skeleton. The project
has runnable backend pieces, but the web workbench and e2e flow are not ready
yet, so the docs should make that boundary explicit.

### How it works

The default development flow remains JSONL-backed: simulator output is written
to `.local/`, ingestion validates it, Process Sentinel produces state files, and
FastAPI reads those files for local API responses. Docker Compose is available
for the PostgreSQL service, but it is not required for the default skeleton run.

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
make lint
make typecheck
make test
make test-e2e
make dev-db
docker compose -f infra/docker/docker-compose.yml config
docker compose -f infra/docker/docker-compose.yml ps
```

### Key files

- `README.md`
- `DEVELOPMENT_STATUS.md`
- `.env.example`
- `infra/docker/docker-compose.yml`

### What to learn next

Use the development status file as the handoff point for the next milestone:
shared event contract hardening before building more UI or storage behavior.

## 2026-05-11 - First MVP domain model

### What changed

Added the first API-facing domain model for sites, areas, equipment, process
signals, batches, quality results, deviations, alerts, and investigations. The
API now exposes read-only demo records for those objects, including an
investigation detail response that links process signals to a failed quality
result and deviation.

### Why it matters

Process Sentinel needs manufacturing context before it can explain quality
drift. This model gives future detection and UI work stable identifiers for the
site, equipment, batch, process signals, quality outcome, deviation, alert, and
investigation.

### How it works

`services/api/factory_api/domain.py` defines strict Pydantic models and
deterministic demo data. `services/api/factory_api/main.py` serves that data
through read-only endpoints. The investigation detail endpoint joins the demo
investigation to its deviation, alert, quality result, and process signals so
contributors can see the expected relationship shape without adding database
storage yet.

### How to run it

```bash
make api
```

Then open:

```text
http://127.0.0.1:8000/investigations/inv_fill_weight_drift_1001
```

### How to test it

```bash
make test
make lint
make typecheck
```

### Key files

- `services/api/factory_api/domain.py`
- `services/api/factory_api/main.py`
- `services/api/tests/test_domain.py`
- `docs/DOMAIN_MODEL.md`

### What to learn next

Connect Process Sentinel detections to these domain identifiers so drift
evidence can be shown beside the related batch, quality result, deviation, and
investigation context.

## 2026-05-12 - Base FactoryEvent schema

### What changed

Added `FactoryEvent` as the named base event envelope in the shared
`factory-events` package while keeping `EventEnvelope` available for existing
service code. The event context now supports an optional `batch_id`, and a base
event fixture demonstrates event identity, event type, UTC timestamp, source,
line and asset context, optional batch/work order references, payload, and
metadata.

### Why it matters

Simulator, ingestion, Process Sentinel, evidence, and API workflows need one
shared event contract. A named base event model makes that contract explicit and
keeps validation behavior centralized.

### How it works

`FactoryEvent` validates the common envelope, dispatches payload validation by
`event_type`, rejects unsupported event types, requires UTC timestamps, and
requires simulator events to be marked as simulated. Payload-specific models
still validate process measurements, quality measurements, detections,
recommendations, approvals, and audit events.

### How to run it

No developer workflow changed. The same simulator and ingestion commands use the
shared event contract.

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

### How to test it

```bash
make test-contract
make lint
make typecheck
make test
```

### Key files

- `packages/factory-events/factory_events/models.py`
- `packages/factory-events/tests/test_event_contracts.py`
- `packages/test-fixtures/valid-events/base_factory_event.json`
- `docs/DATA_CONTRACTS.md`

### What to learn next

Define the next event-specific contracts from epic #8, starting with process
signal and quality event fixtures that build on this base envelope.

## 2026-05-12 - Pull request template expectations

### What changed

Updated the pull request template with a linked issue section, an explicit
`Closes #issue-number` reminder, and reviewer notes. Updated the contributor
checklist to match those PR expectations.

### Why it matters

Small, reviewable pull requests need clear issue linkage, test evidence,
documentation impact, and reviewer guidance before they are merged. This keeps
open-source contribution review consistent.

### How it works

New pull requests now prompt contributors to identify the linked issue at the
top of the PR body and to call out anything reviewers should focus on. The
contributor guide mirrors that expectation in the PR checklist.

### How to run it

No runtime command is needed. GitHub applies `.github/pull_request_template.md`
when a contributor opens a pull request.

### How to test it

Open a draft pull request and confirm the template appears. For local validation
of this documentation-only change, run:

```bash
make lint
make typecheck
make test
```

### Key files

- `.github/pull_request_template.md`
- `CONTRIBUTING.md`

### What to learn next

Keep refining contributor workflow docs as the project adds more active checks
and review expectations.
