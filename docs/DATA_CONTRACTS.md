# Data Contracts

## Purpose

Data contracts define how services exchange factory information.

All service boundaries should use explicit schemas. Do not pass unstructured dictionaries across service boundaries without validation.

## Current Implementation

The MVP skeleton implements the first contracts in:

```text
packages/factory-events/factory_events/models.py
```

The base event model is `FactoryEvent`. `EventEnvelope` remains available as a
backward-compatible name for existing simulator, ingestion, and API code.

Contract fixtures live in:

```text
packages/test-fixtures/valid-events/
packages/test-fixtures/invalid-events/
packages/test-fixtures/drift-scenarios/
```

Contributor-facing example payloads live in:

```text
examples/events/
```

Run contract tests with:

```bash
make test-contract
```

The implementation currently validates the common envelope, event identity,
UTC timestamps, schema version `1.0.0`, source system metadata, line and asset
context, optional batch and work order references, process signal payloads,
quality event payloads, asset status payloads, production batch and work order
payloads, governed recommendation payloads, supported event types, and payload
shape. Unknown event types are rejected by ingestion.

## Base FactoryEvent Envelope

Every platform event should use a common envelope.

```json
{
  "event_id": "evt_000001",
  "event_type": "process.measurement.recorded",
  "schema_version": "1.0.0",
  "timestamp": "2026-01-01T12:00:00Z",
  "source": {
    "system": "factory-simulator",
    "adapter": "simulator",
    "source_event_id": "sim-000001"
  },
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "asset_id": "asset_filler_1",
    "batch_id": "batch_demo_1001",
    "work_order_id": "wo_1001"
  },
  "payload": {
    "signal_id": "fill_weight",
    "signal_name": "Fill Weight",
    "tag_name": "asset_filler_1.fill_weight",
    "value": 501.2,
    "unit": "g",
    "quality": "good",
    "normal_min": 495.0,
    "normal_max": 505.0,
    "target_value": 500.0
  },
  "metadata": {
    "simulated": true,
    "trace_id": "trace_000001"
  }
}
```

The checked-in example lives at:

```text
examples/events/base_factory_event.json
packages/test-fixtures/valid-events/base_factory_event.json
```

### Envelope Fields

- `event_id`: stable event identity.
- `event_type`: constrained to the currently supported MVP event types.
- `schema_version`: currently `1.0.0`.
- `timestamp`: timezone-aware UTC timestamp.
- `source.system`: source system name, such as `factory-simulator`.
- `source.adapter`: adapter that produced the event, such as `simulator`.
- `source.source_event_id`: original source-side event identity.
- `context.site_id`, `context.area_id`, `context.line_id`: required location and line context.
- `context.asset_id`: optional equipment or asset context.
- `context.batch_id`: optional batch reference.
- `context.work_order_id`: optional work order reference.
- `payload`: event-type-specific payload validated by the shared contract package.
- `metadata.simulated`: marks simulator/demo events.
- `metadata.trace_id`: trace identity for correlating processing and evidence.

## Event Types

Supported MVP event types are:

- `process.measurement.recorded`
- `quality.measurement.recorded`
- `asset.status.updated`
- `production.batch.started`
- `production.batch.completed`
- `production.batch.status.updated`
- `production.work_order.started`
- `production.work_order.completed`
- `production.work_order.status.updated`
- `sentinel.detection.created`
- `governance.recommendation.proposed`
- `governance.approval.recorded`
- `governance.audit.recorded`

### Process Measurement Recorded

```json
{
  "event_type": "process.measurement.recorded",
  "payload": {
    "signal_id": "fill_weight",
    "signal_name": "Fill Weight",
    "tag_name": "asset_filler_1.fill_weight",
    "value": 501.2,
    "unit": "g",
    "quality": "good",
    "normal_min": 495.0,
    "normal_max": 505.0,
    "target_value": 500.0
  }
}
```

`ProcessSignalEvent` is the typed envelope specialization for
`process.measurement.recorded`. It uses the same `FactoryEvent` envelope and
adds a process-signal payload for simulated or real tag values.

Additional process signal examples live at:

```text
examples/events/process_signal_event.json
packages/test-fixtures/valid-events/process_temperature_signal.json
packages/test-fixtures/valid-events/process_pressure_signal.json
```

