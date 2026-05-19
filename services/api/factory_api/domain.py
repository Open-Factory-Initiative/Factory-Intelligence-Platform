from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Site(StrictModel):
    site_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    timezone: str = Field(min_length=1)
    description: str


class Area(StrictModel):
    area_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str


class Equipment(StrictModel):
    equipment_id: str = Field(min_length=1)
    area_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    equipment_type: str = Field(min_length=1)
    criticality: Literal["low", "medium", "high"]


class ProcessSignal(StrictModel):
    signal_id: str = Field(min_length=1)
    equipment_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    normal_min: float
    normal_max: float

    @model_validator(mode="after")
    def validate_normal_range(self) -> ProcessSignal:
        if self.normal_min >= self.normal_max:
            msg = "normal_min must be less than normal_max"
            raise ValueError(msg)
        return self


class Batch(StrictModel):
    batch_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    area_id: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    status: Literal["planned", "running", "completed", "held", "released"]
    started_at: datetime
    ended_at: datetime | None


class QualityResult(StrictModel):
    quality_result_id: str = Field(min_length=1)
    batch_id: str = Field(min_length=1)
    measurement_name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    spec_min: float
    spec_max: float
    result: Literal["pass", "fail"]
    related_signal_ids: list[str] = Field(min_length=1)
    recorded_at: datetime

    @model_validator(mode="after")
    def validate_spec_range(self) -> QualityResult:
        if self.spec_min >= self.spec_max:
            msg = "spec_min must be less than spec_max"
            raise ValueError(msg)
        return self


class Deviation(StrictModel):
    deviation_id: str = Field(min_length=1)
    batch_id: str = Field(min_length=1)
    quality_result_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]
    status: Literal["open", "under_investigation", "closed"]
    related_signal_ids: list[str] = Field(min_length=1)
    opened_at: datetime


class Alert(StrictModel):
    alert_id: str = Field(min_length=1)
    deviation_id: str | None
    batch_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]
    status: Literal["active", "acknowledged", "closed"]
    triggered_at: datetime


class Investigation(StrictModel):
    investigation_id: str = Field(min_length=1)
    deviation_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: Literal["open", "in_review", "closed"]
    owner: str = Field(min_length=1)
    alert_ids: list[str] = Field(min_length=1)
    quality_result_ids: list[str] = Field(min_length=1)
    related_signal_ids: list[str] = Field(min_length=1)
    opened_at: datetime


class InvestigationDetail(StrictModel):
    investigation: Investigation
    deviation: Deviation
    alerts: list[Alert]
    quality_results: list[QualityResult]
    process_signals: list[ProcessSignal]


class DomainData(StrictModel):
    sites: list[Site]
    areas: list[Area]
    equipment: list[Equipment]
    process_signals: list[ProcessSignal]
    batches: list[Batch]
    quality_results: list[QualityResult]
    deviations: list[Deviation]
    alerts: list[Alert]
    investigations: list[Investigation]

    def get_site(self, site_id: str) -> Site | None:
        return _get_by_id(self.sites, "site_id", site_id)

    def get_area(self, area_id: str) -> Area | None:
        return _get_by_id(self.areas, "area_id", area_id)

    def get_equipment(self, equipment_id: str) -> Equipment | None:
        return _get_by_id(self.equipment, "equipment_id", equipment_id)

    def get_process_signal(self, signal_id: str) -> ProcessSignal | None:
        return _get_by_id(self.process_signals, "signal_id", signal_id)

    def get_batch(self, batch_id: str) -> Batch | None:
        return _get_by_id(self.batches, "batch_id", batch_id)

    def get_quality_result(self, quality_result_id: str) -> QualityResult | None:
        return _get_by_id(self.quality_results, "quality_result_id", quality_result_id)

    def get_deviation(self, deviation_id: str) -> Deviation | None:
        return _get_by_id(self.deviations, "deviation_id", deviation_id)

    def get_alert(self, alert_id: str) -> Alert | None:
        return _get_by_id(self.alerts, "alert_id", alert_id)

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        return _get_by_id(self.investigations, "investigation_id", investigation_id)

    def get_investigation_detail(self, investigation_id: str) -> InvestigationDetail | None:
        investigation = self.get_investigation(investigation_id)
        if investigation is None:
            return None
        deviation = self.get_deviation(investigation.deviation_id)
        if deviation is None:
            return None
        return InvestigationDetail(
            investigation=investigation,
            deviation=deviation,
            alerts=[alert for alert in self.alerts if alert.alert_id in investigation.alert_ids],
            quality_results=[
                result
                for result in self.quality_results
                if result.quality_result_id in investigation.quality_result_ids
            ],
            process_signals=[
                signal
                for signal in self.process_signals
                if signal.signal_id in investigation.related_signal_ids
            ],
        )


