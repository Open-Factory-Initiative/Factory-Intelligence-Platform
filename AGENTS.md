# AGENTS.md

Instructions for Codex and other coding agents working in this repository.

## Project Identity

This repository is the **Factory Intelligence Platform**, an open-source platform under the **Open Factory Initiative**.

The long-term product is a modular **Factory Intelligence Layer** for intelligent, connected, AI-ready factories.

The first MVP vertical slice is **Process Sentinel**:

```text
Synthetic Factory Simulator
→ Ingestion Worker
→ Unified Factory Event Model
→ Drift Detection
→ Evidence Timeline
→ Governed Recommendation Workflow
→ Web UI Workbench
→ RCA / CAPA Draft
→ Factory Memory
```

## Primary Goal

Build a professional, testable, documented, open-source platform that can evolve from a simulator-backed MVP into a real industrial intelligence platform.

Favor small, reviewable pull requests. Do not attempt to build the entire platform in one task.

## How Codex Should Work

Before implementing any non-trivial change:

1. Read this file.
2. Read `docs/START_HERE_FOR_CODEX.md`.
3. Read the relevant architecture and testing docs.
4. Propose a concise plan.
5. Identify files to change.
6. Implement the smallest useful vertical slice.
7. Add or update tests.
8. Add or update documentation.
9. Update `docs/LEARNING_LOG.md` with a short explanation of what changed and how it works.

## Teaching Requirement

This repo is being built as both software and a learning project.

After each meaningful change, include:

- What was built
- Why it was built that way
- How data flows through it
- How to run or test it
- What the next learning step should be

Keep explanations practical and beginner-friendly without hiding important engineering detail.

## Architecture Rules

Use the architecture in `docs/ARCHITECTURE.md` as the source of truth.

Do not bypass the core platform layers:

- Source adapters ingest raw data.
- The unified factory event model normalizes data.
- Platform services read/write through documented interfaces.
- Detection services produce evidence-backed signals.
- Governed actions require explicit human approval before high-impact action.
- UI features should reflect actual backend state, not fake hardcoded flows unless clearly marked as demo data.

## Suggested Initial Stack

Unless the maintainer changes direction, assume:

- Python + FastAPI for backend services
- TypeScript + React / Next.js for the web app
- PostgreSQL for durable relational data
- Timescale-compatible schema patterns for time-series data
- MQTT-compatible ingestion path for local development
- Pytest for backend tests
- Playwright for e2e tests
- Docker Compose for local orchestration

## Directory Intent

Recommended structure:

```text
apps/web/                  Web UI workbench
services/api/              Public API gateway and app backend
services/ingestion/        Data ingestion workers and adapters
services/simulator/        Synthetic factory data generator
services/process-sentinel/ Drift detection and investigation workflow
packages/factory-events/   Shared schemas, contracts, and fixtures
packages/test-fixtures/    Reusable test data
infra/docker/              Local Docker Compose and service config
docs/                      Product, architecture, testing, contributor docs
prompts/                   Codex prompts for staged implementation
```

If the actual repo structure differs, update this file and the docs after confirming the new structure.

## Testing Expectations

Every meaningful change must include tests.

Minimum expectations:

- Unit tests for business logic
- Integration tests for service boundaries
- Contract tests for event schemas and API contracts
- End-to-end tests for the MVP path
- Regression tests for bugs

Do not mark work complete unless the relevant tests pass or the failure is clearly documented.

## Documentation Expectations

Update docs when behavior changes.

Documentation should include:

- What changed
- How to run it
- How to test it
- What assumptions were made
- Any new environment variables
- Any new API endpoints or data contracts

## Safety and Governance Rules

This platform may eventually interact with real industrial systems. Treat that seriously.

Never implement autonomous high-impact industrial actions by default.

High-impact actions must be:

- Evidence-backed
- Audited
- Human-approved
- Reversible when possible
- Clearly separated from recommendations

Examples of high-impact actions:

- Changing production parameters
- Releasing or quarantining product
- Modifying a work order
- Closing a deviation
- Sending data to an external system
- Creating a CAPA or quality record

## Dependency Rules

Prefer mature, open-source dependencies.

Before adding a dependency, explain:

- Why it is needed
- Why the standard library or existing project dependency is not enough
- License compatibility
- Security or maintenance concerns

## Code Quality Rules

- Prefer clear code over clever code.
- Keep modules small and testable.
- Use type hints in Python.
- Use TypeScript types for UI and shared contracts.
- Avoid hidden global state.
- Avoid hardcoded credentials.
- Use environment variables for configuration.
- Add structured logging for service behavior.
- Keep demo data clearly separated from production-style code.

## Pull Request Definition of Done

A change is done when:

- It implements the requested behavior.
- It includes relevant tests.
- It updates relevant docs.
- It has no obvious secrets or unsafe defaults.
- It is small enough to review.
- It includes a learning summary in `docs/LEARNING_LOG.md`.
- It passes the documented lint/test commands or explains why they cannot run yet.

## Do Not Do

- Do not build broad features without an approved plan.
- Do not silently change architecture.
- Do not remove tests to make a task pass.
- Do not add proprietary or cloud-only dependencies without approval.
- Do not use real plant names, customer data, or confidential examples.
- Do not implement direct writeback to real industrial systems in the MVP.
- Do not claim production readiness without evidence.

## If Unsure

When uncertain, prefer:

1. A smaller implementation
2. More tests
3. Better documentation
4. Explicit assumptions
5. Human approval for industrial actions
