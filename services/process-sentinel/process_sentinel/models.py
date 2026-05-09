from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Detection(StrictModel):
    detection_id: str
    detection_type: Literal["quality_drift", "process_excursion"]
    severity: Literal["low", "medium", "high"]
    status: Literal[
        "new",
        "investigating",
        "recommendation_created",
        "acknowledged",
        "closed",
        "false_positive",
    ]
    created_at: datetime
    time_window_start: datetime
    time_window_end: datetime
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    related_work_order_id: str | None
    related_asset_ids: list[str]


class EvidenceItem(StrictModel):
    evidence_id: str
    detection_id: str
    evidence_type: Literal["process_signal", "quality_result", "correlation_window"]
    timestamp: datetime
    title: str
    description: str
    source_event_ids: list[str]
    score: float = Field(ge=0.0, le=1.0)


class Recommendation(StrictModel):
    recommendation_id: str
    detection_id: str
    status: Literal["draft", "proposed", "needs_review", "approved", "rejected", "deferred"]
    recommended_action: str
    rationale: str
    risk_level: Literal["low", "medium", "high"]
    requires_approval: bool
    evidence_ids: list[str]
    created_at: datetime


class ApprovalDecision(StrictModel):
    approval_id: str
    recommendation_id: str
    reviewer: str
    decision: Literal["approved", "rejected", "deferred", "needs_more_evidence"]
    reason: str
    created_at: datetime


class AuditEvent(StrictModel):
    audit_event_id: str
    timestamp: datetime
    actor: str
    action: str
    entity_type: str
    entity_id: str
    details: dict


class SentinelRunResult(StrictModel):
    detections: list[Detection]
    evidence_items: list[EvidenceItem]
    recommendations: list[Recommendation]


class RcaCapaDraft(StrictModel):
    detection_id: str
    title: str
    problem_statement: str
    evidence_summary: list[str]
    recommended_containment: str
    capa_placeholder: str