### Quality Measurement Recorded

```json
{
  "event_type": "quality.measurement.recorded",
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "asset_id": "asset_checkweigher_1",
    "batch_id": "batch_demo_1001",
    "work_order_id": "wo_1001"
  },
  "payload": {
    "quality_check_type": "inline_check",
    "measurement_name": "Final Fill Weight",
    "value": 501.0,
    "unit": "g",
    "result_status": "pass",
    "result": "pass",
    "severity": "low",
    "spec_min": 495.0,
    "spec_max": 505.0
  }
}
```

`QualityEvent` is the typed envelope specialization for
`quality.measurement.recorded`. It uses the same `FactoryEvent` envelope and
represents quality observations such as inline checks, inspections, lab results,
deviations, defects, and outcome markers. Affected batch and work order
references are carried in the shared event context.

Additional quality examples live at:

```text
examples/events/quality_event.json
packages/test-fixtures/valid-events/quality_in_spec_result.json
packages/test-fixtures/valid-events/quality_out_of_spec_result.json
packages/test-fixtures/valid-events/quality_visual_inspection.json
```

### Asset Status Updated

Contributor-facing asset example:

```text
examples/events/asset_event.json
```

```json
{
  "event_type": "asset.status.updated",
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "asset_id": "asset_filler_1"
  },
  "payload": {
    "asset_id": "asset_filler_1",
    "asset_name": "Filler 1",
    "asset_type": "filler",
    "previous_status": "idle",
    "status": "running",
    "status_reason": "Line startup completed."
  }
}
```

`AssetEvent` is the typed envelope specialization for
`asset.status.updated`. It records equipment state changes that provide context
for process signals, investigations, and future maintenance workflows. If
`context.asset_id` is present, it must match `payload.asset_id`.

### Batch Started

Contributor-facing batch example:

```text
examples/events/batch_event.json
```

```json
{
  "event_type": "production.batch.started",
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "batch_id": "batch_demo_1001",
    "work_order_id": "wo_1001"
  },
  "payload": {
    "batch_id": "batch_demo_1001",
    "lot_id": "lot_demo_20260101",
    "product_id": "prod_demo_tablets",
    "product_name": "Demo Tablets",
    "material_id": "mat_demo_blend",
    "material_name": "Demo Blend",
    "work_order_id": "wo_1001",
    "previous_status": "planned",
    "status": "started",
    "status_reason": "Batch released to packaging line."
  }
}
```

### Batch Completed

```json
{
  "event_type": "production.batch.completed",
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "batch_id": "batch_demo_1001",
    "work_order_id": "wo_1001"
  },
  "payload": {
    "batch_id": "batch_demo_1001",
    "lot_id": "lot_demo_20260101",
    "product_id": "prod_demo_tablets",
    "product_name": "Demo Tablets",
    "material_id": "mat_demo_blend",
    "material_name": "Demo Blend",
    "work_order_id": "wo_1001",
    "previous_status": "started",
    "status": "completed",
    "status_reason": "Batch production finished."
  }
}
```

### Work Order Started

Contributor-facing work order example:

```text
examples/events/work_order_event.json
```

```json
{
  "event_type": "production.work_order.started",
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "work_order_id": "wo_1001"
  },
  "payload": {
    "work_order_id": "wo_1001",
    "product_id": "prod_demo_tablets",
    "product_name": "Demo Tablets",
    "material_id": "mat_demo_blend",
    "material_name": "Demo Blend",
    "batch_id": "batch_demo_1001",
    "lot_id": "lot_demo_20260101",
    "previous_status": "planned",
    "status": "started",
    "status_reason": "Line is ready and materials are staged."
  }
}
```

### Work Order Completed

```json
{
  "event_type": "production.work_order.completed",
  "context": {
    "site_id": "site_demo",
    "area_id": "area_packaging",
    "line_id": "line_1",
    "work_order_id": "wo_1001"
  },
  "payload": {
    "work_order_id": "wo_1001",
    "product_id": "prod_demo_tablets",
    "product_name": "Demo Tablets",
    "material_id": "mat_demo_blend",
    "material_name": "Demo Blend",
    "batch_id": "batch_demo_1001",
    "lot_id": "lot_demo_20260101",
    "previous_status": "started",
    "status": "completed",
    "status_reason": "Planned production quantity completed."
  }
}
```

