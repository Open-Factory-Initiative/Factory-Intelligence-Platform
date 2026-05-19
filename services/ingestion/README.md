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

By default, simulator output is written to:

```text
.local/events/gradual_drift.jsonl
```

Each non-empty line is parsed, validated against `packages/factory-events`, and
then routed to either the accepted event store or the dead-letter file.

## Local Simulator-to-Ingestion Workflow

Run the default local flow from the repository root:

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

The first command creates deterministic simulator events. The second command
validates those events, appends accepted records to local storage, and routes
invalid records to dead-letter storage without stopping the full file.

Useful command variants:

```bash
make simulate SCENARIO=normal OUTPUT=.local/events/normal.jsonl
make ingest INPUT=.local/events/normal.jsonl
make ingest INPUT=.local/events/normal.jsonl EVENTS_STORE=.local/storage/normal-events.jsonl
```

For the deterministic manufacturer demo, use the demo-specific command after
generating demo data:

```bash
make demo-data
make demo-ingest
```

Expected demo ingestion output:

```text
ingestion summary
input_file: .local/events/fill_weight_drift_demo.jsonl
accepted_events: 70
rejected_events: 0
dead_letter_count: 0
accepted_output: .local/storage/fill_weight_drift_demo_events.jsonl
dead_letter_output: .local/storage/fill_weight_drift_demo_dead_letter.jsonl
```

The documented scenarios are `normal`, `gradual_drift`, and
`sudden_excursion`. Use `SEED`, `COUNT`, `DURATION_MINUTES`, and `OUTPUT` when
you need reproducible inputs for manual testing.

## Local Files

Default generated and ingested files:

| Purpose | Default path |
| --- | --- |
| Simulator output | `.local/events/<scenario>.jsonl` |
| Accepted event store | `.local/storage/events.jsonl` |
| Dead-letter records | `.local/storage/dead_letter.jsonl` |
| Process Sentinel state | `.local/storage/sentinel/` |

The `.local/` directory is generated developer data and is ignored by Git.

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
.venv/bin/python -m factory_ingestion.cli \
  --input .local/events/gradual_drift.jsonl \
  --events-store .local/storage/events.jsonl \
  --dead-letter .local/storage/dead_letter.jsonl
```

## Accepted Event Storage

Accepted events are written to the local JSONL event store:

```text
.local/storage/events.jsonl
```

This is the path used by `make ingest`, `make sentinel-run`, and the local API
by default. Each line is one validated factory event serialized as JSON, so the
file can be inspected with standard command-line tools and read back through
`JsonlEventStore`.

Inspect the accepted store:

```bash
wc -l .local/storage/events.jsonl
head -n 3 .local/storage/events.jsonl
```

The local store is idempotent by `event_id`: ingesting the same deterministic
simulator output more than once validates the events again but does not append
duplicate accepted-event rows. To reset local accepted-event storage, remove the
file and run ingestion again:

```bash
rm .local/storage/events.jsonl
make ingest INPUT=.local/events/gradual_drift.jsonl
```

The command prints a summary such as:

```text
ingestion summary
input_file: .local/events/gradual_drift.jsonl
accepted_events: 56
rejected_events: 0
dead_letter_count: 0
accepted_output: .local/storage/events.jsonl
dead_letter_output: .local/storage/dead_letter.jsonl
```

Malformed JSON, unsupported event types, and schema-invalid events are rejected
without stopping the file. The default dead-letter output path is predictable:

```text
.local/storage/dead_letter.jsonl
```

Dead-letter rows include the source file, source line number, rejection
timestamp, validation error, structured error details, parsed original payload
when JSON parsing succeeds, and the raw input line so contributors can inspect
bad input without losing the rest of the batch.

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
  "source_path": ".local/events/gradual_drift.jsonl",
  "recorded_at": "2026-05-19T01:23:45.678901+00:00",
  "error": "event failed shared factory event schema validation",
  "errors": [
    {
      "path": "quality",
      "message": "Input should be 'good', 'uncertain' or 'bad'",
      "type": "literal_error",
      "input": "offline"
    }
  ],
  "payload": {
    "event_id": "..."
  },
  "raw": "{\"event_id\": \"...\"}"
}
```

Malformed JSON rows cannot include a parsed `payload`, so those dead-letter
records keep `payload` as `null` and preserve the original text in `raw`.

When ingestion rejects records, the summary includes a few validation examples
from the dead-letter file:

```text
ingestion summary
input_file: .local/events/gradual_drift.jsonl
accepted_events: 55
rejected_events: 1
dead_letter_count: 1
accepted_output: .local/storage/events.jsonl
dead_letter_output: .local/storage/dead_letter.jsonl
validation_error_examples:
- line 12: quality: Input should be 'good', 'uncertain' or 'bad'
```

Inspect dead-letter output:

```bash
wc -l .local/storage/dead_letter.jsonl
head -n 3 .local/storage/dead_letter.jsonl
```

## Reset Local Generated Data

To reset only the ingestion outputs and keep simulator input files:

```bash
rm -f .local/storage/events.jsonl .local/storage/dead_letter.jsonl
rm -rf .local/storage/sentinel
```

To reset the full local MVP generated data set:

```bash
rm -rf .local/events .local/storage
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

## Troubleshooting

If `make ingest` cannot find the input file, generate simulator output first or
pass the exact input path:

```bash
make simulate SCENARIO=gradual_drift
make ingest INPUT=.local/events/gradual_drift.jsonl
```

If `make ingest` fails because `.venv/bin/python` is missing, install the local
development environment:

```bash
make setup
```

If accepted counts look lower than expected after re-running the same scenario,
the local store is likely skipping duplicate `event_id` values. Reset
`.local/storage/events.jsonl` or write to a new `EVENTS_STORE` path for a clean
manual run.

If ingestion fails while reading `.local/storage/events.jsonl`, the local store
may contain stale or hand-edited generated data that no longer matches the
shared event contracts. Reset local generated storage, then re-run simulator and
ingestion.

If rejected counts are non-zero, inspect `.local/storage/dead_letter.jsonl` and
the `validation_error_examples` section in the ingestion summary. Common causes
are malformed JSON, missing required event fields, unsupported `event_type`
values, invalid enum values, invalid process or quality ranges, and mismatched
quality result fields.

## Demo Ingestion Troubleshooting

For the manufacturer demo, use the demo-specific local paths instead of the
generic defaults:

| Purpose | Demo path |
| --- | --- |
| Simulator output | `.local/events/fill_weight_drift_demo.jsonl` |
| Accepted event store | `.local/storage/fill_weight_drift_demo_events.jsonl` |
| Dead-letter records | `.local/storage/fill_weight_drift_demo_dead_letter.jsonl` |
| Process Sentinel state | `.local/storage/fill_weight_drift_demo_sentinel/` |

If no detections appear after ingestion, run the clean demo sequence:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
```

The expected deterministic demo counts are 70 generated events, 70 accepted
events, 0 rejected events, and 0 dead-letter rows. See
`docs/DEMO_RUNBOOK.md` for the full troubleshooting checklist.
