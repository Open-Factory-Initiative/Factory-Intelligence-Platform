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

## 2026-05-12 - Baseline CI workflow hardening

### What changed

Updated the GitHub Actions CI workflow to use stable checkout, Python, and Node
actions, install backend dependencies with `make setup`, and run `make lint`,
`make typecheck`, and `make test` as explicit named steps. Updated the
contributor guide with the same local validation commands.

### Why it matters

The project foundation needs CI that mirrors contributor workflows. Clear step
names make failures easier to understand, and reusing Makefile commands keeps
local and pull-request validation aligned.

### How it works

CI runs on pull requests and pushes to `main`. The backend job sets up Python,
installs dependencies, then runs linting, type/syntax checks, and tests through
the Makefile. The frontend job remains conditional until a frontend package
exists.

### How to run it

CI runs automatically on GitHub. Locally, run:

```bash
make setup
make lint
make typecheck
make test
```

### How to test it

```bash
make lint
make typecheck
make test
```

### Key files

- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`
- `CONTRIBUTING.md`

### What to learn next

Keep refining contributor workflow docs as the project adds more active checks
and review expectations. Once the web workbench exists, replace the placeholder e2e command with real
Playwright coverage and add that check to CI.

## 2026-05-12 - ADR template and process

### What changed

Added a reusable Architecture Decision Record template and a decisions README
that explains when contributors should create an ADR.

### Why it matters

The project is starting to make durable architecture choices around event
models, storage, connectors, governed actions, and validation. Recording those
decisions keeps future work aligned with the reasoning behind the platform.

### How it works

Contributors copy `docs/decisions/ADR_TEMPLATE.md` to the next numbered ADR
file, fill in the required decision sections, and submit it with the pull
request that introduces or depends on the decision. Superseded decisions stay in
place and point to the newer ADR.

### How to run it

No runtime command is needed for this documentation-only change.

### How to test it

Review the Markdown headings and links in GitHub or locally:

```bash
sed -n '1,220p' docs/decisions/ADR_TEMPLATE.md
sed -n '1,220p' docs/decisions/README.md
```

### Key files

- `docs/decisions/ADR_TEMPLATE.md`
- `docs/decisions/README.md`
- `docs/LEARNING_LOG.md`

### What to learn next

Use the ADR process for the next durable platform choice, such as storage
strategy, connector architecture, or governed action lifecycle details.

## 2026-05-12 - Contributor onboarding guide

### What changed

Expanded the contributor guide with the project mission, current repository
shape, issue types, beginner-friendly work guidance, local setup commands,
branch naming, pull request expectations, testing commands, and support paths.
Added a README link that points new contributors to the guide.

### Why it matters

New contributors need one practical entry point before they can make safe,
focused changes. The guide keeps project onboarding aligned with the current
simulator-backed Process Sentinel skeleton and the repository's review
expectations.

### How it works

`CONTRIBUTING.md` now walks contributors from project orientation through local
setup, validation, branch creation, and pull request submission. It also points
architecture decisions to the ADR process and routes questions through GitHub
Issues or Discussions.

### How to run it

No runtime command is needed for this documentation-only change.

### How to test it

Review the Markdown and verify the documented commands still match the repo:

```bash
make lint
make typecheck
make test
make test-e2e
make docs
```

### Key files

- `CONTRIBUTING.md`
- `README.md`
- `docs/LEARNING_LOG.md`

### What to learn next

Use early contributor feedback to refine issue labels, issue templates, and the
good-first-issue path as the project attracts external contributors.

## 2026-05-12 - Local setup verification

### What changed

Verified the local developer setup from a fresh local clone and tightened setup
docs where the walkthrough exposed small gaps. README now includes clone
commands, lists Git as a prerequisite, and explains that first-time dependency
installation needs PyPI access. CONTRIBUTING now carries the same setup note and
uses a generic issue branch example.

### Why it matters

The project foundation should let a new contributor clone the repo, install
dependencies, run tests, and exercise the simulator-backed MVP path without
guessing which steps are assumed.

### How it works

The verified path creates a repo-local `.venv`, installs `requirements-dev.txt`,
runs lint/typecheck/tests, generates simulator events, ingests them into local
JSONL storage, runs Process Sentinel, and starts the FastAPI API over that
local state.

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
make help
make lint
make typecheck
make test
make test-e2e
make docs
```

### Key files

- `README.md`
- `CONTRIBUTING.md`
- `docs/LEARNING_LOG.md`

### What to learn next

Add a real docs checker and e2e workflow when the web workbench exists so the
currently documented placeholder commands can become active validation steps.

## 2026-05-14 - Batch and work order event schemas

### What changed

Added shared `BatchEvent` and `WorkOrderEvent` contracts to the factory-events
package, including typed payloads, supported production event types, valid
example fixtures, invalid example fixtures, and contract tests.

### Why it was built that way

Batch and work order context belongs in the shared event layer because multiple
services need the same production identifiers before drift detections can be
connected to affected lots, products, materials, and orders. The new models
reuse the existing `FactoryEvent` envelope instead of creating a separate event
shape.

### How data flows through it

A source adapter emits a `FactoryEvent` with a production event type such as
`production.batch.started` or `production.work_order.completed`. The shared
validator selects the matching payload model, validates required identifiers and
status values, and rejects mismatches between envelope context IDs and payload
IDs.

### How to run it

No service command is required for the schema change. Event payloads can be
validated by importing `validate_event` from `factory_events`.

### How to test it

```bash
make test-contract
make lint
make typecheck
make test
```

### What to learn next

Connect simulator output to these production context events so drift detections
can reference the affected batch, lot, product, and work order in the evidence
timeline.

## 2026-05-14 - Process signal event schema

### What changed

Added `ProcessSignalEvent` as the typed factory-events envelope for
`process.measurement.recorded` events. The process measurement payload now
requires a process tag name and supports optional normal operating limits plus a
target value. Valid temperature and pressure examples and invalid examples were
added to the shared fixtures.

### Why it was built that way

Process Sentinel needs one consistent contract for simulator tags and future
connector tags. Reusing the existing `FactoryEvent` envelope keeps event
identity, source metadata, UTC timestamps, line context, and validation behavior
consistent with the rest of the shared event model.

### How data flows through it

A source adapter emits a `process.measurement.recorded` event. The shared
validator selects the process measurement payload, checks the required tag name,
numeric value, engineering unit, quality value, and optional normal range, then
returns a validated `FactoryEvent` or `ProcessSignalEvent`.

### How to run it

No service command is required for the schema change. Process signal payloads
can be validated by importing `validate_event` or `ProcessSignalEvent` from
`factory_events`.

### How to test it

```bash
make test-contract
make lint
make typecheck
make test
```

### What to learn next

Use the process signal limits in simulator scenarios and Process Sentinel
evidence so detections can explain which tags moved outside their expected
operating range.
