from __future__ import annotations

import json
from pathlib import Path

from process_sentinel.models import (
    ApprovalDecision,
    AuditEvent,
    Detection,
    EvidenceItem,
    RcaCapaDraft,
    Recommendation,
    SentinelRunResult,
)


class SentinelStateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_run_result(self, result: SentinelRunResult) -> None:
        self._write_models("detections.json", result.detections)
        self._write_models("evidence.json", result.evidence_items)
        self._write_models("recommendations.json", result.recommendations)
        for filename in ("approval_decisions.json", "audit_events.json"):
            path = self.state_dir / filename
            if not path.exists():
                path.write_text("[]\n", encoding="utf-8")

    def list_detections(self) -> list[Detection]:
        return self._read_models("detections.json", Detection)

    def get_detection(self, detection_id: str) -> Detection | None:
        return next(
            (
                detection
                for detection in self.list_detections()
                if detection.detection_id == detection_id
            ),
            None,
        )

    def list_evidence(self, detection_id: str | None = None) -> list[EvidenceItem]:
        evidence = self._read_models("evidence.json", EvidenceItem)
        if detection_id is not None:
            evidence = [item for item in evidence if item.detection_id == detection_id]
        return sorted(evidence, key=lambda item: item.timestamp)

    def list_recommendations(self) -> list[Recommendation]:
        return self._read_models("recommendations.json", Recommendation)

    def get_recommendation(self, recommendation_id: str) -> Recommendation | None:
        return next(
            (
                recommendation
                for recommendation in self.list_recommendations()
                if recommendation.recommendation_id == recommendation_id
            ),
            None,
        )

    def record_decision(
        self, *, recommendation_id: str, decision: str, reviewer: str, reason: str
    ) -> ApprovalDecision:
        from datetime import UTC, datetime

        recommendations = self.list_recommendations()
        recommendation = next(
            (item for item in recommendations if item.recommendation_id == recommendation_id), None
        )
        if recommendation is None:
            msg = f"recommendation not found: {recommendation_id}"
            raise KeyError(msg)

        now = datetime.now(UTC)
        updated = recommendation.model_copy(update={"status": decision})
        recommendations = [
            updated if item.recommendation_id == recommendation_id else item
            for item in recommendations
        ]
        self._write_models("recommendations.json", recommendations)

        approval = ApprovalDecision(
            approval_id=f"apr_{recommendation_id}_{decision}",
            recommendation_id=recommendation_id,
            reviewer=reviewer,
            decision=decision,
            reason=reason,
            created_at=now,
        )
        approvals = self._read_models("approval_decisions.json", ApprovalDecision)
        approvals.append(approval)
        self._write_models("approval_decisions.json", approvals)

        audit_event = AuditEvent(
            audit_event_id=f"aud_{recommendation_id}_{decision}",
            timestamp=now,
            actor=reviewer,
            action=f"recommendation.{decision}",
            entity_type="recommendation",
            entity_id=recommendation_id,
            details={
                "reason": reason,
                "previous_status": recommendation.status,
                "new_status": decision,
            },
        )
        audit_events = self._read_models("audit_events.json", AuditEvent)
        audit_events.append(audit_event)
        self._write_models("audit_events.json", audit_events)
        return approval

    def build_rca_capa_draft(self, detection_id: str) -> RcaCapaDraft | None:
        detection = self.get_detection(detection_id)
        if detection is None:
            return None
        evidence_items = self.list_evidence(detection_id)
        recommendation = next(
            (
                item
                for item in self.list_recommendations()
                if item.detection_id == detection.detection_id
            ),
            None,
        )
        return RcaCapaDraft(
            detection_id=detection.detection_id,
            title=f"RCA/CAPA draft for {detection.summary}",
            problem_statement=detection.summary,
            evidence_summary=[item.description for item in evidence_items],
            recommended_containment=(
                recommendation.recommended_action
                if recommendation is not None
                else "No recommendation has been generated."
            ),
            capa_placeholder=(
                "Document root cause, corrective action, preventive action, owner, and due date "
                "after human investigation."
            ),
            human_review_required=True,
        )

    def _write_models(self, filename: str, models: list) -> None:
        path = self.state_dir / filename
        path.write_text(
            json.dumps(
                [model.model_dump(mode="json") for model in models],
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    def _read_models(self, filename: str, model_type):
        path = self.state_dir / filename
        if not path.exists():
            return []
        return [
            model_type.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))
        ]
