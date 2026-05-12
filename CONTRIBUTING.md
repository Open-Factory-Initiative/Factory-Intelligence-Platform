# Contributing

Thank you for contributing to the Factory Intelligence Platform.

This project is part of the Open Factory Initiative, a community building
open-source infrastructure for intelligent, connected, and AI-ready factories.
The first MVP vertical slice is Process Sentinel: a simulator-backed workflow
for detecting process and quality drift, gathering evidence, and supporting
human-approved recommendations.

## Before You Start

Please read:

- [README.md](./README.md)
- [AGENTS.md](./AGENTS.md)
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- [docs/MVP_SCOPE.md](./docs/MVP_SCOPE.md)
- [docs/TESTING.md](./docs/TESTING.md)
- [CODE_REVIEW.md](./CODE_REVIEW.md)
- [SUPPORT.md](./SUPPORT.md)

## Project Structure

The current skeleton is backend-first and simulator-backed:

- `packages/factory-events` - shared event contracts and fixtures
- `services/simulator` - deterministic synthetic factory data
- `services/ingestion` - event validation, storage, and dead-letter handling
- `services/process-sentinel` - drift detection rules and recommendations
- `services/api` - FastAPI endpoints for local MVP state
- `apps/web` - placeholder for the future workbench
- `infra/docker` - local Docker Compose configuration
- `docs` - architecture, testing, domain, and contributor documentation

## Issue Types

Work is tracked in GitHub Issues and grouped under epics when useful.

- `Epic` - a larger outcome that groups related issues.
- `Feature` - a user-visible or platform capability.
- `Task` - focused implementation, documentation, or maintenance work.
- `Bug` - incorrect behavior or broken developer workflow.
- `Research` - investigation needed before implementation.
- `ADR` - an architecture decision record. See
  [docs/decisions/README.md](./docs/decisions/README.md).

## Finding Beginner-Friendly Work

Start with issues labeled `good first issue` when available. Good first issues
should be narrow, well-described, and safe to complete without redesigning the
platform.

If no `good first issue` work is available, look for small `Task` or
documentation issues in the current milestone. Before starting, comment on the
issue with your intended scope so maintainers can help keep the change focused.

## Local Setup

Prerequisites:

- Git
- Python 3.12+
- Make
- Docker Desktop or another Docker Compose-compatible runtime

Clone and install the development environment:

```bash
git clone https://github.com/Open-Factory-Initiative/Factory-Intelligence-Platform.git
cd Factory-Intelligence-Platform
make setup
```

`make setup` creates a repo-local `.venv` and installs development dependencies
from `requirements-dev.txt`. The first run needs network access to PyPI unless
the packages are already available in your local pip cache.

Optional: create a local environment file from the checked-in template:

```bash
cp .env.example .env
```

Run the simulator-backed MVP path:

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
make api
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Start the optional PostgreSQL service when working on durable storage:

```bash
make dev-db
```

The default MVP loop uses JSONL files under `.local/`, so PostgreSQL is not
required for most starter issues.

## Test Commands

Run the baseline validation before opening a pull request:

```bash
make lint
make typecheck
make test
```

Run narrower suites while iterating:

```bash
make test-unit
make test-integration
make test-contract
make test-e2e
make docs
```

`make test-e2e` and `make docs` are documented placeholders until the web
workbench and docs checker are implemented.

## Branch Naming

Create a branch from `main` and keep the branch name tied to the issue:

```bash
git switch main
git pull
git switch -c task/issue-number-short-name
```

Use these prefixes:

- `feature/issue-number-short-name`
- `task/issue-number-short-name`
- `bugfix/issue-number-short-name`
- `research/issue-number-short-name`
- `docs/issue-number-short-name`

## Pull Request Expectations

Keep pull requests small and reviewable. Each PR should:

- link the relevant issue and include `Closes #issue-number` when it should
  close the issue
- summarize what changed and why
- include exact test commands and results
- call out documentation impact
- include screenshots for UI changes
- explain risks, assumptions, or follow-up work
- avoid secrets, proprietary plant data, and unsafe industrial writeback
- update `docs/LEARNING_LOG.md` for meaningful changes

## Code Style

Prefer clarity over cleverness.

Use:

- type hints for Python
- TypeScript types for frontend code
- explicit schemas for contracts
- structured logs for service behavior
- small modules with tests close to behavior

## Industrial Safety

Do not add direct writeback to real industrial systems without a design
discussion, governance model, audit requirements, and maintainer approval.
Recommendations should stay evidence-backed and human-approved.

Do not use real plant names, customer data, credentials, or confidential
operational examples.

## Asking Questions

Use GitHub Issues for bugs, setup problems, documentation gaps, and scoped work
proposals. Use GitHub Discussions if enabled for broader ideas, use cases,
roadmap discussion, and contributor introductions.

Before opening a question, include what you tried, what happened, what you
expected, relevant logs or screenshots, your operating system, and whether you
used simulator data or a real integration.
