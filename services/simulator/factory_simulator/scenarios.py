from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ScenarioType = Literal["normal", "gradual_drift", "sudden_excursion", "noisy_sensor"]
ScenarioName = Literal["normal", "gradual_drift", "sudden_excursion", "fill_weight_drift_demo"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScenarioMetadata(StrictModel):
    name: ScenarioName
    scenario_type: ScenarioType
    description: str = Field(min_length=1)
    default_seed: int = Field(ge=0)
    default_count: int = Field(ge=6)
    duration_minutes: int = Field(ge=6)


class ScenarioLineContext(StrictModel):
    site_id: str = Field(min_length=1)
    area_id: str = Field(min_length=1)
    line_id: str = Field(min_length=1)
    work_order_id: str = Field(min_length=1)
    batch_id: str | None = None


class ScenarioProduct(StrictModel):
    product_id: str = Field(min_length=1)
    product_name: str = Field(min_length=1)


class ScenarioAsset(StrictModel):
    asset_id: str = Field(min_length=1)
    asset_name: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)


class ScenarioProcessTag(StrictModel):
    signal_id: str = Field(min_length=1)
    signal_name: str = Field(min_length=1)
    asset_id: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    baseline_value: float
    normal_min: float | None = None
    normal_max: float | None = None
    target_value: float | None = None
    drift_per_step: float | None = None
    excursion_value: float | None = None
    noise_band: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_normal_range(self) -> ScenarioProcessTag:
        if self.normal_min is None and self.normal_max is None:
            return self
        if self.normal_min is None or self.normal_max is None:
            msg = "normal_min and normal_max must be provided together"
            raise ValueError(msg)
        if self.normal_min >= self.normal_max:
            msg = "normal_min must be less than normal_max"
            raise ValueError(msg)
        return self


class ScenarioQualityMarker(StrictModel):
    measurement_name: str = Field(min_length=1)
    asset_id: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    spec_min: float
    spec_max: float
    every_n_samples: int = Field(ge=1)
    severity_on_fail: Literal["low", "medium", "high", "critical"]

    @model_validator(mode="after")
    def validate_spec_range(self) -> ScenarioQualityMarker:
        if self.spec_min >= self.spec_max:
            msg = "spec_min must be less than spec_max"
            raise ValueError(msg)
        return self


class ScenarioOutputSettings(StrictModel):
    format: Literal["jsonl"] = "jsonl"
    default_path: str = Field(min_length=1)


class ScenarioDefinition(StrictModel):
    metadata: ScenarioMetadata
    line_context: ScenarioLineContext
    product: ScenarioProduct
    assets: tuple[ScenarioAsset, ...] = Field(min_length=1)
    process_tags: tuple[ScenarioProcessTag, ...] = Field(min_length=1)
    quality_markers: tuple[ScenarioQualityMarker, ...] = Field(min_length=1)
    output: ScenarioOutputSettings

    @model_validator(mode="after")
    def validate_asset_references(self) -> ScenarioDefinition:
        asset_ids = {asset.asset_id for asset in self.assets}
        referenced_asset_ids = {
            *{tag.asset_id for tag in self.process_tags},
            *{marker.asset_id for marker in self.quality_markers},
        }
        missing_asset_ids = sorted(referenced_asset_ids - asset_ids)
        if missing_asset_ids:
            msg = f"scenario references unknown asset ids: {', '.join(missing_asset_ids)}"
            raise ValueError(msg)
        return self


DEMO_LINE_CONTEXT = ScenarioLineContext(
    site_id="site_demo",
    area_id="area_packaging",
    line_id="line_1",
    work_order_id="wo_1001",
)

DEMO_PRODUCT = ScenarioProduct(
    product_id="prod_demo_tablets",
    product_name="Demo Tablets",
)

DEMO_ASSETS = (
    ScenarioAsset(
        asset_id="asset_filler_1",
        asset_name="Filler 1",
        asset_type="filler",
    ),
    ScenarioAsset(
        asset_id="asset_checkweigher_1",
        asset_name="Checkweigher 1",
        asset_type="checkweigher",
    ),
    ScenarioAsset(
        asset_id="asset_case_packer_1",
        asset_name="Case Packer 1",
        asset_type="case_packer",
    ),
)

FILL_WEIGHT_DEMO_CONTEXT = ScenarioLineContext(
    site_id="site_demo",
    area_id="area_packaging",
    line_id="line_1",
    work_order_id="wo_demo_fill_weight_1001",
)

FILL_WEIGHT_DEMO_PRODUCT = ScenarioProduct(
    product_id="prod_demo_oral_solution",
    product_name="Demo Oral Solution",
)

FILL_WEIGHT_DEMO_ASSETS = (
    ScenarioAsset(
        asset_id="asset_filler_1",
        asset_name="Filler 1",
        asset_type="filler",
    ),
)

