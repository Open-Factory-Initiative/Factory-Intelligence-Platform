# Prompt 05: API Service

Act as a senior FastAPI backend engineer.

Goal: implement the first API service for the MVP.

Endpoints:

- `GET /health`
- `GET /events`
- `GET /events/{event_id}`
- `GET /sentinel/detections`
- `GET /sentinel/detections/{detection_id}`
- `GET /sentinel/detections/{detection_id}/evidence`
- `GET /recommendations`
- `POST /recommendations/{recommendation_id}/approve`
- `POST /recommendations/{recommendation_id}/reject`
- `POST /recommendations/{recommendation_id}/defer`

Requirements:

- Use typed models
- Generate OpenAPI docs
- Include API tests
- Use shared event contracts
- Keep auth out of scope unless already present
- Update docs and learning log
