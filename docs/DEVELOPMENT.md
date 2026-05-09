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

The eventual local stack should support:

```bash
make dev
```

Expected services:

- Web UI
- API
- Simulator
- Ingestion worker
- PostgreSQL
- MQTT broker

## Environment Variables

Create `.env.example` before requiring `.env`.

Recommended pattern:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/factory_intelligence
MQTT_BROKER_URL=mqtt://localhost:1883
APP_ENV=development
LOG_LEVEL=info
SIMULATOR_SEED=42
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