DEMO_PROCESS_TAGS = (
    ScenarioProcessTag(
        signal_id="fill_weight",
        signal_name="Fill Weight",
        asset_id="asset_filler_1",
        unit="g",
        baseline_value=500.0,
        normal_min=495.0,
        normal_max=505.0,
        target_value=500.0,
        noise_band=0.25,
    ),
    ScenarioProcessTag(
        signal_id="filler_nozzle_pressure",
        signal_name="Filler Nozzle Pressure",
        asset_id="asset_filler_1",
        unit="bar",
        baseline_value=2.1,
        normal_min=1.9,
        normal_max=2.4,
        target_value=2.1,
        noise_band=0.04,
    ),
)

DEMO_QUALITY_MARKERS = (
    ScenarioQualityMarker(
        measurement_name="Final Fill Weight",
        asset_id="asset_checkweigher_1",
        unit="g",
        spec_min=495.0,
        spec_max=505.0,
        every_n_samples=3,
        severity_on_fail="high",
    ),
)

SCENARIO_DEFINITIONS: dict[ScenarioName, ScenarioDefinition] = {
    "normal": ScenarioDefinition(
        metadata=ScenarioMetadata(
            name="normal",
            scenario_type="normal",
            description="Stable demo operation with process and quality values inside limits.",
            default_seed=42,
            default_count=24,
            duration_minutes=24,
        ),
        line_context=DEMO_LINE_CONTEXT,
        product=DEMO_PRODUCT,
        assets=DEMO_ASSETS,
        process_tags=DEMO_PROCESS_TAGS,
        quality_markers=DEMO_QUALITY_MARKERS,
        output=ScenarioOutputSettings(default_path=".local/events/normal.jsonl"),
    ),
    "gradual_drift": ScenarioDefinition(
        metadata=ScenarioMetadata(
            name="gradual_drift",
            scenario_type="gradual_drift",
            description="Fill weight and nozzle pressure drift upward after a stable baseline.",
            default_seed=42,
            default_count=24,
            duration_minutes=24,
        ),
        line_context=DEMO_LINE_CONTEXT,
        product=DEMO_PRODUCT,
        assets=DEMO_ASSETS,
        process_tags=(
            DEMO_PROCESS_TAGS[0].model_copy(update={"drift_per_step": 0.33}),
            DEMO_PROCESS_TAGS[1].model_copy(update={"drift_per_step": 0.025}),
        ),
        quality_markers=DEMO_QUALITY_MARKERS,
        output=ScenarioOutputSettings(default_path=".local/events/gradual_drift.jsonl"),
    ),
    "sudden_excursion": ScenarioDefinition(
        metadata=ScenarioMetadata(
            name="sudden_excursion",
            scenario_type="sudden_excursion",
            description="A short process excursion creates an out-of-spec quality result.",
            default_seed=42,
            default_count=24,
            duration_minutes=24,
        ),
        line_context=DEMO_LINE_CONTEXT,
        product=DEMO_PRODUCT,
        assets=DEMO_ASSETS,
        process_tags=(
            DEMO_PROCESS_TAGS[0].model_copy(update={"excursion_value": 509.5}),
            DEMO_PROCESS_TAGS[1].model_copy(update={"excursion_value": 2.8}),
        ),
        quality_markers=DEMO_QUALITY_MARKERS,
        output=ScenarioOutputSettings(default_path=".local/events/sudden_excursion.jsonl"),
    ),
    "fill_weight_drift_demo": ScenarioDefinition(
        metadata=ScenarioMetadata(
            name="fill_weight_drift_demo",
            scenario_type="gradual_drift",
            description=(
                "Manufacturer demo story: a single filler line runs one demo product and work "
                "order, then fill weight drifts upward before a delayed quality concern."
            ),
            default_seed=120,
            default_count=30,
            duration_minutes=30,
        ),
        line_context=FILL_WEIGHT_DEMO_CONTEXT,
        product=FILL_WEIGHT_DEMO_PRODUCT,
        assets=FILL_WEIGHT_DEMO_ASSETS,
        process_tags=(
            DEMO_PROCESS_TAGS[0].model_copy(update={"drift_per_step": 0.33}),
            DEMO_PROCESS_TAGS[1].model_copy(update={"drift_per_step": 0.01}),
        ),
        quality_markers=(
            DEMO_QUALITY_MARKERS[0].model_copy(update={"asset_id": "asset_filler_1"}),
        ),
        output=ScenarioOutputSettings(default_path=".local/events/fill_weight_drift_demo.jsonl"),
    ),
}

SCENARIOS: tuple[ScenarioName, ...] = tuple(SCENARIO_DEFINITIONS)
SUPPORTED_SCENARIO_TYPES: tuple[ScenarioType, ...] = (
    "normal",
    "gradual_drift",
    "sudden_excursion",
    "noisy_sensor",
)


def scenario_definition_for(name: str) -> ScenarioDefinition:
    definition = SCENARIO_DEFINITIONS.get(name)
    if definition is None:
        msg = f"unsupported scenario: {name}"
        raise ValueError(msg)
    return definition
