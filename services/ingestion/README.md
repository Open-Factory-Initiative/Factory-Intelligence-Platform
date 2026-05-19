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

## Validation Behavior

Ingestion validates incoming records through the shared factory event schemas
before accepted events reach storage. Validation covers:

- Base event envelope fields such as `event_id`, `event_type`,
  `schema_version`, `timestamp`, `source`, `context`, `payload`, and
  `metadata`
- Supported event types such as process measurements, quality measurements,
  batch events, and work order events
- Payload-specific rules such as process normal ranges, quality specification
  ranges, result compatibility, and batch/work-order context consistency

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

Common validation errors include:

- Missing required base fields, such as `event_id` or `timestamp`
- Unsupported `event_type` values
- Invalid enum values, such as an unknown process `quality`
- Invalid ranges, such as `normal_min` greater than `normal_max`
- Mismatched quality `result` and `result_status` values

Dead-letter records also include an `errors` list with structured validation
details:

```json
{
  "line_number": 3,
  "error": "event failed shared factory event schema validation",
  "errors": [
    {
      "path": "quality",
      "message": "Input should be 'good', 'uncertain' or 'bad'",
      "type": "literal_error",
      "input": "offline"
    }
  ],
  "raw": "{\"event_id\": \"...\"}"
}
```
