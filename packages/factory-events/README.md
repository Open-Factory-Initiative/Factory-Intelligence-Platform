# Factory Events

Shared event contracts for service boundaries in the Factory Intelligence Platform.

The package validates the MVP `FactoryEvent` envelope and the first Process
Sentinel event payloads. Services should import these models instead of passing
unvalidated dictionaries across boundaries.

`FactoryEvent` defines the shared base envelope: event identity, constrained
event type, UTC timestamp, source system, line and asset context, optional batch
and work order references, payload, and metadata. `EventEnvelope` remains as a
backward-compatible name for existing service code.

The current MVP contract includes typed envelopes for process measurements,
quality measurements, asset status updates, batch lifecycle events, work order
lifecycle events, and governed recommendation proposals.
