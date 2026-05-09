# Start Here For Codex

This document explains how to use Codex to build the Factory Intelligence Platform.

## First Principle

Do not ask Codex to build the whole platform at once.

Use Codex to build small, tested, documented vertical slices.

## Recommended Codex Workflow

1. Start Codex from the repository root.
2. Ask Codex to read:
   - `AGENTS.md`
   - `PLANS.md`
   - `CODE_REVIEW.md`
   - `docs/ARCHITECTURE.md`
   - `docs/MVP_SCOPE.md`
   - `docs/TESTING.md`
   - The relevant prompt in `prompts/`
3. Use plan mode before code.
4. Review the plan.
5. Let Codex implement only that step.
6. Run tests.
7. Ask Codex to review its own diff.
8. Commit.
9. Move to the next prompt.

## First Prompt To Run

Use this first:

```text
Read AGENTS.md, PLANS.md, CODE_REVIEW.md, docs/START_HERE_FOR_CODEX.md, docs/ARCHITECTURE.md, docs/MVP_SCOPE.md, docs/DOMAIN_MODEL.md, docs/DATA_CONTRACTS.md, and docs/TESTING.md.

Do not write code yet.

Inspect the current repository. Create a practical implementation plan for the first MVP skeleton of the Factory Intelligence Platform. The plan should include the proposed repo structure, service boundaries, initial development commands, initial tests, and documentation updates. Keep the first implementation focused on a simulator-backed Process Sentinel workflow, not the full long-term platform.
```

## Suggested Reasoning Levels

Use lower reasoning for small edits and higher reasoning for architecture-heavy work.

Suggested pattern:

- Low: formatting, simple docs edits, small test fixes
- Medium: single-service implementation, small UI work
- High: architecture, data contracts, debugging, cross-service changes
- Extra High: large refactors, planning, multi-service workflows, risk-heavy decisions

## What To Build First

Build in this order:

1. Repository skeleton
2. Local development environment
3. Shared factory event schemas
4. Synthetic factory simulator
5. Ingestion worker
6. API service
7. Process Sentinel drift rules
8. Evidence timeline
9. Governed recommendation queue
10. Web UI
11. RCA/CAPA draft export
12. Tests and documentation hardening

## What Not To Build First

Avoid these until the MVP works:

- Real plant connectors
- Direct industrial writeback
- Complex agent frameworks
- Multi-tenant auth
- Advanced scheduling
- Enterprise RBAC
- Plugin marketplace
- Production deployment automation
- Complex ML pipelines

## Learning Loop

After each meaningful Codex task, require an update to `docs/LEARNING_LOG.md`.

The entry should include:

```markdown
## YYYY-MM-DD - <task name>

### What changed

### How it works

### How to run it

### How to test it

### What to learn next
```

## Quality Gate

Before each commit, ask Codex:

```text
Review the current diff against AGENTS.md, CODE_REVIEW.md, docs/ARCHITECTURE.md, and docs/TESTING.md. Identify architecture risks, missing tests, documentation gaps, and any unsafe industrial-action assumptions. Do not modify files until you report the review.
```
