VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
SYSTEM_PYTHON ?= python3
SCENARIO ?= gradual_drift
SEED ?= 42
COUNT ?= 24
DURATION_MINUTES ?=
OUTPUT ?= .local/events/$(SCENARIO).jsonl
INPUT ?= $(OUTPUT)
EVENTS_STORE ?= .local/storage/events.jsonl
SENTINEL_STATE_DIR ?= .local/storage/sentinel
DEMO_SCENARIO ?= fill_weight_drift_demo
DEMO_SEED ?= 120
DEMO_COUNT ?= 30
DEMO_EVENTS_DIR ?= .local/events
DEMO_STORAGE_DIR ?= .local/storage
DEMO_OUTPUT ?= $(DEMO_EVENTS_DIR)/$(DEMO_SCENARIO).jsonl
DEMO_EVENTS_STORE ?= $(DEMO_STORAGE_DIR)/$(DEMO_SCENARIO)_events.jsonl
DEMO_DEAD_LETTER ?= $(DEMO_STORAGE_DIR)/$(DEMO_SCENARIO)_dead_letter.jsonl
DEMO_SENTINEL_STATE_DIR ?= $(DEMO_STORAGE_DIR)/$(DEMO_SCENARIO)_sentinel
PYTHONPATH := packages/factory-events:services/simulator:services/ingestion:services/process-sentinel:services/api
export PYTHONPATH

.PHONY: help setup dev dev-db simulate ingest sentinel-run demo demo-reset demo-data demo-ingest demo-sentinel-run demo-api-smoke api api-reload test test-unit test-integration test-contract test-e2e lint typecheck docs

help:
	@echo "Factory Intelligence Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup              Install Python development dependencies"
	@echo "  make dev-db             Start local PostgreSQL with Docker Compose"
	@echo "  make simulate           Generate simulator JSONL events"
	@echo "  make ingest             Validate and ingest simulator events"
	@echo "  make sentinel-run       Run Process Sentinel over ingested events"
	@echo "  make demo               Prepare and verify deterministic demo state"
	@echo "  make demo-reset         Clear generated local demo files"
	@echo "  make demo-data          Generate deterministic manufacturer demo data"
	@echo "  make demo-ingest        Ingest deterministic manufacturer demo data"
	@echo "  make demo-sentinel-run  Run Process Sentinel over demo data"
	@echo "  make demo-api-smoke     Smoke test demo data through the API app"
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
	$(PYTHON) -m factory_simulator.cli --scenario $(SCENARIO) --seed $(SEED) $(if $(DURATION_MINUTES),--duration-minutes $(DURATION_MINUTES),--count $(COUNT)) --output $(OUTPUT)

ingest:
	$(PYTHON) -m factory_ingestion.cli --input $(INPUT) --events-store $(EVENTS_STORE)

sentinel-run:
	$(PYTHON) -m process_sentinel.cli --events-store $(EVENTS_STORE) --state-dir $(SENTINEL_STATE_DIR)

demo: demo-reset demo-data demo-ingest demo-sentinel-run demo-api-smoke
	@echo ""
	@echo "Demo state is ready."
	@echo "Expected detection ID: det_fill_weight_gradual_drift"
	@echo "Expected recommendation ID: rec_fill_weight_gradual_drift"
	@echo ""
	@echo "Start the API in one terminal:"
	@echo "  make api EVENTS_STORE=$(DEMO_EVENTS_STORE) SENTINEL_STATE_DIR=$(DEMO_SENTINEL_STATE_DIR)"
	@echo ""
	@echo "Start the Operations Workbench in another terminal:"
	@echo "  cd apps/web && npm run dev"
	@echo ""
	@echo "Expected API URLs:"
	@echo "  http://127.0.0.1:8000/docs"
	@echo "  http://127.0.0.1:8000/sentinel/detections"
	@echo "  http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift"
	@echo "  http://127.0.0.1:8000/sentinel/detections/det_fill_weight_gradual_drift/evidence"
	@echo "  http://127.0.0.1:8000/recommendations"
	@echo "  http://127.0.0.1:8000/reports/rca-capa-drafts/det_fill_weight_gradual_drift"
	@echo ""
	@echo "Expected Workbench URLs:"
	@echo "  http://127.0.0.1:3000"
	@echo "  http://127.0.0.1:3000/detections/det_fill_weight_gradual_drift"
	@echo "  http://127.0.0.1:3000/recommendations?detection_id=det_fill_weight_gradual_drift"
	@echo "  http://127.0.0.1:3000/rca-capa-draft?detection_id=det_fill_weight_gradual_drift"
	@echo ""
	@echo "All generated demo files are under .local/ and are ignored by Git."

demo-reset:
	rm -f $(DEMO_OUTPUT) $(DEMO_EVENTS_STORE) $(DEMO_DEAD_LETTER)
	rm -rf $(DEMO_SENTINEL_STATE_DIR)
	@echo "Demo generated state cleared."
	@echo "Next: make demo-data"

demo-data:
	$(PYTHON) -m factory_simulator.cli --scenario $(DEMO_SCENARIO) --seed $(DEMO_SEED) --count $(DEMO_COUNT) --output $(DEMO_OUTPUT)
	@echo "Demo data ready: $(DEMO_OUTPUT)"
	@echo "Next: make demo-ingest"

demo-ingest:
	$(PYTHON) -m factory_ingestion.cli --input $(DEMO_OUTPUT) --events-store $(DEMO_EVENTS_STORE) --dead-letter $(DEMO_DEAD_LETTER)
	@echo "Demo events stored: $(DEMO_EVENTS_STORE)"
	@echo "Next: make demo-sentinel-run"

demo-sentinel-run:
	$(PYTHON) -m process_sentinel.cli --events-store $(DEMO_EVENTS_STORE) --state-dir $(DEMO_SENTINEL_STATE_DIR)
	@echo "Demo Sentinel state: $(DEMO_SENTINEL_STATE_DIR)"
	@echo "Next: make api EVENTS_STORE=$(DEMO_EVENTS_STORE) SENTINEL_STATE_DIR=$(DEMO_SENTINEL_STATE_DIR)"

demo-api-smoke:
	$(PYTHON) -m factory_api.demo_smoke --events-store $(DEMO_EVENTS_STORE) --sentinel-state-dir $(DEMO_SENTINEL_STATE_DIR)

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
