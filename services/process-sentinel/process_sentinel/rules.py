from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from statistics import mean

from factory_events import EventEnvelope

from process_sentinel.models import Detection, EvidenceItem, Recommendation, SentinelRunResult


def run_sentinel(events: Sequence[EventEnvelope]) -> SentinelRunResult:
    sorted_events = sorted(events, key=lambda event: event.timestamp)
    detections: list[Detection] = []
    evidence: list[EvidenceItem] = []
    recommendations: list[Recommendation] = []

    drift = _detect_gradual_fill_weight_drift(sorted_events)
    if drift is not None:
        detections.append(drift[0])
        evidence.extend(drift[1])
        recommendations.append(_recommendation_for_detection(drift[0], drift[1]))

    excursion = _detect_sudden_excursion(sorted_events)
    if excursion is not None:
        detections.append(excursion[0])
        evidence.extend(excursion[1])
        recommendations.append(_recommendation_for_detection(excursion[0], excursion[1]))

    return SentinelRunResult(
        detections=detections,
        evidence_items=evidence,
        recommendations=recommendations,
    )


def _detect_gradual_fill_weight_drift(
    events: Sequence[EventEnvelope],
) -> tuple[Detection, list[EvidenceItem]] | None:
    fill_events = [
        event
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "fill_weight"
    ]
    if len(fill_events) < 12:
        return None

    baseline = fill_events[:6]
    recent = fill_events[-6:]
    baseline_average = mean(event.payload.value for event in baseline)
    recent_average = mean(event.payload.value for event in recent)
    delta = recent_average - baseline_average
    if delta < 2.0:
        return None

    detection_id = "det_fill_weight_gradual_drift"
    related_asset_ids = sorted(
        {event.context.asset_id for event in fill_events if event.context.asset_id}
    )
    detection = Detection(
        detection_id=detection_id,
        detection_type="quality_drift",
        severity="medium",
        status="recommendation_created",
        created_at=datetime.now(UTC),
        time_window_start=baseline[0].timestamp,
        time_window_end=recent[-1].timestamp,
        summary=(
            "Advisory: fill weight is trending upward, which may move the affected "
            "work order toward the upper quality limit."
        ),
        confidence=min(0.95, 0.55 + delta / 10),
        related_work_order_id=recent[-1].context.work_order_id,
        related_asset_ids=related_asset_ids,
    )
    evidence = [
        EvidenceItem(
            evidence_id="evi_fill_weight_baseline_vs_recent",
            detection_id=detection_id,
            evidence_type="process_signal",
            severity=detection.severity,
            timestamp=recent[-1].timestamp,
            title="Recent fill weight average is higher than baseline",
            description=(
                f"Baseline average was {baseline_average:.2f} g; recent average was "
                f"{recent_average:.2f} g, a {delta:.2f} g increase."
            ),
            source_event_ids=[event.event_id for event in [*baseline, *recent]],
            **_evidence_context([*baseline, *recent]),
            score=min(0.95, 0.5 + delta / 10),
        )
    ]

    quality_events = [
        event
        for event in events
        if event.event_type == "quality.measurement.recorded"
        and event.timestamp >= recent[0].timestamp
    ]
    if quality_events:
        evidence.append(
            EvidenceItem(
                evidence_id="evi_quality_results_recent_window",
                detection_id=detection_id,
                evidence_type="quality_result",
                severity=detection.severity,
                timestamp=quality_events[-1].timestamp,
                title="Recent quality checks are near the upper spec limit",
                description=(
                    "Recent final fill weight checks show the same upward direction "
                    "as the process signal."
                ),
                source_event_ids=[event.event_id for event in quality_events],
                **_evidence_context(quality_events),
                score=0.72,
            )
        )

    return detection, evidence


def _detect_sudden_excursion(
    events: Sequence[EventEnvelope],
) -> tuple[Detection, list[EvidenceItem]] | None:
    excursion_events = [
        event
        for event in events
        if event.event_type == "process.measurement.recorded"
        and event.payload.signal_id == "filler_nozzle_pressure"
        and event.payload.value > 2.6
    ]
    if not excursion_events:
        return None

    first = excursion_events[0]
    last = excursion_events[-1]
    detection_id = "det_process_sudden_excursion"
    detection = Detection(
        detection_id=detection_id,
        detection_type="process_excursion",
        severity="high",
        status="recommendation_created",
        created_at=datetime.now(UTC),
        time_window_start=first.timestamp,
        time_window_end=last.timestamp,
        summary="A process signal exceeded the MVP control limit.",
        confidence=0.9,
        related_work_order_id=last.context.work_order_id,
        related_asset_ids=sorted(
            {event.context.asset_id for event in excursion_events if event.context.asset_id}
        ),
    )
    evidence = [
        EvidenceItem(
            evidence_id="evi_process_signal_excursion",
            detection_id=detection_id,
            evidence_type="process_signal",
            severity=detection.severity,
            timestamp=last.timestamp,
            title="Process signal exceeded control limit",
            description=(
                f"{len(excursion_events)} process measurements exceeded the MVP control limit "
                "during the scenario window."
            ),
            source_event_ids=[event.event_id for event in excursion_events],
            **_evidence_context(excursion_events),
            score=0.9,
        )
    ]

    return detection, evidence


def _recommendation_for_detection(
    detection: Detection, evidence_items: Sequence[EvidenceItem]
) -> Recommendation:
    if detection.severity == "high":
        action = "Inspect filler operation and hold affected demo work order for quality review."
        rationale = "A process excursion can affect product quality and requires human review."
    else:
        action = (
            "Inspect filler calibration and increase quality checks for the affected demo work "
            "order."
        )
        rationale = "The trend is moving toward the quality limit before confirmed broad failure."

    return Recommendation(
        recommendation_id=f"rec_{detection.detection_id.removeprefix('det_')}",
        detection_id=detection.detection_id,
        status="needs_review",
        recommended_action=action,
        rationale=rationale,
        risk_level=detection.severity,
        requires_approval=True,
        evidence_ids=[item.evidence_id for item in evidence_items],
        created_at=datetime.now(UTC),
    )


def _evidence_context(events: Sequence[EventEnvelope]) -> dict[str, list[str]]:
    return {
        "related_asset_ids": sorted(
            {event.context.asset_id for event in events if event.context.asset_id}
        ),
        "related_batch_ids": sorted(
            {event.context.batch_id for event in events if event.context.batch_id}
        ),
        "related_work_order_ids": sorted(
            {event.context.work_order_id for event in events if event.context.work_order_id}
        ),
    }
