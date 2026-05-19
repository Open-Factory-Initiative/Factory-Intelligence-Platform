# Evidence Timeline API/UI Contract

## Purpose

This contract defines the evidence timeline shape the Operations Workbench can
expect for the simulator-backed Process Sentinel demo. It covers the MVP API
response only; it does not define charting, generated clients, advanced
analytics, or Factory Memory retrieval.

## Endpoint

```text
GET /sentinel/detections/{detection_id}/evidence
```

Demo detection:

```text
GET /sentinel/detections/det_fill_weight_gradual_drift/evidence
```

## Response Shape

The endpoint returns an array of evidence items. Items are ordered
chronologically by `timestamp`.

| Field | Type | UI use |
| --- | --- | --- |
| `evidence_id` | string | Stable key for list rendering and detail actions. |
| `detection_id` | string | Confirms the evidence belongs to the selected detection. |
| `evidence_type` | string | Badge/filter value such as `process_signal` or `quality_result`. |
| `timestamp` | ISO 8601 string | Timeline ordering and display time. |
| `title` | string | Primary evidence row/card heading. |
| `description` | string | Human-readable explanation for the evidence item. |
| `source_event_ids` | string array | Links to source events when event drilldown is available. |
| `score` | number from 0 to 1 | Relevance/confidence indicator when available. |

## Demo Example Response

```json
[
  {
    "evidence_id": "evi_fill_weight_baseline_vs_recent",
    "detection_id": "det_fill_weight_gradual_drift",
    "evidence_type": "process_signal",
    "timestamp": "2026-01-01T12:29:00Z",
    "title": "Recent fill weight average is higher than baseline",
    "description": "Baseline average was 500.07 g; recent average was 506.37 g, a 6.30 g increase.",
    "source_event_ids": [
      "evt_fill_weight_drift_demo_fill_0000",
      "evt_fill_weight_drift_demo_fill_0001",
      "evt_fill_weight_drift_demo_fill_0002",
      "evt_fill_weight_drift_demo_fill_0003",
      "evt_fill_weight_drift_demo_fill_0004",
      "evt_fill_weight_drift_demo_fill_0005",
      "evt_fill_weight_drift_demo_fill_0024",
      "evt_fill_weight_drift_demo_fill_0025",
      "evt_fill_weight_drift_demo_fill_0026",
      "evt_fill_weight_drift_demo_fill_0027",
      "evt_fill_weight_drift_demo_fill_0028",
      "evt_fill_weight_drift_demo_fill_0029"
    ],
    "score": 0.95
  },
  {
    "evidence_id": "evi_quality_results_recent_window",
    "detection_id": "det_fill_weight_gradual_drift",
    "evidence_type": "quality_result",
    "timestamp": "2026-01-01T12:29:20Z",
    "title": "Recent quality checks are near the upper spec limit",
    "description": "Recent final fill weight checks show the same upward direction as the process signal.",
    "source_event_ids": [
      "evt_fill_weight_drift_demo_quality_0026",
      "evt_fill_weight_drift_demo_quality_0029"
    ],
    "score": 0.72
  }
]
```

## Empty State

When the detection exists but has no evidence, the API returns an empty array:

```json
[]
```

Workbench behavior:

- Show the selected detection header.
- Render an empty evidence state such as `No evidence is available for this
  detection yet.`
- Do not hide the detection or show a system error.

## Error State

When the detection does not exist, the API returns `404`:

```json
{
  "error": {
    "code": "detection_not_found",
    "message": "Detection not found: det_missing"
  }
}
```

Workbench behavior:

- Show a not-found or stale-state message.
- Offer a way to return to the detection list.
- Do not treat this as an industrial action or recommendation decision.

## Current Backend Status

The current FastAPI backend returns all fields required by this contract for
the deterministic demo evidence timeline. No backend follow-up issue is needed
for the MVP evidence display contract.
