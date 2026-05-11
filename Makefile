VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
SYSTEM_PYTHON ?= python3
SCENARIO ?= gradual_drift
OUTPUT ?= .local/events/$(SCENARIO).jsonl
INPUT ?= $(OUTPUT)
EVENTS_STORE ?= .local/storage/events.jsonl
SENTINEL_STATE_DIR ?= .local/storage/sentinel
PYTHONPATH := packages/factory-events:services/simulator:services/ingestion:services/process-sentinel:services/api
export PYTHONPATH

.PHONY: help setup dev dev-db simulate ingest sentinel-run api api-reload test test-unit test-integration test-contract test-e2e lint typecheck docs

help:
	@echo "Factory Intelligence Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup              Install Python development dependencies"
	@echo "  make dev-db             Start local PostgreSQL with Docker Compose"
	@echo "  make simulate           Generate simulator JSONL events"
	@echo "  make ingest             Validate and ingest simulator events"
	@echo "  make sentinel-run       Run Process Sentinel over ingested events"
	@echo "  make api                Start FastAPI API"
	@echo "  make api-reload         Start FastAPI API with auto-reload"
	@echo "  make test               Run all configured tests"
	@echo "  make test-unit          Run unit tests"
	@echo "  make test-integration   Run integration tests"
	@echo "  make test-contract      Run contract tests"
	@echo "  make test-e2e           Run end-to-end tests"
	@echo "  make lint               Run lint checks"
	@echo "  make typecheck          Run type checks"
	@echo "  make docs               Validate or serve docs"

setup:
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

dev:
	@echo "Run these in separate terminals for the MVP skeleton:"
	@echo "  make dev-db"
	@echo "  make simulate SCENARIO=gradual_drift"
	@echo "  make ingest INPUT=.local/events/gradual_drift.jsonl"
	@echo "  make sentinel-run"
	@echo "  make api"

dev-db:
	docker compose -f infra/docker/docker-compose.yml up -d

simulate:
	$(PYTHON) -m factory_simulator.cli --scenario $(SCENARIO) --output $(OUTPUT)

ingest:
	$(PYTHON) -m factory_ingestion.cli --input $(INPUT) --events-store $(EVENTS_STORE)

sentinel-run:
	$(PYTHON) -m process_sentinel.cli --events-store $(EVENTS_STORE) --state-dir $(SENTINEL_STATE_DIR)

api:
	FACTORY_EVENTS_STORE=$(EVENTS_STORE) SENTINEL_STATE_DIR=$(SENTINEL_STATE_DIR) $(VENV)/bin/uvicorn factory_api.main:app --app-dir services/api

api-reload:
	FACTORY_EVENTS_STORE=$(EVENTS_STORE) SENTINEL_STATE_DIR=$(SENTINEL_STATE_DIR) $(VENV)/bin/uvicorn factory_api.main:app --reload --app-dir services/api

test:
	$(PYTHON) -m pytest

test-unit:
	$(PYTHON) -m pytest packages/factory-events/tests services/simulator/tests services/process-sentinel/tests

test-integration:
	$(PYTHON) -m pytest services/ingestion/tests services/api/tests

test-contract:
	$(PYTHON) -m pytest packages/factory-events/tests

test-e2e:
	@echo "E2E tests are deferred until apps/web is implemented."

lint:
	$(PYTHON) -m ruff check packages services

typecheck:
	$(PYTHON) -m compileall packages services

docs:
	@echo "Docs are Markdown-only in the MVP skeleton; no docs checker is configured yet."