### Drift Detection Created

```json
{
  "event_type": "sentinel.detection.created",
  "payload": {
    "detection_id": "det_000001",
    "detection_type": "quality_drift",
    "severity": "medium",
    "summary": "Fill weight trending upward",
    "confidence": 0.82,
    "time_window_start": "2026-01-01T11:30:00Z",
    "time_window_end": "2026-01-01T12:00:00Z"
  }
}
```

### Recommendation Proposed

Contributor-facing recommendation example:

```text
examples/events/recommendation_event.json
```

```json
{
  "event_type": "governance.recommendation.proposed",
  "payload": {
    "recommendation_id": "rec_000001",
    "detection_id": "det_000001",
    "recommended_action": "Inspect filler calibration and hold affected work order for quality review.",
    "risk_level": "medium",
    "requires_approval": true,
    "evidence_ids": ["evi_000001", "evi_000002"]
  }
}
```

`RecommendationEvent` is the typed envelope specialization for
`governance.recommendation.proposed`. Recommendations remain advisory and
human-reviewed; high-impact action still requires the governed approval flow.

### Approval Decision Recorded

```json
{
  "event_type": "governance.approval.recorded",
  "payload": {
    "approval_id": "apr_000001",
    "recommendation_id": "rec_000001",
    "decision": "approved",
    "reviewer": "quality_engineer",
    "reason": "Evidence supports containment."
  }
}
```

## Schema Rules

- Every event must have `event_id`.
- Every event must have `event_type`.
- Every event must have `schema_version`.
- Every event must have an ISO-8601 UTC timestamp.
- Every event must include `source`.
- Every event must include required line context.
- `batch_id` and `work_order_id` are optional context references.
- Simulator events must include `metadata.simulated = true`.
- Payloads must be validated.
- Process signal payloads must include `signal_id`, `signal_name`, `tag_name`,
  numeric `value`, engineering `unit`, and constrained signal `quality`.
- Process signal payloads may include `normal_min`, `normal_max`, and
  `target_value`. If one normal range bound is provided, both bounds are
  required, and `normal_min` must be less than `normal_max`.
- Quality event payloads must include `quality_check_type`, `measurement_name`,
  numeric `value`, engineering `unit`, constrained `result_status`, and
  constrained `severity`.
- Quality event payloads may include `spec_min` and `spec_max`. If one
  specification bound is provided, both bounds are required, and `spec_min`
  must be less than `spec_max`.
- Quality event batch and work order references should use
  `context.batch_id` and `context.work_order_id`.
- Asset status payloads must include `asset_id`, `asset_name`, `asset_type`,
  and constrained asset `status`.
- If `context.asset_id` is present for an asset event, it must match
  `payload.asset_id`.
- Batch event payloads must include `batch_id`, `lot_id`, `product_id`,
  `product_name`, and a constrained batch `status`.
- Work order event payloads must include `work_order_id`, `product_id`,
  `product_name`, and a constrained work order `status`.
- Recommendation payloads must include `recommendation_id`, `detection_id`,
  `recommended_action`, constrained `risk_level`, `requires_approval`, and at
  least one `evidence_ids` entry.
- Batch and work order lifecycle event names must match their payload status:
  started events use `status = "started"` and completed events use
  `status = "completed"`.
- If `context.batch_id` or `context.work_order_id` is also present in a
  production context event, it must match the corresponding payload identifier.
- Unknown event types must be rejected or sent to a dead-letter path.
- Schema changes require tests and documentation updates.

## Versioning

Use semantic-style schema versions:

- Patch: backwards-compatible clarification
- Minor: backwards-compatible field addition
- Major: breaking field change or removal

## Contract Testing

Every schema should include:

- Valid fixture
- Invalid fixture
- Missing required fields test
- Type validation test
- Version compatibility test

## OpenAPI

API contracts should be generated from backend models where possible.

API docs should include:

- Endpoint path
- Method
- Request body
- Response body
- Error cases
- Authentication assumptions
- Example request/response
