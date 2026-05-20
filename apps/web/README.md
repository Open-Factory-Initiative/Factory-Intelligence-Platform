# Operations Workbench

Minimal Next.js app shell for the simulator-backed Process Sentinel demo. The
Workbench reads from the local FastAPI backend through a small typed API client
in `lib/api-client.ts`.

## Local Startup

Install dependencies from this directory:

```bash
npm install
```

Run the app:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:3000
```

## API Base URL

The frontend reads the local FastAPI backend URL from
`NEXT_PUBLIC_API_BASE_URL`.

Default:

```text
http://127.0.0.1:8000
```

Override without code changes:

```bash
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

The API client currently covers:

- `GET /health`
- `GET /sites`
- `GET /areas`
- `GET /equipment`
- `GET /batches`
- `GET /sentinel/detections`
- `GET /sentinel/detections/{detection_id}`
- `GET /sentinel/detections/{detection_id}/evidence`
- `GET /recommendations`
- `GET /recommendations/{recommendation_id}`
- `POST /recommendations/{recommendation_id}/approve`
- `POST /recommendations/{recommendation_id}/reject`
- `POST /recommendations/{recommendation_id}/defer`
- `GET /reports/rca-capa-drafts/{detection_id}`

When the backend is unavailable, the demo pages render a readable API connection
message instead of failing silently.

## Routes

- `/` - Factory overview dashboard with site, line, asset, work order, product,
  active detection count, pending recommendation count, and primary detection CTA
- `/detections` - Process Sentinel detection list with summary, severity,
  confidence, status, time window, work order, related assets, and detail links
- `/detections/{detection_id}` - Read-only Process Sentinel detection detail
  with a plain-English `Why this was flagged` explanation, API-backed evidence
  timeline, recommendation review link, and RCA/CAPA draft link
- `/recommendations` - Governed recommendation review preview
- `/rca-capa-draft` - RCA/CAPA draft preview

The shell labels all demo content as simulator-backed data. The pages include
loading states, empty states, and simple user-readable API error states.

## Manual API Check

In one terminal, prepare and run the backend demo API:

```bash
make demo-reset
make demo-data
make demo-ingest
make demo-sentinel-run
make api
```

In another terminal, run:

```bash
cd apps/web
npm run dev
```

Then open `http://127.0.0.1:3000` and verify Overview, Detections,
Recommendations, and RCA/CAPA Draft render against the configured API base URL.

## Checks

```bash
npm run lint
npm run typecheck
npm test
npm run build
```
