# API Service

FastAPI shell for the simulator-backed Process Sentinel MVP.

The API currently exposes:

- Health and event query endpoints.
- Read-only domain context endpoints for sites, areas, equipment, process
  signals, batches, quality results, deviations, alerts, and investigations.
- Process Sentinel detections, evidence, recommendations, and RCA/CAPA draft
  endpoints over local demo state.

## Local Web CORS

The API enables local Workbench browser calls from these default origins:

```text
http://127.0.0.1:3000
http://localhost:3000
http://127.0.0.1:3001
http://localhost:3001
```

Override the comma-separated list with `FACTORY_API_CORS_ORIGINS` when testing a
different local web origin. This is intended for the simulator-backed Workbench
demo path so client-side recommendation decisions can call the API directly.

Example:

```bash
uvicorn factory_api.main:app --reload --app-dir services/api
```
