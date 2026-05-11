from __future__ import annotations

import os
from pathlib import Path

from factory_ingestion.storage import JsonlEventStore
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from process_sentinel.storage import SentinelStateStore
from pydantic import BaseModel, Field


class ApiNotFoundError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message


class RecommendationDecisionRequest(BaseModel):
    reviewer: str = Field(min_length=1)
    reason: str = Field(min_length=1)


def create_app(
    *,
    events_store_path: Path | None = None,
    sentinel_state_dir: Path | None = None,
) -> FastAPI:
    resolved_events_store = events_store_path or Path(
        os.getenv("FACTORY_EVENTS_STORE", ".local/storage/events.jsonl")
    )
    resolved_state_dir = sentinel_state_dir or Path(
        os.getenv("SENTINEL_STATE_DIR", ".local/storage/sentinel")
    )

    app = FastAPI(
        title="Factory Intelligence Platform API",
        version="0.1.0",
        description="Simulator-backed Process Sentinel MVP API.",
    )

    @app.exception_handler(ApiNotFoundError)
    def not_found_handler(_request: object, exc: ApiNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    def event_store() -> JsonlEventStore:
        return JsonlEventStore(resolved_events_store)

    def sentinel_store() -> SentinelStateStore:
        return SentinelStateStore(resolved_state_dir)

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "simulator_backed": True,
            "events_store": str(resolved_events_store),
            "sentinel_state_dir": str(resolved_state_dir),
        }

    @app.get("/events")
    def list_events(event_type: str | None = None) -> list[dict]:
        events = event_store().list_events()
        if event_type is not None:
            events = [event for event in events if event.event_type == event_type]
        return [event.model_dump(mode="json") for event in events]

    @app.get("/events/{event_id}")
    def get_event(event_id: str) -> dict:
        event = event_store().get_event(event_id)
        if event is None:
            raise_not_found("event_not_found", f"Event not found: {event_id}")
        return event.model_dump(mode="json")

    @app.get("/sentinel/detections")
    def list_detections() -> list[dict]:
        return [item.model_dump(mode="json") for item in sentinel_store().list_detections()]

    @app.get("/sentinel/detections/{detection_id}")
    def get_detection(detection_id: str) -> dict:
        detection = sentinel_store().get_detection(detection_id)
        if detection is None:
            raise_not_found("detection_not_found", f"Detection not found: {detection_id}")
        return detection.model_dump(mode="json")

    @app.get("/sentinel/detections/{detection_id}/evidence")
    def list_detection_evidence(detection_id: str) -> list[dict]:
        if sentinel_store().get_detection(detection_id) is None:
            raise_not_found("detection_not_found", f"Detection not found: {detection_id}")
        return [
            item.model_dump(mode="json") for item in sentinel_store().list_evidence(detection_id)
        ]

    @app.get("/recommendations")
    def list_recommendations() -> list[dict]:
        return [item.model_dump(mode="json") for item in sentinel_store().list_recommendations()]

    @app.get("/recommendations/{recommendation_id}")
    def get_recommendation(recommendation_id: str) -> dict:
        recommendation = sentinel_store().get_recommendation(recommendation_id)
        if recommendation is None:
            raise_not_found(
                "recommendation_not_found", f"Recommendation not found: {recommendation_id}"
            )
        return recommendation.model_dump(mode="json")

    @app.post("/recommendations/{recommendation_id}/approve")
    def approve_recommendation(
        recommendation_id: str, request: RecommendationDecisionRequest
    ) -> dict:
        return _record_decision(recommendation_id, "approved", request)

    @app.post("/recommendations/{recommendation_id}/reject")
    def reject_recommendation(
        recommendation_id: str, request: RecommendationDecisionRequest
    ) -> dict:
        return _record_decision(recommendation_id, "rejected", request)

    @app.post("/recommendations/{recommendation_id}/defer")
    def defer_recommendation(
        recommendation_id: str, request: RecommendationDecisionRequest
    ) -> dict:
        return _record_decision(recommendation_id, "deferred", request)

    @app.get("/reports/rca-capa-drafts/{detection_id}")
    def get_rca_capa_draft(detection_id: str) -> dict:
        draft = sentinel_store().build_rca_capa_draft(detection_id)
        if draft is None:
            raise_not_found("detection_not_found", f"Detection not found: {detection_id}")
        return draft.model_dump(mode="json")

    def _record_decision(
        recommendation_id: str, decision: str, request: RecommendationDecisionRequest
    ) -> dict:
        try:
            approval = sentinel_store().record_decision(
                recommendation_id=recommendation_id,
                decision=decision,
                reviewer=request.reviewer,
                reason=request.reason,
            )
        except KeyError:
            raise_not_found(
                "recommendation_not_found", f"Recommendation not found: {recommendation_id}"
            )
        return approval.model_dump(mode="json")

    return app


def raise_not_found(code: str, message: str) -> None:
    raise ApiNotFoundError(code, message)


app = create_app()
