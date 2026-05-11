# API Design

## Purpose

The API provides a stable interface for the web UI and future integrations.

## API Principles

- Contract-first where practical
- Clear resource naming
- Explicit error responses
- Stable IDs
- Traceable audit behavior
- OpenAPI documentation
- No hidden demo state

## Initial Endpoint Groups

### Health

```text
GET /health
```

### Events

```text
POST /events
GET /events
GET /events/{event_id}
```

`POST /events` is part of the target API design. The current skeleton exposes
read-only event queries over local JSONL storage.

### Domain Context

```text
GET /sites
GET /sites/{site_id}
GET /areas
GET /areas/{area_id}
GET /equipment
GET /equipment/{equipment_id}
GET /process-signals
GET /process-signals/{signal_id}
GET /batches
GET /batches/{batch_id}
GET /quality-results
GET /quality-results/{quality_result_id}
GET /deviations
GET /deviations/{deviation_id}
GET /alerts
GET /alerts/{alert_id}
GET /investigations
GET /investigations/{investigation_id}
```

The current domain endpoints are read-only and return simulator/demo context for
the first Process Sentinel MVP. Investigation detail responses include linked
deviation, alert, quality result, and process signal records.

### Process Sentinel

```text
GET /sentinel/detections
GET /sentinel/detections/{detection_id}
GET /sentinel/detections/{detection_id}/evidence
```

### Recommendations

```text
GET /recommendations
GET /recommendations/{recommendation_id}
POST /recommendations/{recommendation_id}/approve
POST /recommendations/{recommendation_id}/reject
POST /recommendations/{recommendation_id}/defer
```

### Reports

```text
GET /reports/rca-capa-drafts/{detection_id}
```

## Error Format

Use consistent error responses:

```json
{
  "error": {
    "code": "invalid_event",
    "message": "Event payload failed validation.",
    "details": {}
  }
}
```

## API Testing

Every endpoint should have tests for:

- Successful response
- Invalid input
- Missing resource
- Unauthorized access once auth exists
- Contract shape
