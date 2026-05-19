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

## 2026-05-19 - Simulator usage documentation

### What changed

Expanded the simulator documentation with available scenarios, recommended
`make simulate` usage, direct CLI usage, seed behavior, JSONL output format,
default paths, example commands, and the handoff from simulator output to
ingestion and Process Sentinel.

### Why it matters

Contributors need to generate realistic local data without reading simulator
code first. Clear docs make the simulator useful for onboarding, tests, demos,
issue reproduction, and the full Process Sentinel MVP workflow.

### How it works

The simulator writes Factory Event JSONL files under `.local/events/`. Ingestion
reads that JSONL path, validates each line through the shared contracts, writes
accepted events to `.local/storage/events.jsonl`, and leaves invalid records in
the dead-letter file.

### How to run it

```bash
make simulate SCENARIO=gradual_drift OUTPUT=.local/events/gradual_drift.jsonl
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
```

### How to test it

```bash
make docs
make simulate SCENARIO=normal OUTPUT=/private/tmp/fip-docs-normal.jsonl
make ingest INPUT=/private/tmp/fip-docs-normal.jsonl
make test
```

### Key files

- `services/simulator/README.md`
- `README.md`

### What to learn next

Use the documented simulator-to-ingestion workflow as the starting point for
future Process Sentinel walkthroughs and e2e tests.

## 2026-05-18 - Simulator scenario regression tests

### What changed

Added simulator regression tests that cover every current generated scenario for
expected event counts, process and quality timing, schema validity, stable event
identity, deterministic metadata, and sudden excursion signal behavior.

### Why it matters

The simulator is the source of local MVP data. Strong scenario tests protect the
ingestion and Process Sentinel workflow from accidental changes to event shape,
timing, determinism, or scenario-specific signal patterns.

### How it works

The tests generate each scenario with fixed seeds and counts, validate every
event through the shared Factory Event schema, check the expected two process
events plus periodic quality checks, and assert that sudden excursion pressure
spikes are bounded to the excursion window.

### How to run it

```bash
make test-unit
```

### How to test it

```bash
make test-unit
make lint
make typecheck
make test
```

### Key files

- `services/simulator/tests/test_simulator.py`

### What to learn next

Use these scenario guarantees when writing ingestion and Process Sentinel
regression tests that depend on specific simulator event timing.

## 2026-05-18 - Simulator CLI command

### What changed

Refined the simulator CLI so it supports scenario name, output path, seed,
event count, and duration-style sample count. Added CLI tests for normal output,
gradual drift output, invalid scenario errors, JSONL file creation, and schema
validation.

### Why it matters

Contributors need a simple command to generate local simulator data for tests,
demos, and debugging without writing Python code. Clear CLI behavior also makes
future onboarding and issue reproduction easier.

### How it works

The CLI parses arguments with `argparse`, calls the existing deterministic
simulator generator, creates the output directory, writes one Factory Event JSON
object per line, and prints a summary of the generated stream.

### How to run it

```bash
make simulate SCENARIO=gradual_drift SEED=42 OUTPUT=.local/events/gradual_drift.jsonl
make simulate SCENARIO=normal SEED=42 COUNT=24 OUTPUT=.local/events/normal.jsonl
```

### How to test it

```bash
make test-unit
make lint
make typecheck
make test
```

### Key files

- `services/simulator/factory_simulator/cli.py`
- `services/simulator/tests/test_simulator.py`
- `services/simulator/README.md`

### What to learn next

Use the CLI-generated JSONL files as fixtures for ingestion and Process
Sentinel workflows.

## 2026-05-18 - Deterministic simulator seed support

### What changed

Added explicit tests proving every generated simulator scenario produces the
same event payloads for the same seed and different valid payloads for a
different seed. Documented simulator seed usage for reproducible demos, tests,
and issue debugging.

### Why it matters

Deterministic simulator output lets contributors reproduce failures exactly.
That is important for debugging ingestion, Process Sentinel rules, evidence
generation, and future demo walkthroughs without relying on real factory data.

### How it works

The simulator passes the requested seed into a local `Random` instance for each
generation run. Event IDs and timestamps stay stable for a scenario and count,
while seeded noise controls process and quality values.

### How to run it

