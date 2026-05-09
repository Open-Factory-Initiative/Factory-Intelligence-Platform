# Prompt 04: Ingestion Service

Act as a senior backend/data ingestion engineer.

Goal: implement the first ingestion service that reads simulator events, validates them, and persists or stages them for the API.

Requirements:

- Accept simulator events
- Validate against shared contracts
- Reject invalid events with clear errors
- Preserve source metadata
- Include structured logs
- Include unit and integration tests
- Include a simple local run command
- Update docs and learning log

Do not add real OPC UA, MQTT production, MES, QMS, or ERP integration yet.
