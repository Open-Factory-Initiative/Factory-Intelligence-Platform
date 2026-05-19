from __future__ import annotations

import os
from pathlib import Path

from factory_ingestion.storage import JsonlEventStore
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from process_sentinel.storage import SentinelStateStore
from pydantic import BaseModel, Field

from factory_api.domain import DomainData, build_demo_domain_data


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
    domain_data: DomainData | None = None,
) -> FastAPI:
    resolved_events_store = events_store_path or Path(
        os.getenv("FACTORY_EVENTS_STORE", ".local/storage/events.jsonl")
    )
    resolved_state_dir = sentinel_state_dir or Path(
        os.getenv("SENTINEL_STATE_DIR", ".local/storage/sentinel")
    )
    resolved_domain_data = domain_data or build_demo_domain_data()

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

    def domain() -> DomainData:
        return resolved_domain_data

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

    @app.get("/sites")
    def list_sites() -> list[dict]:
        return [item.model_dump(mode="json") for item in domain().sites]

    @app.get("/sites/{site_id}")
    def get_site(site_id: str) -> dict:
        site = domain().get_site(site_id)
        if site is None:
            raise_not_found("site_not_found", f"Site not found: {site_id}")
        return site.model_dump(mode="json")

    @app.get("/areas")
    def list_areas(site_id: str | None = None) -> list[dict]:
        areas = domain().areas
        if site_id is not None:
            areas = [area for area in areas if area.site_id == site_id]
        return [item.model_dump(mode="json") for item in areas]

    @app.get("/areas/{area_id}")
    def get_area(area_id: str) -> dict:
        area = domain().get_area(area_id)
        if area is None:
            raise_not_found("area_not_found", f"Area not found: {area_id}")
        return area.model_dump(mode="json")

    @app.get("/equipment")
    def list_equipment(area_id: str | None = None) -> list[dict]:
        equipment = domain().equipment
        if area_id is not None:
            equipment = [item for item in equipment if item.area_id == area_id]
        return [item.model_dump(mode="json") for item in equipment]

    @app.get("/equipment/{equipment_id}")
    def get_equipment(equipment_id: str) -> dict:
        equipment = domain().get_equipment(equipment_id)
        if equipment is None:
            raise_not_found("equipment_not_found", f"Equipment not found: {equipment_id}")
        return equipment.model_dump(mode="json")

    @app.get("/process-signals")
    def list_process_signals(equipment_id: str | None = None) -> list[dict]:
        signals = domain().process_signals
        if equipment_id is not None:
            signals = [signal for signal in signals if signal.equipment_id == equipment_id]
        return [item.model_dump(mode="json") for item in signals]

    @app.get("/process-signals/{signal_id}")
    def get_process_signal(signal_id: str) -> dict:
        signal = domain().get_process_signal(signal_id)
        if signal is None:
            raise_not_found("process_signal_not_found", f"Process signal not found: {signal_id}")
        return signal.model_dump(mode="json")

    @app.get("/batches")
    def list_batches(area_id: str | None = None, status: str | None = None) -> list[dict]:
        batches = domain().batches
        if area_id is not None:
            batches = [batch for batch in batches if batch.area_id == area_id]
        if status is not None:
            batches = [batch for batch in batches if batch.status == status]
        return [item.model_dump(mode="json") for item in batches]

    @app.get("/batches/{batch_id}")
    def get_batch(batch_id: str) -> dict:
        batch = domain().get_batch(batch_id)
        if batch is None:
            raise_not_found("batch_not_found", f"Batch not found: {batch_id}")
        return batch.model_dump(mode="json")

    @app.get("/quality-results")
    def list_quality_results(batch_id: str | None = None) -> list[dict]:
        results = domain().quality_results
        if batch_id is not None:
            results = [result for result in results if result.batch_id == batch_id]
        return [item.model_dump(mode="json") for item in results]

    @app.get("/quality-results/{quality_result_id}")
    def get_quality_result(quality_result_id: str) -> dict:
        result = domain().get_quality_result(quality_result_id)
        if result is None:
            raise_not_found(
                "quality_result_not_found", f"Quality result not found: {quality_result_id}"
            )
        return result.model_dump(mode="json")

    @app.get("/deviations")
    def list_deviations(batch_id: str | None = None) -> list[dict]:
        deviations = domain().deviations
        if batch_id is not None:
            deviations = [deviation for deviation in deviations if deviation.batch_id == batch_id]
        return [item.model_dump(mode="json") for item in deviations]

    @app.get("/deviations/{deviation_id}")
    def get_deviation(deviation_id: str) -> dict:
        deviation = domain().get_deviation(deviation_id)
        if deviation is None:
            raise_not_found("deviation_not_found", f"Deviation not found: {deviation_id}")
        return deviation.model_dump(mode="json")

    @app.get("/alerts")
    def list_alerts(batch_id: str | None = None, status: str | None = None) -> list[dict]:
        alerts = domain().alerts
        if batch_id is not None:
            alerts = [alert for alert in alerts if alert.batch_id == batch_id]
        if status is not None:
            alerts = [alert for alert in alerts if alert.status == status]
        return [item.model_dump(mode="json") for item in alerts]

    @app.get("/alerts/{alert_id}")
    def get_alert(alert_id: str) -> dict:
        alert = domain().get_alert(alert_id)
        if alert is None:
            raise_not_found("alert_not_found", f"Alert not found: {alert_id}")
        return alert.model_dump(mode="json")

    @app.get("/investigations")
    def list_investigations(status: str | None = None) -> list[dict]:
        investigations = domain().investigations
        if status is not None:
            investigations = [
                investigation for investigation in investigations if investigation.status == status
            ]
        return [item.model_dump(mode="json") for item in investigations]

    @app.get("/investigations/{investigation_id}")
    def get_investigation(investigation_id: str) -> dict:
        investigation = domain().get_investigation_detail(investigation_id)
        if investigation is None:
            raise_not_found(
                "investigation_not_found", f"Investigation not found: {investigation_id}"
            )
        return investigation.model_dump(mode="json")

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
        response = approval.model_dump(mode="json")
        response["timestamp"] = response["created_at"]
        return response

    return app


def raise_not_found(code: str, message: str) -> None:
    raise ApiNotFoundError(code, message)


app = create_app()