```bash
make simulate SCENARIO=gradual_drift OUTPUT=.local/events/gradual_drift.jsonl
make simulate SCENARIO=gradual_drift SEED=43 OUTPUT=.local/events/gradual_drift_seed_43.jsonl
```

### How to test it

```bash
make test-unit
make lint
make typecheck
make test
```

### Key files

- `services/simulator/tests/test_simulator.py`
- `services/simulator/README.md`

### What to learn next

Use fixed seeds in integration tests whenever a scenario output needs to be
compared across ingestion, detection, and evidence-generation steps.

## 2026-05-18 - Gradual drift simulator scenario

### What changed

Made the gradual drift generator use the scenario definition's baseline values,
noise bands, and drift rates. Added tests that prove the scenario has a stable
baseline period, a visible upward drift, a delayed failing quality marker, and
valid Factory Event payloads.

### Why it matters

Process Sentinel needs a deterministic drift dataset where process evidence
appears before the quality concern. That lets contributors test early warning,
evidence timeline, and investigation behavior without real factory data.

### How it works

The first eight samples remain at baseline with bounded noise. After that, fill
weight and nozzle pressure increase by their configured `drift_per_step` values.
Quality checks are emitted every third sample, and the first failing quality
event appears only after the process drift has had time to develop.

### How to run it

```bash
make simulate SCENARIO=gradual_drift OUTPUT=.local/events/gradual_drift.jsonl
```

### How to test it

```bash
make test-unit
make lint
make typecheck
make test
```

### Key files

- `services/simulator/factory_simulator/generator.py`
- `services/simulator/tests/test_simulator.py`
- `services/simulator/README.md`

### What to learn next

Use the gradual drift JSONL output to verify ingestion compatibility and
Process Sentinel evidence generation in a follow-up task.

## 2026-05-18 - Normal operation simulator scenario

### What changed

Added focused validation for the simulator's `normal` scenario and documented
the normal-operation CLI command. Process measurement events now include their
configured normal limits and target values, and quality events use the scenario
quality marker specification.

### Why it matters

The normal scenario is the clean baseline for testing ingestion, schema
validation, and Process Sentinel behavior when no quality drift should be
detected. Keeping the generated events self-describing makes later tests easier
to understand.

### How it works

The simulator reads the `normal` scenario definition, generates two process
measurements per sample, and emits an inline quality check every third sample.
With a fixed seed, the same count always produces the same JSONL-ready Factory
Event payloads, and all normal values stay inside the configured ranges.

### How to run it

```bash
make simulate SCENARIO=normal OUTPUT=.local/events/normal.jsonl
```

### How to test it

```bash
make test-unit
make lint
make typecheck
make test
```

### Key files

- `services/simulator/factory_simulator/generator.py`
- `services/simulator/tests/test_simulator.py`
- `services/simulator/README.md`

### What to learn next

Use the normal JSONL output as a baseline fixture for ingestion and Process
Sentinel tests that assert no drift detections are created.

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

## 2026-05-14 - Quality event schema

### What changed

Added `QualityEvent` as the typed factory-events envelope for
`quality.measurement.recorded` events. The quality payload now represents the
quality check type, result value, result status, severity, optional
specification limits, and affected batch/work order context through the shared
event envelope.

### Why it was built that way

Process Sentinel needs a consistent quality outcome contract before it can
correlate process behavior with inspections, lab results, defects, deviations,
or outcome markers. Reusing `FactoryEvent` keeps quality observations aligned
with the shared source metadata, UTC timestamp, and line context rules.

### How data flows through it

A source adapter emits a `quality.measurement.recorded` event with a
quality-specific payload. The shared validator selects the quality payload
model, checks required fields such as `quality_check_type`, `result_status`,
and `severity`, validates optional specification limits, and returns a validated
`FactoryEvent` or `QualityEvent`.

### How to run it

No service command is required for the schema change. Quality payloads can be
validated by importing `validate_event` or `QualityEvent` from
`factory_events`.

### How to test it

```bash
make test-contract
make lint
make typecheck
make test
```

### What to learn next

Use richer quality event types in simulator scenarios so Process Sentinel can
show whether process drift is connected to inspections, lab results, defects,
or deviation signals.

## 2026-05-15 - Project foundation status

### What changed

Added `docs/PROJECT_FOUNDATION.md` to map the project foundation epic to the
actual repository files that satisfy it. Linked the new status page from the
README and file index, and added a direct `good first issue` query to the
contributor guide.

