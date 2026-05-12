from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SUPPORTED_SCHEMA_VERSION = "1.0.0"


class UnsupportedEventTypeError(ValueError):
    """Raised when an event type is outside the current MVP contract."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EventSource(StrictModel):
    system: str = Field(min_length=1)
    adapter: str = Field(min_length=1)
    source_event_id: str = Field(min_length=1)


class EventContext(StrictModel):
    site_id: str = Field(min_length=1)
    area_id: str = Field(min_length=1)
    line_id: str = Field(min_length=1)
    asset_id: str | None = None
    batch_id: str | None = None
    work_order_id: str | None = None


class EventMetadata(StrictModel):
    simulated: bool
    trace_id: str = Field(min_length=1)


class ProcessMeasurementPayload(StrictModel):
    signal_id: str = Field(min_length=1)
    signal_name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    quality: Literal["good", "uncertain", "bad"]


class QualityMeasurementPayload(StrictModel):
    measurement_name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    spec_min: float
    spec_max: float
    result: Literal["pass", "fail"]

    @model_validator(mode="after")
    def validate_spec_range(self) -> QualityMeasurementPayload:
        if self.spec_min >= self.spec_max:
            msg = "spec_min must be less than spec_max"
            raise ValueError(msg)
        return self


class SentinelDetectionPayload(StrictModel):
    detection_id: str = Field(min_length=1)
    detection_type: Literal["quality_drift", "process_excursion"]
    severity: Literal["low", "medium", "high"]
    summary: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    time_window_start: datetime
    time_window_end: datetime

    @field_validator("time_window_start", "time_window_end")
    @classmethod
    def require_utc_window(cls, value: datetime) -> datetime:
        return require_utc_datetime(value)

    @model_validator(mode="after")
    def validate_window(self) -> SentinelDetectionPayload:
        if self.time_window_start >= self.time_window_end:
            msg = "time_window_start must be before time_window_end"
            raise ValueError(msg)
        return self


class RecommendationPayload(StrictModel):
    recommendation_id: str = Field(min_length=1)
    detection_id: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)
    risk_level: Literal["low", "medium", "high"]
    requires_approval: bool
    evidence_ids: list[str] = Field(min_length=1)


class ApprovalDecisionPayload(StrictModel):
    approval_id: str = Field(min_length=1)
    recommendation_id: str = Field(min_length=1)
    decision: Literal["approved", "rejected", "deferred", "needs_more_evidence"]
    reviewer: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class AuditEventPayload(StrictModel):
    audit_event_id: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    action: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    entity_id: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)


Payload = (
    ProcessMeasurementPayload
    | QualityMeasurementPayload
    | SentinelDetectionPayload
    | RecommendationPayload
    | ApprovalDecisionPayload
    | AuditEventPayload
)


EVENT_PAYLOAD_MODELS: dict[str, type[Payload]] = {
    "process.measurement.recorded": ProcessMeasurementPayload,
    "quality.measurement.recorded": QualityMeasurementPayload,
    "sentinel.detection.created": SentinelDetectionPayload,
    "governance.recommendation.proposed": RecommendationPayload,
    "governance.approval.recorded": ApprovalDecisionPayload,
    "governance.audit.recorded": AuditEventPayload,
}


class FactoryEvent(StrictModel):
    event_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    schema_version: str
    timestamp: datetime
    source: EventSource
    context: EventContext
    payload: Payload
    metadata: EventMetadata

    @field_validator("timestamp")
    @classmethod
    def require_utc_timestamp(cls, value: datetime) -> datetime:
        return require_utc_datetime(value)

    @model_validator(mode="before")
    @classmethod
    def validate_payload_for_event_type(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        event_type = data.get("event_type")
        if not isinstance(event_type, str):
            return data
        payload_model = payload_model_for_event_type(event_type)
        data = data.copy()
        data["payload"] = payload_model.model_validate(data.get("payload", {}))
        return data

    @model_validator(mode="after")
    def validate_envelope_rules(self) -> FactoryEvent:
        if self.schema_version != SUPPORTED_SCHEMA_VERSION:
            msg = f"schema_version must be {SUPPORTED_SCHEMA_VERSION}"
            raise ValueError(msg)
        if self.source.adapter == "simulator" and self.metadata.simulated is not True:
            msg = "simulator events must include metadata.simulated = true"
            raise ValueError(msg)
        return self


class EventEnvelope(FactoryEvent):
    """Backward-compatible name for the base FactoryEvent envelope."""


def require_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        msg = "timestamp values must be timezone-aware UTC datetimes"
        raise ValueError(msg)
    return value


def payload_model_for_event_type(event_type: str) -> type[Payload]:
    try:
        return EVENT_PAYLOAD_MODELS[event_type]
    except KeyError as exc:
        msg = f"unsupported event_type: {event_type}"
        raise UnsupportedEventTypeError(msg) from exc


def validate_event(data: dict[str, Any]) -> FactoryEvent:
    event_type = data.get("event_type")
    if isinstance(event_type, str):
        payload_model_for_event_type(event_type)
    return FactoryEvent.model_validate(data)
