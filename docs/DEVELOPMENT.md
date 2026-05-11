# Development Guide

## Prerequisites

Recommended local tools:

- Git
- Docker Desktop or compatible Docker runtime
- Node.js LTS
- Python 3.12+
- Make
- Codex CLI
- A code editor

## Clone

```bash
git clone https://github.com/Open-Factory-Initiative/Factory-Intelligence-Platform.git
cd Factory-Intelligence-Platform
```

## Install Codex CLI

```bash
npm i -g @openai/codex
```

Then run:

```bash
codex
```

## First Codex Session

From the repo root:

```text
Read AGENTS.md, PLANS.md, CODE_REVIEW.md, docs/START_HERE_FOR_CODEX.md, docs/ARCHITECTURE.md, docs/MVP_SCOPE.md, and docs/TESTING.md.

Do not write code yet. Inspect the repository and propose a first implementation plan.
```

## Recommended Branch Workflow

```bash
git checkout -b docs/codex-starter-kit
```

For implementation:

```bash
git checkout -b feat/simulator-vertical-slice
```

## Local Development Target

The current MVP skeleton supports a backend-first local loop:

```bash
make setup
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
make api
```

This generates simulator events, validates and stores them in `.local/`, runs
Process Sentinel, and starts the FastAPI API.

Use `make api-reload` when you want the FastAPI process to restart after file
changes. The default `make api` command avoids file watching so it is more
reliable in constrained agent and CI environments.

To start the local PostgreSQL service for durable storage work:

```bash
make dev-db
```

The web app is intentionally a placeholder until the backend workflow has stable
state to display.

Current skeleton components:

- `packages/factory-events` — shared event contracts
- `services/simulator` — deterministic scenario generator
- `services/ingestion` — validation and dead-letter handling
- `services/process-sentinel` — drift rules, evidence, recommendations
- `services/api` — FastAPI endpoints for the MVP state
- `infra/docker` — PostgreSQL compose config

## Environment Variables

Create `.env.example` before requiring `.env`.

Recommended pattern:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/factory_intelligence
MQTT_BROKER_URL=mqtt://localhost:1883
APP_ENV=development
LOG_LEVEL=info
SIMULATOR_SEED=42
FACTORY_EVENTS_STORE=.local/storage/events.jsonl
SENTINEL_STATE_DIR=.local/storage/sentinel
```

Do not commit real secrets.

## Commit Guidance

Good commit examples:

```text
docs: add codex starter architecture
feat(simulator): add seeded drift scenario generator
test(sentinel): cover gradual drift rule
```

## Pull Request Guidance

Every PR should include:

- Summary
- Why the change was made
- Test evidence
- Documentation updates
- Screenshots for UI changes
- Risks or follow-up work