### How it works

The status page points new contributors to setup, issue workflow, PR
expectations, CI, templates, ADRs, and repository structure docs. It also maps
the foundation epic acceptance criteria and original child issues to the files
that now exist in the repository.

### How to run it

No runtime command is required for this documentation-only change.

### How to test it

```bash
make docs
make lint
make typecheck
make test
```

### What to learn next

Keep future foundation improvements as focused issues, such as docs checking,
more CI hardening, or web workbench onboarding once `apps/web` is implemented.

## 2026-05-15 - Factory event contract tests

### What changed

Strengthened the shared factory-events contract test suite so every valid event
fixture is checked through both the public `validate_event` API and the
implemented typed event model. The invalid fixture tests now also assert that
validation failures point to the expected field and include an actionable error
message.

### Why it was built that way

Issue #28 is a test guardrail for the existing shared contracts, not a request
to redesign the event model. Keeping the change in the contract test suite
makes simulator output, ingestion validation, and future connectors safer
without changing runtime behavior.

### How data flows through it

A fixture payload is loaded from `packages/test-fixtures`, passed into
`validate_event`, and then validated against the typed model for its event
category. Invalid fixtures follow the same public validation path and confirm
the contract reports the field that needs to be fixed.

### How to run it

No service command is required. The focused contract suite runs with:

```bash
make test-contract
```

### How to test it

```bash
make test-contract
make lint
make typecheck
make test
```

### What to learn next

Use these contract tests as the first check when adding new event types, then
add simulator fixtures and ingestion tests that prove those new events travel
through the MVP path correctly.

## 2026-05-15 - Example factory event payloads

### What changed

Added contributor-facing JSON examples under `examples/events` for the base
factory event envelope, process signal events, quality events, batch events,
and work order events. The contract test suite now validates those examples
through the shared event models.

### Why it was built that way

Issue #29 asks for examples that contributors can read without opening the
implementation. Keeping examples separate from test fixtures makes the public
examples easier to find while still testing them against the same contract
package used by simulator and ingestion code.

### How data flows through it

Each example follows the shared `FactoryEvent` envelope and uses a supported
event type. The contract tests load each file, call `validate_event`, and then
validate the payload against the matching typed event model when one exists.

### How to run it

No service command is required. The examples can be inspected directly in:

```text
examples/events/
```

### How to test it

```bash
make test-contract
make lint
make typecheck
make test
```

### What to learn next

Use these examples when documenting event naming conventions and when adding
future event types such as recommendation, approval, audit, and asset events.

## 2026-05-16 - Local AI and site intelligence roadmap

### What changed

Updated the roadmap and supporting product, architecture, MVP scope, governance,
and security docs to include local model gateway, SLM-first/LLM-fallback
routing, Site AI Packages, site-specific RAG, training and evaluation pipelines,
model governance, agent orchestration, and validation-aware onboarding.

### How it works

The first MVP remains simulator-backed Process Sentinel. The new AI roadmap
items are positioned as post-MVP expansion work that must stay local-first,
model-agnostic, evidence-cited, audit-friendly, and human-reviewed through
governed recommendation workflows.

### How to run it

No service command is required for this documentation-only change.

### How to test it

```bash
git diff --check
make docs
make lint
make typecheck
make test
```

### What to learn next

Turn the roadmap into focused implementation issues for the Local Model Gateway,
Site AI Package, RAG/Factory Memory, evaluation harness, and model governance
workstreams once the Process Sentinel MVP path is stable.

## 2026-05-18 - Simulator scenario definition format

### What changed

Added a typed simulator scenario definition format for the current demo
scenarios. The format captures scenario metadata, line context, assets, process
tag configuration, quality marker configuration, and output settings.

### How it works

`factory_simulator.scenarios` defines validated scenario objects for `normal`,
`gradual_drift`, and `sudden_excursion`. The simulator still emits the same
kind of deterministic factory events, but scenario names and context now come
from the shared scenario definitions instead of an ad hoc list.

### How to run it

```bash
make simulate SCENARIO=gradual_drift
```

### How to test it

```bash
make test-unit
make lint
make typecheck
make test
```

### What to learn next

Use the scenario definitions to drive future scenario fixtures, including noisy
sensor behavior, without changing the simulator CLI contract.

