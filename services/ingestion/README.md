# Ingestion Service

Validates simulator events against the shared contracts and persists accepted
events. The MVP includes a JSONL-backed local store for fast development and a
PostgreSQL schema for the durable event store path.

## JSONL Input

The local ingestion path expects one complete factory event JSON object per
line. Simulator output already uses this format:

```bash
make simulate SCENARIO=gradual_drift
```

Each non-empty line is parsed, validated against `packages/factory-events`, and
then routed to either the accepted event store or the dead-letter file.

## Local Command

Run ingestion against simulator output:

```bash
make ingest INPUT=.local/events/gradual_drift.jsonl
```

The equivalent direct command is:

```bash
python -m factory_ingestion.cli \
  --input .local/events/gradual_drift.jsonl \
  --events-store .local/storage/events.jsonl \
  --dead-letter .local/storage/dead_letter.jsonl
```

The command prints a summary such as:

```text
ingestion complete: accepted=56 rejected=0 events_store=.local/storage/events.jsonl dead_letter=.local/storage/dead_letter.jsonl
```

Malformed JSON, unsupported event types, and schema-invalid events are rejected
without stopping the file. Dead-letter rows include the source line number, the
validation error, and the raw input line so contributors can inspect bad input
without losing the rest of the batch.
