# Unified Namespace

## Purpose

The Unified Namespace, or UNS, is the conceptual event backbone of the Factory Intelligence Platform. It gives factory data a consistent structure so applications can reason about assets, process signals, quality outcomes, work orders, and recommendations.

The MVP does not need a full industrial UNS implementation. It needs a clear topic and event model that can evolve.

## Topic Pattern

Recommended topic pattern:

```text
ofi/{site}/{area}/{line}/{asset_or_context}/{event_category}/{event_name}
```

Examples:

```text
ofi/demo-site/packaging/line-1/filler-1/process/measurement-recorded
ofi/demo-site/packaging/line-1/filler-1/asset/status-changed
ofi/demo-site/packaging/line-1/work-orders/work-order-started
ofi/demo-site/packaging/line-1/quality/measurement-recorded
ofi/demo-site/packaging/line-1/sentinel/detection-created
ofi/demo-site/packaging/line-1/governance/recommendation-proposed
```

## Event Naming

Use past-tense event names:

- `measurement-recorded`
- `work-order-started`
- `detection-created`
- `recommendation-proposed`
- `approval-recorded`

Avoid command-like events for the MVP:

- Avoid `set-speed`
- Avoid `release-product`
- Avoid `close-deviation`

Commands imply action. MVP events should describe facts and human-approved decisions.

## MVP UNS Scope

The MVP UNS should support:

- Simulator event publishing
- Ingestion topic mapping
- Event validation
- Event persistence
- Query by context
- Query by time window
- Query by detection/recommendation relationship

## Long-Term UNS Direction

Future versions may support:

- Real MQTT brokers
- OPC UA mapping
- Historian mapping
- Asset hierarchy discovery
- Event replay
- Stream processing
- Multi-site federation
- Role-based topic access
- External consumers