## 2026-05-19 - JSONL ingestion path

### What changed

Completed the local JSONL ingestion path for simulator output. Ingestion now
checks for missing or non-file inputs before reading, rejects malformed JSON and
non-object JSONL rows into the dead-letter file, and keeps accepted/rejected
summary counts for each run.

### Why it was built that way

The first ingestion path should stay simple and reviewable: read one local file,
validate each candidate event through the shared factory event contracts, append
valid events to the local JSONL store, and preserve invalid rows for inspection.
That proves the ingestion boundary without introducing MQTT, OPC UA, Kafka, or
production streaming infrastructure.

### How data flows through it

The simulator writes one factory event per JSONL line. The ingestion CLI opens
that file, parses each non-empty line, validates the event with
`packages/factory-events`, appends accepted events to
`.local/storage/events.jsonl`, and writes rejected rows to
`.local/storage/dead_letter.jsonl` with the source line number and error.

### How to run it

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use the accepted event store as the handoff point into Process Sentinel, then
add focused integration tests that prove detections are built from ingested
events rather than simulator objects in memory.

## 2026-05-19 - Ingestion schema validation

### What changed

Added an ingestion-facing validation wrapper around the shared factory event
schemas. Invalid incoming events now produce structured validation issues with
field paths, messages, and issue types, and those details are written into
dead-letter records.

### Why it was built that way

The shared `packages/factory-events` models remain the source of truth for
event contracts. The ingestion service only translates schema failures into
operational error details so downstream services stay protected without
duplicating validation rules.

### How data flows through it

JSONL rows are parsed into candidate event objects, passed to
`validate_incoming_event`, and validated by the shared event schemas. Valid
events continue into accepted storage. Invalid events are rejected before
storage and written to the dead-letter file with the raw row and structured
validation context.

### How to run it

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

### How to test it

```bash
make test-integration
make test-contract
make test
make lint
make typecheck
```

### What to learn next

Use the structured dead-letter details to build the next ingestion reporting
slice, including clearer summaries for accepted and rejected records.

## 2026-05-19 - Local accepted-event storage

### What changed

Hardened the MVP local accepted-event store. Accepted events are written to
`.local/storage/events.jsonl` as valid JSONL, invalid events are excluded from
that store, and repeated ingestion of the same deterministic simulator output no
longer appends duplicate rows for the same `event_id`.

### Why it was built that way

The MVP needs a simple handoff between ingestion, Process Sentinel, and the API
before PostgreSQL persistence is required. A local JSONL store keeps the data
easy to inspect while matching the existing simulator-first development loop.

### How data flows through it

The ingestion worker validates each candidate event and calls `JsonlEventStore`
only for accepted events. The store serializes one validated factory event per
line and skips duplicate `event_id` values so local reruns remain repeatable.
Process Sentinel and the API use the same `.local/storage/events.jsonl` path by
default.
## 2026-05-19 - Dead-letter handling for invalid events

### What changed

Expanded local dead-letter records for rejected ingestion rows. Each record now
includes the source file path, line number, rejection timestamp, top-level error,
structured validation errors, raw input text, and the parsed original payload
when JSON parsing succeeds. The ingestion summary also reports
`dead_letter_count`.

### Why it was built that way

Dead-letter handling is the traceability boundary for bad input. Keeping it as
local JSONL preserves the MVP's simulator-first workflow while giving
contributors enough context to debug malformed or schema-invalid records.

### How data flows through it

The ingestion worker reads each JSONL line, parses and validates candidate
events, appends valid events to the accepted store, and writes rejected records
to `.local/storage/dead_letter.jsonl`. Malformed JSON keeps the original text in
`raw`; schema-invalid JSON also keeps the parsed `payload` for inspection.

### How to run it

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use this accepted-event store as the stable input for the next Process Sentinel
integration tests, then defer PostgreSQL persistence and retention policy work
to later issues.
Use the dead-letter count and structured error fields as the basis for a focused
ingestion summary/reporting issue, without adding retry queues or production
message-broker dead-letter topics yet.

## 2026-05-19 - Ingestion summary output

### What changed

Added a human-readable ingestion summary to the ingestion CLI. The summary now
shows the input file, accepted event count, rejected event count,
dead-letter count, accepted output path, dead-letter output path, and a few
validation error examples when records are rejected.

