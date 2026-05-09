# MVP Scope

## MVP Name

Process Sentinel Vertical Slice

## Goal

Create a local, simulator-backed MVP that proves the platform can detect quality/process drift, explain it with evidence, and route a governed recommendation to a human.

## MVP Flow

```text
1. Start local stack.
2. Simulator emits factory events.
3. Ingestion service validates and stores events.
4. Process Sentinel evaluates recent process windows.
5. Drift detection creates a detection.
6. Evidence service builds a timeline.
7. Recommendation service creates a proposed action.
8. User reviews recommendation in web UI.
9. User approves, rejects, or defers.
10. System writes audit event.
11. System creates RCA/CAPA draft.
```

## In Scope

### Simulator

- One site
- One production area
- One line
- Three to five assets
- One product
- Work orders
- Process measurements
- Quality measurements
- At least three scenarios:
  - normal operation
  - gradual quality drift
  - sudden process excursion

### Data Model

- Site
- Area
- Line
- Asset
- Tag / signal
- Work order
- Material lot
- Process measurement
- Quality measurement
- Detection
- Evidence item
- Recommendation
- Approval decision
- Audit event

### Backend

- Health endpoint
- Event ingest endpoint
- Event query endpoint
- Detection query endpoint
- Evidence query endpoint
- Recommendation review endpoint
- Report draft endpoint

### UI

- Overview dashboard
- Detection list
- Detection detail
- Evidence timeline
- Recommendation approval panel
- RCA/CAPA draft preview

### Testing

- Unit tests for drift rules
- Unit tests for schema validation
- Integration tests for ingestion → storage
- API tests for core endpoints
- Playwright e2e test for full user workflow

### Documentation

- Setup
- Architecture
- Data contracts
- Testing
- Contribution guide
- Learning log

## Out Of Scope

- Real OPC UA integration
- Real MQTT production broker
- Real QMS writeback
- User authentication
- Multi-tenant support
- Cloud deployment
- Enterprise-grade observability
- Large language model decision autonomy
- Production industrial control

## MVP Milestones

### Milestone 1: Repo Foundation

- Monorepo structure
- Local dev commands
- CI placeholder
- Docs baseline

### Milestone 2: Shared Event Contracts

- Event schemas
- Sample events
- Contract tests

### Milestone 3: Simulator

- Deterministic scenarios
- Event emission
- Test fixtures

### Milestone 4: Ingestion + Storage

- Validate events
- Persist events
- Query events

### Milestone 5: Process Sentinel

- Drift rules
- Detections
- Evidence windows

### Milestone 6: Governed Recommendations

- Recommendation states
- Approval decisions
- Audit trail

### Milestone 7: Web Workbench

- Detection overview
- Evidence timeline
- Approval UI
- RCA/CAPA preview

### Milestone 8: E2E + Docs

- Playwright scenario
- Test documentation
- Architecture validation
