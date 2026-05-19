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
    tag_name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    quality: Literal["good", "uncertain", "bad"]
    normal_min: float | None = None
    normal_max: float | None = None
    target_value: float | None = None

    @model_validator(mode="after")
    def validate_normal_range(self) -> ProcessMeasurementPayload:
        if self.normal_min is None and self.normal_max is None:
            return self
        if self.normal_min is None or self.normal_max is None:
            msg = "normal_min and normal_max must be provided together"
            raise ValueError(msg)
        if self.normal_min >= self.normal_max:
            msg = "normal_min must be less than normal_max"
            raise ValueError(msg)
        return self


class QualityMeasurementPayload(StrictModel):
    quality_check_type: Literal[
        "inspection",
        "lab_result",
        "inline_check",
        "deviation",
        "defect",
        "outcome_marker",
    ]
    measurement_name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    result_status: Literal["pass", "fail", "warning", "inconclusive"]
    result: Literal["pass", "fail"] | None = None
    severity: Literal["low", "medium", "high", "critical"]
    spec_min: float | None = None
    spec_max: float | None = None

    @model_validator(mode="after")
    def validate_spec_range(self) -> QualityMeasurementPayload:
        if self.spec_min is None and self.spec_max is None:
            return self
        if self.spec_min is None or self.spec_max is None:
            msg = "spec_min and spec_max must be provided together"
            raise ValueError(msg)
        if self.spec_min >= self.spec_max:
            msg = "spec_min must be less than spec_max"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_result_compatibility(self) -> QualityMeasurementPayload:
        if self.result is not None and self.result != self.result_status:
            msg = "result must match result_status when both are provided"
            raise ValueError(msg)
        return self


BatchStatus = Literal["planned", "started", "completed", "held", "released", "cancelled"]
WorkOrderStatus = Literal["planned", "started", "completed", "held", "cancelled"]
AssetStatus = Literal["running", "idle", "stopped", "faulted", "maintenance", "offline"]


class AssetEventPayload(StrictModel):
    asset_id: str = Field(min_length=1)
    asset_name: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)
    previous_status: AssetStatus | None = None
    status: AssetStatus
    status_reason: str | None = None


class BatchEventPayload(StrictModel):
    batch_id: str = Field(min_length=1)
    lot_id: str = Field(min_length=1)
    product_id: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    material_id: str | None = None
    material_name: str | None = None
    work_order_id: str | None = None
    previous_status: BatchStatus | None = None
    status: BatchStatus
    status_reason: str | None = None


class WorkOrderEventPayload(StrictModel):
    work_order_id: str = Field(min_length=1)
    product_id: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    material_id: str | None = None
    material_name: str | None = None
    batch_id: str | None = None
    lot_id: str | None = None
    previous_status: WorkOrderStatus | None = None
    status: WorkOrderStatus
    status_reason: str | None = None


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
    | AssetEventPayload
    | BatchEventPayload
    | WorkOrderEventPayload
    | SentinelDetectionPayload
    | RecommendationPayload
    | ApprovalDecisionPayload
    | AuditEventPayload
)


EVENT_PAYLOAD_MODELS: dict[str, type[Payload]] = {
    "process.measurement.recorded": ProcessMeasurementPayload,
    "quality.measurement.recorded": QualityMeasurementPayload,
    "asset.status.updated": AssetEventPayload,
    "production.batch.started": BatchEventPayload,
    "production.batch.completed": BatchEventPayload,
    "production.batch.status.updated": BatchEventPayload,
    "production.work_order.started": WorkOrderEventPayload,
    "production.work_order.completed": WorkOrderEventPayload,
    "production.work_order.status.updated": WorkOrderEventPayload,
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
        self.validate_asset_event_rules()
        self.validate_production_event_rules()
        return self

    def validate_asset_event_rules(self) -> None:
        if isinstance(self.payload, AssetEventPayload):
            if self.context.asset_id is not None and self.context.asset_id != self.payload.asset_id:
                msg = "context.asset_id must match payload.asset_id"
                raise ValueError(msg)

    def validate_production_event_rules(self) -> None:
        if isinstance(self.payload, BatchEventPayload):
            if self.context.batch_id is not None and self.context.batch_id != self.payload.batch_id:
                msg = "context.batch_id must match payload.batch_id"
                raise ValueError(msg)
            if (
                self.context.work_order_id is not None
                and self.payload.work_order_id is not None
                and self.context.work_order_id != self.payload.work_order_id
            ):
                msg = "context.work_order_id must match payload.work_order_id"
                raise ValueError(msg)
            expected_status_by_type = {
                "production.batch.started": "started",
                "production.batch.completed": "completed",
            }
            expected_status = expected_status_by_type.get(self.event_type)
            if expected_status is not None and self.payload.status != expected_status:
                msg = f"{self.event_type} payload.status must be {expected_status}"
                raise ValueError(msg)
        if isinstance(self.payload, WorkOrderEventPayload):
            if (
                self.context.work_order_id is not None
                and self.context.work_order_id != self.payload.work_order_id
            ):
                msg = "context.work_order_id must match payload.work_order_id"
                raise ValueError(msg)
            if (
                self.context.batch_id is not None
                and self.payload.batch_id is not None
                and self.context.batch_id != self.payload.batch_id
            ):
                msg = "context.batch_id must match payload.batch_id"
                raise ValueError(msg)
            expected_status_by_type = {
                "production.work_order.started": "started",
                "production.work_order.completed": "completed",
            }
            expected_status = expected_status_by_type.get(self.event_type)
            if expected_status is not None and self.payload.status != expected_status:
                msg = f"{self.event_type} payload.status must be {expected_status}"
                raise ValueError(msg)


class EventEnvelope(FactoryEvent):
    """Backward-compatible name for the base FactoryEvent envelope."""


class ProcessSignalEvent(FactoryEvent):
    event_type: Literal["process.measurement.recorded"]
    payload: ProcessMeasurementPayload


class QualityEvent(FactoryEvent):
    event_type: Literal["quality.measurement.recorded"]
    payload: QualityMeasurementPayload


class AssetEvent(FactoryEvent):
    event_type: Literal["asset.status.updated"]
    payload: AssetEventPayload


class BatchEvent(FactoryEvent):
    event_type: Literal[
        "production.batch.started",
        "production.batch.completed",
        "production.batch.status.updated",
    ]
    payload: BatchEventPayload


class WorkOrderEvent(FactoryEvent):
    event_type: Literal[
        "production.work_order.started",
        "production.work_order.completed",
        "production.work_order.status.updated",
    ]
    payload: WorkOrderEventPayload


class RecommendationEvent(FactoryEvent):
    event_type: Literal["governance.recommendation.proposed"]
    payload: RecommendationPayload


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
