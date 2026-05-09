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

### Assets

```text
GET /assets
GET /assets/{asset_id}
```

### Work Orders

```text
GET /work-orders
GET /work-orders/{work_order_id}
```

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
