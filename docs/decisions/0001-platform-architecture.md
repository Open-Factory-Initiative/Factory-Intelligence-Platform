# ADR 0001: Simulator-First Modular Platform Architecture

## Status

Proposed

## Context

The Factory Intelligence Platform aims to become an open-source Factory Intelligence Layer for manufacturing operations. The long-term platform may connect to ERP, MES, SCADA, historians, QMS, CMMS, LIMS, WMS, and industrial protocols.

However, real industrial integrations introduce complexity, safety concerns, vendor-specific behavior, and access constraints.

## Decision

Start with a simulator-first architecture and build a narrow Process Sentinel vertical slice before connecting to real systems.

The platform will be organized around:

- Synthetic factory simulator
- Ingestion layer
- Unified factory event model
- Event storage
- Process Sentinel drift detection
- Evidence timeline
- Governed recommendation workflow
- Web UI workbench
- RCA/CAPA draft output

## Consequences

### Positive

- Easier for contributors to run locally
- Safer than connecting to real equipment
- Enables deterministic tests
- Supports demos and education
- Creates stable contracts before real integrations

### Negative

- Early MVP will not prove real connector complexity
- Simulator may oversimplify manufacturing reality
- Additional work will be needed for production-grade deployments

## Follow-Up Decisions

Future ADRs should cover:

- Event schema implementation
- Database choice
- Web framework choice
- Broker/eventing choice
- Governance/action dispatcher model
- Real connector strategy
