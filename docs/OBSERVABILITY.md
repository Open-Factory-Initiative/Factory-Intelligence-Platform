# Observability

## Purpose

The platform should be explainable to developers and eventually plant users. Observability starts in local development.

## MVP Observability

Include:

- Structured logs
- Health checks
- Trace IDs in events
- Clear startup logs
- Error logs for rejected events
- Audit logs for recommendation decisions

## Log Fields

Recommended fields:

- `timestamp`
- `level`
- `service`
- `trace_id`
- `event_id`
- `message`
- `context`

## Health Checks

Each service should expose or support a health check.

Examples:

- API process is running
- Database reachable
- Broker reachable
- Simulator running
- Ingestion worker processing

## Metrics Direction

Future metrics:

- Events ingested per minute
- Invalid events per minute
- Detections created
- Recommendation approval latency
- E2E scenario duration
- Drift false-positive rate
