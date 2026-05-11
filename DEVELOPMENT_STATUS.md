# Development Status

Last reviewed: 2026-05-11

## What Currently Works

- Python development setup through `make setup`.
- Deterministic simulator scenarios through `make simulate`.
- JSONL ingestion, validation, and dead-letter handling through `make ingest`.
- Process Sentinel drift detection, evidence, and recommendation generation through `make sentinel-run`.
- FastAPI local API startup through `make api`, with auto-reload available through `make api-reload`.
- PostgreSQL Docker Compose configuration through `make dev-db`.
- Backend checks through `make lint`, `make typecheck`, and `make test`.

## What Is Incomplete

- `apps/web` is a placeholder; the Next.js workbench has not been implemented.
- `make test-e2e` is a documented placeholder until the web workbench exists.
- PostgreSQL is configured, but the default local MVP flow still uses JSONL storage.
- Real MQTT, OPC UA, MES, QMS, CMMS, and ERP connectors are out of scope for the current skeleton.
- Authentication, multi-tenant behavior, production deployment, and real industrial writeback are not implemented.

## How To Run The Current Skeleton

```bash
make setup
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
make sentinel-run
make api
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Optional local PostgreSQL:

```bash
make dev-db
```

## Verified Commands

```bash
make lint
make typecheck
make test
make test-unit
make test-integration
make test-contract
make test-e2e
make dev-db
docker compose -f infra/docker/docker-compose.yml config
docker compose -f infra/docker/docker-compose.yml ps
```

`make test-e2e` should print the placeholder message until the web workbench is implemented.
`make dev-db` should start a healthy PostgreSQL container on local port `5432`.

## Recommended Next Steps

1. Harden shared event contracts with additional fixtures for recommendation, approval, and audit events.
2. Add the first minimal web workbench screen over the existing API state.
3. Replace the placeholder e2e command with a Playwright test once the workbench exists.
4. Decide when JSONL development storage should give way to the PostgreSQL-backed path for integration tests.