### Why it was built that way

Contributors should be able to understand an ingestion run without opening the
event store or dead-letter file first. The CLI still writes the detailed data to
local JSONL files, but the terminal output now gives enough context to decide
what to inspect next.

### How data flows through it

`ingest_jsonl` validates and routes each input row, then the CLI formats the
result into a summary. When rejected records exist, the CLI reads the first few
dead-letter records and includes their line number and useful error detail in
the summary.

### How to run it

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use the summary output as the contributor-facing surface for future ingestion
reporting work, while keeping retry queues, broker topics, and UI reporting for
later scoped issues.

## 2026-05-19 - Ingestion integration tests

### What changed

Added integration tests for the simulator-to-ingestion file path. The tests use
deterministic simulator-generated events, run them through the ingestion CLI,
verify accepted events are stored, verify invalid events go to dead-letter
storage, and assert the ingestion summary counts are correct.

### Why it was built that way

This keeps the test focused on the MVP boundary between the simulator and
ingestion worker without adding real connectors, databases, or message brokers.
Using `tmp_path` keeps test output isolated from developer `.local/` data.

### How data flows through it

The simulator produces valid factory event objects, the test writes them as
JSONL input, the ingestion CLI validates each row, accepted events are persisted
to a temporary JSONL store, and rejected records are written to a temporary
dead-letter file with useful error context.

### How to run it

```bash
make test-integration
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use this integration coverage as the base for the next Process Sentinel tests
that consume ingested events from local storage.

## 2026-05-19 - Local ingestion workflow documentation

### What changed

Expanded the ingestion service README with the full local
simulator-to-ingestion workflow, default generated file paths, accepted-event
and dead-letter inspection commands, reset commands, and troubleshooting notes.

### Why it was built that way

Issue #45 is documentation-focused, so the smallest useful change is a
contributor-facing guide near the ingestion service instead of new runtime
behavior. The guide uses the existing Makefile defaults so contributors can
copy commands directly from the docs.

### How data flows through it

The simulator writes JSONL events under `.local/events/`, ingestion validates
each line through the shared factory event contracts, accepted records are
appended to `.local/storage/events.jsonl`, and invalid records are written to
`.local/storage/dead_letter.jsonl` with structured error details.

### How to run it

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

### How to test it

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make docs
git diff --check
```

### What to learn next

Use the documented local ingestion workflow as the contributor baseline for the
next storage, Process Sentinel, or API documentation tasks.

## 2026-05-19 - Shared event model epic completion

### What changed

Completed the remaining shared event model gaps by adding asset status and
typed recommendation event contracts, valid and invalid contract fixtures,
contributor-facing example payloads, contract tests, and documentation updates.

### Why it was built that way

Issue #8 is the shared event model epic, so the implementation stayed inside
the existing factory-events package and documentation. The new contracts reuse
the existing `FactoryEvent` envelope and Pydantic validation pattern instead of
adding a new schema system.

### How it works

`validate_event` chooses the payload model from `event_type`, validates the
typed payload, then applies envelope rules such as UTC timestamps, schema
version, simulator metadata, and matching asset identifiers. Asset status
events provide equipment state context, while recommendation events represent
governed, evidence-backed advisory output from Process Sentinel.

### How to run it

```bash
make test-contract
```

### How to test it

```bash
make test-contract
make test
make lint
make typecheck
```

### What to learn next

Use the shared event model as the stable boundary for simulator, ingestion,
Process Sentinel, and API work. Future event additions should include typed
models, fixtures, examples, docs, and contract tests in the same change.

## 2026-05-19 - Manufacturer demo simulator scenario

### What changed

Added the `fill_weight_drift_demo` simulator scenario for the demo-ready
Process Sentinel path. The scenario defines one demo site, area, line, product,
work order, and affected filler asset, then produces baseline operation,
gradual fill-weight drift, and a delayed quality concern.

### Why it was built that way

Issue #120 asks for a polished deterministic demo scenario, so the change stays
inside the existing simulator and Process Sentinel test paths. The scenario
reuses the existing shared event contracts, ingestion flow, and Process
Sentinel drift rule instead of adding separate demo-only logic.

### How it works

