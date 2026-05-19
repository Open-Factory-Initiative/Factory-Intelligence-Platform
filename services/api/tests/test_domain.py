from __future__ import annotations

import pytest
from factory_api.domain import ProcessSignal, build_demo_domain_data
from pydantic import ValidationError


def test_demo_domain_links_process_signals_to_quality_and_investigation() -> None:
    domain = build_demo_domain_data()

    site = domain.get_site("greenville_demo_site")
    area = domain.get_area("packaging_area")
    filler = domain.get_equipment("filler_f_201")
    checkweigher = domain.get_equipment("checkweigher_cw_201")
    quality_result = domain.get_quality_result("qr_fill_weight_WO_DEMO_1007")
    deviation = domain.get_deviation("dev_fill_weight_drift_WO_DEMO_1007")
    investigation = domain.get_investigation_detail("inv_fill_weight_drift_WO_DEMO_1007")

    assert site is not None
    assert site.name == "Greenville Demo Site"
    assert area is not None
    assert area.name == "Packaging Area"
    assert filler is not None
    assert filler.name == "Filler F-201"
    assert checkweigher is not None
    assert checkweigher.name == "Checkweigher CW-201"
    assert quality_result is not None
    assert quality_result.batch_id == "BATCH-DEMO-1007"
    assert quality_result.related_signal_ids == ["fill_weight", "filler_nozzle_pressure"]
    assert deviation is not None
    assert deviation.quality_result_id == quality_result.quality_result_id
    assert investigation is not None
    assert investigation.deviation.deviation_id == deviation.deviation_id
    assert [signal.signal_id for signal in investigation.process_signals] == [
        "fill_weight",
        "filler_nozzle_pressure",
    ]


def test_process_signal_requires_valid_normal_range() -> None:
    with pytest.raises(ValidationError, match="normal_min"):
        ProcessSignal(
            signal_id="invalid_signal",
            equipment_id="filler_f_201",
            name="Invalid Signal",
            unit="g",
            normal_min=10.0,
            normal_max=10.0,
        )
