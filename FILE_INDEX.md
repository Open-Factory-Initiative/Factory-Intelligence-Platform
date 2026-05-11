# File Index

This package is designed to be copied into the root of:

```text
https://github.com/Open-Factory-Initiative/Factory-Intelligence-Platform
```

## Root Files

- `README.md` — project overview and architecture summary
- `requirements-dev.txt` — Python development dependency list for the MVP skeleton
- `AGENTS.md` — Codex repository instructions
- `PLANS.md` — execution plan template for Codex
- `CODE_REVIEW.md` — review rubric
- `CONTRIBUTING.md` — contributor guide
- `CODE_OF_CONDUCT.md` — community standards
- `SECURITY.md` — security and industrial safety reporting
- `SUPPORT.md` — support guidance
- `GOVERNANCE.md` — governance model
- `ROADMAP.md` — phased project roadmap
- `CHANGELOG.md` — changelog starter
- `Makefile` — placeholder command interface
- `.env.example` — environment variable template
- `.editorconfig` — editor defaults
- `.gitignore` — ignore rules

## Docs

- `docs/START_HERE_FOR_CODEX.md` — first file to read before using Codex
- `docs/CODEX_LOCAL_SETUP.md` — Codex CLI setup and workflow
- `docs/ARCHITECTURE.md` — full platform architecture
- `docs/PRODUCT_REQUIREMENTS.md` — product thesis and requirements
- `docs/MVP_SCOPE.md` — first vertical slice
- `docs/DOMAIN_MODEL.md` — core manufacturing entities
- `docs/DATA_CONTRACTS.md` — event contracts and examples
- `docs/UNIFIED_NAMESPACE.md` — UNS/topic model
- `docs/GOVERNED_ACTIONS.md` — recommendation and approval model
- `docs/API_DESIGN.md` — initial API shape
- `docs/TESTING.md` — unit/integration/contract/e2e strategy
- `docs/DEVELOPMENT.md` — local development workflow
- `docs/DOCUMENTATION.md` — documentation standards
- `docs/OBSERVABILITY.md` — logging/metrics/traceability direction
- `docs/SECURITY_MODEL.md` — security and safety model
- `docs/LEARNING_MODE.md` — how Codex should teach while building
- `docs/LEARNING_LOG.md` — running learning journal
- `docs/decisions/0001-platform-architecture.md` — first ADR

## Prompts

- `prompts/00-repo-inspection-and-plan.md`
- `prompts/01-repository-foundation.md`
- `prompts/02-shared-event-contracts.md`
- `prompts/03-synthetic-factory-simulator.md`
- `prompts/04-ingestion-service.md`
- `prompts/05-api-service.md`
- `prompts/06-process-sentinel.md`
- `prompts/07-evidence-timeline.md`
- `prompts/08-governed-recommendations.md`
- `prompts/09-web-workbench.md`
- `prompts/10-rca-capa-draft.md`
- `prompts/11-e2e-tests.md`
- `prompts/12-documentation-hardening.md`
- `prompts/13-review-and-refactor.md`

## GitHub Files

- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/documentation.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/workflows/ci.yml`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`

## MVP Skeleton Code

- `packages/factory-events/` — shared factory event schemas and contract tests
- `packages/test-fixtures/` — valid, invalid, and drift scenario fixtures
- `services/simulator/` — deterministic simulator scenario generator
- `services/ingestion/` — event validation, dead-letter handling, and storage schema
- `services/process-sentinel/` — drift rules, evidence, recommendations, and state store
- `services/api/` — FastAPI API over MVP state
- `apps/web/` — placeholder for the future web workbench
- `infra/docker/` — local PostgreSQL Docker Compose config