The simulator uses the scenario definition to generate deterministic process
and quality JSONL events. Process Sentinel reads the ingested events, detects
the fill-weight drift, attaches process and quality evidence, creates a
human-reviewed recommendation, and leaves enough state for the RCA/CAPA draft
builder to produce a preview.

### How to run it

```bash
make simulate SCENARIO=fill_weight_drift_demo SEED=120 COUNT=30 OUTPUT=.local/events/fill_weight_drift_demo.jsonl
make ingest INPUT=.local/events/fill_weight_drift_demo.jsonl EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl
make sentinel-run EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-unit
make test
make lint
make typecheck
```

### What to learn next

Use this scenario as the stable manufacturer demo input for the upcoming UI,
demo runbook, smoke test, and presentation polish issues.

## 2026-05-19 - Realistic seeded demo data pack

### What changed

Updated the manufacturer demo seed data to use realistic demo names and IDs:
Greenville Demo Site, Packaging Area, Line 2, Filler F-201, Checkweigher
CW-201, OFI Demo Beverage, `WO-DEMO-1007`, and `BATCH-DEMO-1007`. The API demo
domain data now matches those names, and the demo runbook records the expected
IDs and output.

### Why it was built that way

Issue #121 is about making the demo feel like a real manufacturing workflow.
The change keeps the existing event contracts and simulator architecture intact
while improving the seeded data that UI cards, API endpoints, and demo scripts
will display.

### How it works

The simulator emits process and quality events with realistic site, line, work
order, batch, asset, source, trace, and tag fields. The API domain seed exposes
the corresponding display names so overview and detail cards can show readable
manufacturing context without connecting to real plant systems.

### How to run it

```bash
make simulate SCENARIO=fill_weight_drift_demo SEED=120 COUNT=30 OUTPUT=.local/events/fill_weight_drift_demo.jsonl
make ingest INPUT=.local/events/fill_weight_drift_demo.jsonl EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl
make sentinel-run EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-unit
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use these realistic demo IDs as the shared contract for the upcoming demo
runbook, smoke test, and Operations Workbench cards.

## 2026-05-19 - Demo reset and data commands

### What changed

Added `make demo-reset`, `make demo-data`, `make demo-ingest`, and
`make demo-sentinel-run` for the deterministic manufacturer demo path. The demo
runbook, root README, and simulator README now document the commands and their
generated local paths.

### Why it was built that way

Issue #122 needs a reliable pre-call setup flow without touching production
storage or real plant data. Dedicated demo targets keep the polished demo path
repeatable while leaving the generic simulator, ingestion, and Sentinel targets
available for contributor experiments.

### How it works

The demo targets use the seeded `fill_weight_drift_demo` scenario and write all
generated state under `.local/`. `make demo-reset` removes the demo JSONL event
file, local accepted event store, demo dead-letter file, and Sentinel state
directory, then `make demo-data`, `make demo-ingest`, and
`make demo-sentinel-run` rebuild the path from scratch.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
```

### How to test it

```bash
make test-unit
make test
make lint
make typecheck
```

### What to learn next

Build the demo smoke test around these commands so future UI and runbook work
can verify the same reset, seed, ingest, and Sentinel sequence before calls.

## 2026-05-19 - Demo ingestion verification

### What changed

Added demo-specific ingestion tests for the `fill_weight_drift_demo` data path
and documented the expected `make demo-ingest` command, output paths, accepted
count, rejected count, and dead-letter behavior.

### Why it was built that way

Issue #123 is a verification task, not a new connector or storage rewrite. The
implementation keeps the existing ingestion service intact and proves the
manufacturer demo data flows through the same validation and JSONL storage path
as the rest of the MVP.

### How it works

The simulator generates 70 deterministic demo events. Ingestion validates each
event against the shared factory event contracts, writes accepted events to the
demo event store, creates the demo dead-letter file, and reports
accepted/rejected/dead-letter counts in the CLI summary. A mixed-input test also
confirms invalid demo rows are routed to dead-letter storage while valid rows
continue into the accepted store.

### How to run it

