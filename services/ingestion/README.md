# Ingestion Service

Validates simulator events against the shared contracts and persists accepted
events. The MVP includes a JSONL-backed local store for fast development and a
PostgreSQL schema for the durable event store path.

Example:

```bash
python -m factory_ingestion.cli --input .local/events/gradual_drift.jsonl
```

