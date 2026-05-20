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

The API allows the local Workbench origins needed for browser-side demo actions
by default. Override the comma-separated `FACTORY_API_CORS_ORIGINS` value when
running the API on different local web origins.

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
- `/recommendations` - Governed recommendation review panel with reviewer,
  reason, approve/reject/defer controls, and decision feedback
- `/recommendations?detection_id={detection_id}` - Recommendation review scoped
  to the selected Process Sentinel detection
- `/rca-capa-draft` - RCA/CAPA draft preview for the first available demo detection
- `/rca-capa-draft?detection_id={detection_id}` - RCA/CAPA draft preview
  scoped to the selected Process Sentinel detection

The shell labels all demo content as simulator-backed data. The pages include
loading states, empty states, and simple user-readable API error states.

## Governance Decision Feedback

After a reviewer approves, rejects, or defers a recommendation, the Workbench
shows the reviewer, decision, reason, timestamp, recommendation ID, and refreshed
recommendation status without requiring a page refresh. This feedback is a demo
audit trail from the decision POST response, not a validated production audit
record, electronic signature, or external QMS/MES writeback.

The backend currently records local approval decisions and audit events, but it
does not expose a read endpoint for recommendation audit history. Follow-up
backend issue #159 tracks adding that API so the Workbench can later reload
decision history from the server instead of relying only on the POST response.

## RCA/CAPA Draft Preview

The RCA/CAPA draft page loads draft investigation language from
`GET /reports/rca-capa-drafts/{detection_id}`. Detection and recommendation
pages link to it with the selected `detection_id`, and the page shows title,
problem statement, evidence summary, recommended containment, and CAPA
placeholder sections. The copy button copies a plain-text draft for demo review.

The draft is marked as demo-generated decision support that requires human
review. It does not create a CAPA, claim validation status, or submit records to
QMS or MES.

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
For the manufacturer-facing 8-10 minute checklist, talk track, demo boundaries,
and feedback prompts, see `../../docs/demo/MANUFACTURER_DEMO_RUNBOOK.md`.
For local demo failure recovery, see
`../../docs/demo/TROUBLESHOOTING.md`.

## Checks

```bash
npm run lint
npm run typecheck
npm test
npm run build
```