def build_demo_domain_data() -> DomainData:
    started_at = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    drift_at = datetime(2026, 1, 1, 12, 23, tzinfo=UTC)

    return DomainData(
        sites=[
            Site(
                site_id="greenville_demo_site",
                name="Greenville Demo Site",
                timezone="America/New_York",
                description="Simulator-backed Greenville site used for the manufacturer demo.",
            )
        ],
        areas=[
            Area(
                area_id="packaging_area",
                site_id="greenville_demo_site",
                name="Packaging Area",
                description="Packaging area containing Line 2 filling and checkweighing.",
            )
        ],
        equipment=[
            Equipment(
                equipment_id="filler_f_201",
                area_id="packaging_area",
                name="Filler F-201",
                equipment_type="filler",
                criticality="high",
            ),
            Equipment(
                equipment_id="checkweigher_cw_201",
                area_id="packaging_area",
                name="Checkweigher CW-201",
                equipment_type="checkweigher",
                criticality="medium",
            ),
        ],
        process_signals=[
            ProcessSignal(
                signal_id="fill_weight",
                equipment_id="filler_f_201",
                name="Fill Weight",
                unit="g",
                normal_min=495.0,
                normal_max=505.0,
            ),
            ProcessSignal(
                signal_id="filler_nozzle_pressure",
                equipment_id="filler_f_201",
                name="Filler Nozzle Pressure",
                unit="bar",
                normal_min=1.9,
                normal_max=2.6,
            ),
        ],
        batches=[
            Batch(
                batch_id="BATCH-DEMO-1007",
                site_id="greenville_demo_site",
                area_id="packaging_area",
                product_name="OFI Demo Beverage",
                status="held",
                started_at=started_at,
                ended_at=None,
            )
        ],
        quality_results=[
            QualityResult(
                quality_result_id="qr_fill_weight_WO_DEMO_1007",
                batch_id="BATCH-DEMO-1007",
                measurement_name="Final Fill Weight",
                value=505.4,
                unit="g",
                spec_min=495.0,
                spec_max=505.0,
                result="fail",
                related_signal_ids=["fill_weight", "filler_nozzle_pressure"],
                recorded_at=drift_at,
            )
        ],
        deviations=[
            Deviation(
                deviation_id="dev_fill_weight_drift_WO_DEMO_1007",
                batch_id="BATCH-DEMO-1007",
                quality_result_id="qr_fill_weight_WO_DEMO_1007",
                title="Fill weight drift on WO-DEMO-1007 above upper specification",
                severity="medium",
                status="under_investigation",
                related_signal_ids=["fill_weight", "filler_nozzle_pressure"],
                opened_at=drift_at,
            )
        ],
        alerts=[
            Alert(
                alert_id="alert_fill_weight_trend_WO_DEMO_1007",
                deviation_id="dev_fill_weight_drift_WO_DEMO_1007",
                batch_id="BATCH-DEMO-1007",
                signal_id="fill_weight",
                title="Fill weight trend on Filler F-201 approaching upper spec limit",
                severity="medium",
                status="active",
                triggered_at=drift_at,
            )
        ],
        investigations=[
            Investigation(
                investigation_id="inv_fill_weight_drift_WO_DEMO_1007",
                deviation_id="dev_fill_weight_drift_WO_DEMO_1007",
                title="Investigate fill weight drift on WO-DEMO-1007",
                status="open",
                owner="quality_engineer",
                alert_ids=["alert_fill_weight_trend_WO_DEMO_1007"],
                quality_result_ids=["qr_fill_weight_WO_DEMO_1007"],
                related_signal_ids=["fill_weight", "filler_nozzle_pressure"],
                opened_at=drift_at,
            )
        ],
    )


def _get_by_id(items: list, field_name: str, expected_id: str):
    return next((item for item in items if getattr(item, field_name) == expected_id), None)
