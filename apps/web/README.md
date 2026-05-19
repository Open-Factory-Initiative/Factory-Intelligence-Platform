# Operations Workbench

Minimal Next.js app shell for the simulator-backed Process Sentinel demo.

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

## Routes

- `/` - Overview
- `/detections` - Process Sentinel detections placeholder
- `/recommendations` - Governed recommendation review placeholder
- `/rca-capa-draft` - RCA/CAPA draft placeholder

The shell labels all placeholder content as simulator-backed demo data. Future
issues should replace placeholders with API-backed views using the existing
FastAPI endpoints and `docs/EVIDENCE_TIMELINE_API_CONTRACT.md` for evidence
timeline fields.

## Checks

```bash
npm run lint
npm run typecheck
npm test
npm run build
```