```bash
make demo-data
make demo-ingest
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use the verified demo ingestion path as one step in the upcoming full demo smoke
test.

## 2026-05-19 - Demo ingestion troubleshooting notes

### What changed

Added demo ingestion troubleshooting notes to the demo runbook and linked the
demo-specific paths from the ingestion README. The notes list where demo events,
accepted events, dead-letter records, and Sentinel state are written, plus the
expected deterministic counts for a clean demo run.

### Why it was built that way

Issue #124 is about recovering quickly when no detections appear during demo
prep. The docs focus on the smallest reliable recovery path: reset generated
demo state, regenerate deterministic simulator data, ingest it, and rerun
Process Sentinel.

### How it works

The troubleshooting flow keeps all generated files under `.local/`. A clean
demo run should produce 70 generated events, 70 accepted events, 0 rejected
events, 0 dead-letter rows, and one Sentinel detection with evidence and a
recommendation. If those counts drift, the runbook points contributors to the
likely ingestion or path mismatch.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
```

### How to test it

```bash
make docs
make test-integration
make lint
make typecheck
```

### What to learn next

Fold this troubleshooting sequence into the future demo smoke test so failures
can show a clear recovery path before a manufacturer call.

## 2026-05-19 - Demo Sentinel detection verification

### What changed

Added verification for the expected `fill_weight_drift_demo` Process Sentinel
detection and documented the lookup behavior in the demo runbook. The tests now
check the stable detection ID, summary, severity, confidence, related work
order, related asset, and API detail endpoint.

### Why it was built that way

Issue #125 needs confidence that the existing demo data reliably produces the
intended detection. The smallest safe change is to lock down the current
rule-based Sentinel behavior and API exposure instead of adding a new detection
algorithm.

### How it works

The deterministic demo data flows through ingestion into the local event store.
Process Sentinel reads that event store, identifies the gradual fill-weight
drift, writes Sentinel state under `.local/storage/fill_weight_drift_demo_sentinel/`,
and the API exposes the detection through `/sentinel/detections` and
`/sentinel/detections/det_fill_weight_gradual_drift`.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-unit
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use this stable detection contract for the upcoming evidence timeline,
recommendation review, RCA/CAPA preview, and full demo smoke test issues.

## 2026-05-19 - Demo detection copy polish

### What changed

Updated the demo Process Sentinel detection summary to use advisory,
manufacturer-friendly language. The tests now verify that the copy explains the
risk without claiming a root cause, and the demo runbook reflects the final
expected wording.

### Why it was built that way

Issue #126 is copy polish for the existing demo detection, not a new detection
algorithm. The summary stays inside the existing deterministic rule output so
the API and planned UI can use the same language without adding another layer.

### How it works

Process Sentinel still detects the fill-weight drift from the same simulator
events. The detection now says the trend may move the affected work order toward
the upper quality limit, framing the output as advisory decision support and
leaving root-cause determination to human investigation.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
```

### How to test it

```bash
make test-unit
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Carry the same advisory wording style into the evidence, recommendation, and
RCA/CAPA preview demo steps.

## 2026-05-19 - Demo evidence timeline readiness

### What changed

Made the demo evidence timeline behavior explicit and test-covered. Evidence is
returned in chronological order, and the tests now verify readable titles,
descriptions, evidence types, source event IDs, scores, and the link between
process signal behavior and the quality concern. The demo runbook includes the
expected evidence endpoint and example evidence items.

### Why it was built that way

Issue #128 asks for demo-ready evidence, not charting or a new investigation
engine. The implementation keeps the existing Process Sentinel evidence model
and API endpoint, adds ordering at the state-store boundary, and locks down the
fields the demo UI will need.

### How it works

Process Sentinel creates process-signal evidence that compares baseline and
recent fill-weight averages, then quality evidence that shows recent quality
checks moving in the same direction. The API returns those records from
`/sentinel/detections/det_fill_weight_gradual_drift/evidence` with timestamps,
titles, descriptions, source event IDs, evidence types, and scores.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-unit
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use the evidence contract in the upcoming recommendation review, RCA/CAPA
preview, and Operations Workbench demo screens.

## 2026-05-19 - Evidence timeline API/UI contract

### What changed

Added an evidence timeline API/UI contract for the Operations Workbench. The
contract documents the endpoint, UI-needed fields, demo response example,
empty-state behavior, error-state behavior, and confirms that the current API
returns the fields needed for the MVP evidence display.

### Why it was built that way

Issue #129 is a contract alignment task between API and UI work. The backend
already returns the required evidence fields, so the smallest useful change is a
stable contract document plus tests for the documented empty and not-found
states.

