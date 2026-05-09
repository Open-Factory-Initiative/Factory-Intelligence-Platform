# Data Contracts

## Purpose

Data contracts define how services exchange factory information.

All service boundaries should use explicit schemas. Do not pass unstructured dictionaries across service boundaries without validation.

## Event Envelope

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
    "work_order_id": "wo_1001"
  },
  "payload": {},
  "metadata": {
    "simulated": true,
    "trace_id": "trace_000001"
  }
}
```

## Event Types

### Process Measurement Recorded

```json
{
  "event_type": "process.measurement.recorded",
  "payload": {
    "signal_id": "fill_weight",
    "signal_name": "Fill Weight",
    "value": 501.2,
    "unit": "g",
    "quality": "good"
  }
}
```

### Quality Measurement Recorded

```json
{
  "event_type": "quality.measurement.recorded",
  "payload": {
    "measurement_name": "Final Fill Weight",
    "value": 501.0,
    "unit": "g",
    "spec_min": 495.0,
    "spec_max": 505.0,
    "result": "pass"
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
- Simulator events must include `metadata.simulated = true`.
- Payloads must be validated.
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
