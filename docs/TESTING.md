# Testing Strategy

## Purpose

Testing is a core part of the Factory Intelligence Platform. Codex should not add features without tests.

## Test Pyramid

```text
Many unit tests
Some integration tests
Some contract tests
Fewer end-to-end tests
```

## Test Categories

### Unit Tests

Use unit tests for:

- Drift detection rules
- Event validation
- Recommendation logic
- Evidence scoring
- Report generation
- Utility functions

### Integration Tests

Use integration tests for:

- Ingestion → validation → storage
- API → database
- Detection service → event store
- Recommendation service → approval service

### Contract Tests

Use contract tests for:

- Factory event schemas
- API request/response models
- Event topic naming
- Backward compatibility

### End-to-End Tests

Use Playwright for user workflows:

1. Start local stack.
2. Generate drift scenario.
3. Open web UI.
4. See detection.
5. Open evidence timeline.
6. Review recommendation.
7. Approve/reject recommendation.
8. View RCA/CAPA draft.
9. Confirm audit state.

## MVP Test Commands

Current commands:

```bash
make test
make test-unit
make test-integration
make test-contract
make test-e2e
make demo-api-smoke
make lint
make typecheck
```

`make test-e2e` runs the local Operations Workbench Playwright smoke test. The
test starts the FastAPI demo API and Next.js Workbench, prepares deterministic
demo state with `make demo`, and walks the manufacturer demo path in a browser:
overview, detections, detection detail, evidence timeline, recommendation
review, approve/reject/defer decision feedback, and RCA/CAPA draft preview.

The Playwright smoke test is local-only for now. CI integration is intentionally
tracked separately in #165 so this issue can keep the first browser workflow
reliable before hardening it for GitHub Actions.

`make demo-api-smoke` is a backend-only smoke test for the deterministic demo
path. Run it after:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make demo-api-smoke
```

It verifies the generated demo event store, detection endpoint, evidence
endpoint, recommendation endpoint, decision endpoint, and RCA/CAPA draft
endpoint without requiring the browser UI.

## Backend Testing

Current tools:

- `pytest`
- `httpx`
- `ruff`
- `compileall` for the initial syntax/type-import gate

Current expectations:

```bash
make test
make lint
make typecheck
```

## Frontend Testing

Recommended tools:

- `vitest`
- `@testing-library/react`
- `playwright`
- `eslint`
- `tsc --noEmit`

Example expectations:

```bash
cd apps/web
npm test
npm run lint
npm run typecheck
npx playwright test
```

Before the first Playwright run on a new machine, install the browser runtime:

```bash
cd apps/web
npx playwright install chromium
```

Then run either:

```bash
make test-e2e
```

or:

```bash
cd apps/web
npm run test:e2e
```

If the demo state cannot be prepared, the smoke test fails with the captured
`make demo` output so the missing simulator, ingestion, Sentinel, or API step is
visible in the failure log.

## Simulator Testing

The simulator must be deterministic for tests.

Requirements:

- Seeded random generation
- Scenario fixtures
- Known expected drift windows
- Known expected quality outcomes
- Fast local execution

## Drift Detection Tests

Every drift rule should test:

- Normal case
- Drift case
- Missing data
- Noisy data
- Boundary condition
- False positive prevention

## Contract Test Fixtures

Maintain fixtures under:

```text
packages/test-fixtures/
```

Suggested fixture groups:

```text
valid-events/
invalid-events/
drift-scenarios/
api-responses/
```

## CI Expectations

The initial CI can be simple:

- Validate docs links or markdown formatting if configured
- Run backend tests if backend exists
- Run frontend tests if frontend exists
- Run e2e tests once app stack exists

Do not block early documentation work on missing app code. CI can evolve with the repo.