### How it works

The Workbench should call
`GET /sentinel/detections/{detection_id}/evidence` and render the returned
chronological evidence items. Each item includes the evidence type, timestamp,
title, description, source event IDs, and score. Existing detections with no
evidence return an empty array; missing detections return the standard
`detection_not_found` error shape.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use this contract when implementing the Operations Workbench evidence timeline
component.

## 2026-05-19 - Recommendation review workflow

### What changed

Verified the demo recommendation review workflow and tightened the API response
used by the future Operations Workbench confirmation state. The recommendation
endpoints now have tests for the demo recommendation fields and approve, reject,
and defer decision paths.

### Why it was built that way

Issue #130 is about proving the governed review path for the demo, not adding
multi-user approval chains or production electronic signatures. The existing
local Sentinel state store already supports decisions, so the change keeps the
workflow simulator-backed and human-reviewed.

### How it works

Process Sentinel creates a `needs_review` recommendation with a recommended
action, rationale, risk level, approval requirement, and evidence IDs. A reviewer
posts to `/approve`, `/reject`, or `/defer` with their name and reason. The API
updates local recommendation state, records a local approval decision and audit
event, and returns confirmation fields including reviewer, decision, reason,
timestamp, and recommendation ID.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use the documented review response shape when building the Workbench
recommendation approval panel.

## 2026-05-19 - RCA/CAPA draft preview contract

### What changed

Verified the demo RCA/CAPA draft generation path and added an explicit
`human_review_required` field to the draft response. The API and Sentinel tests
now check the draft title, problem statement, evidence summary, recommended
containment, CAPA placeholder structure, and human-review requirement.

### Why it was built that way

Issue #131 only needs a previewable quality-facing draft for the manufacturer
demo. The implementation keeps the draft derived from existing detection,
evidence, and governed recommendation state rather than adding a Markdown export
pipeline, QMS integration, or automatic CAPA creation.

### How it works

The API calls the local Sentinel state store for
`GET /reports/rca-capa-drafts/{detection_id}`. The store looks up the detection,
collects its evidence descriptions, finds the matching recommendation action,
and returns draft data marked as requiring human review.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel
```

### How to test it

```bash
make test-unit
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use this response shape when building the Workbench RCA/CAPA draft preview.

## 2026-05-19 - Backend demo API smoke test

### What changed

Added a backend-only smoke test for the deterministic demo data path. The new
`make demo-api-smoke` command verifies the generated demo event store and checks
the API app for the expected detection, evidence, recommendation, decision, and
RCA/CAPA draft responses.

### Why it was built that way

Issue #136 needs demo readiness coverage without waiting for browser E2E. The
smoke test runs against a temporary copy of local demo state so it can exercise
the decision endpoint without changing the prepared demo files.

### How it works

After `make demo-data`, `make demo-ingest`, and `make demo-sentinel-run`, the
smoke command creates a FastAPI test client for the local demo event store and a
copied Sentinel state directory. It fails with a clear setup message when the
demo files are missing.

### How to run it

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make demo-api-smoke
```

### How to test it

```bash
make test-integration
make test
make lint
make typecheck
```

### What to learn next

Use this backend smoke test as the stable base for the later browser E2E demo
workflow.

## 2026-05-19 - Operations Workbench app shell

### What changed

Created the first runnable Next.js Operations Workbench shell under `apps/web`.
The app includes a shared header, primary navigation, Overview, Detections,
Recommendations, and RCA/CAPA Draft placeholder routes, plus a configurable API
base URL.

### Why it was built that way

Issue #95 is the frontend foundation for the demo, not the full Workbench
workflow. The shell keeps UI scope small, labels simulator-backed demo data
clearly, and avoids auth, deployment, enterprise navigation, or production
tenant concepts.

### How it works

The app uses Next.js App Router routes under `apps/web/app`. The API target is
read from `NEXT_PUBLIC_API_BASE_URL` and defaults to `http://127.0.0.1:8000`.
Placeholder pages document which backend endpoints later issues should connect
to.

### How to run it

```bash
cd apps/web
npm install
npm run dev
```

### How to test it

```bash
cd apps/web
npm run lint
npm run typecheck
npm test
npm run build
```

### What to learn next

Connect the detection placeholder to the FastAPI detection and evidence
endpoints.
