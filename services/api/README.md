# API Service

FastAPI shell for the simulator-backed Process Sentinel MVP.

The API currently exposes:

- Health and event query endpoints.
- Read-only domain context endpoints for sites, areas, equipment, process
  signals, batches, quality results, deviations, alerts, and investigations.
- Process Sentinel detections, evidence, recommendations, and RCA/CAPA draft
  endpoints over local demo state.

Example:

```bash
uvicorn factory_api.main:app --reload --app-dir services/api
```
