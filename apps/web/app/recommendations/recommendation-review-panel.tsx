"use client";

import { type FormEvent, useState } from "react";

import {
  type ApprovalDecision,
  type Recommendation,
  formatApiError,
  workbenchApi,
} from "../../lib/api-client";

type RecommendationReviewPanelProps = {
  initialRecommendation: Recommendation;
};

type DecisionAction = "approve" | "reject" | "defer";

export function RecommendationReviewPanel({
  initialRecommendation,
}: RecommendationReviewPanelProps) {
  const [recommendation, setRecommendation] =
    useState<Recommendation>(initialRecommendation);
  const [reviewer, setReviewer] = useState("");
  const [reason, setReason] = useState("");
  const [decisionResult, setDecisionResult] = useState<ApprovalDecision | null>(
    null,
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [submittingAction, setSubmittingAction] = useState<DecisionAction | null>(
    null,
  );

  const canSubmit =
    reviewer.trim().length > 0 && reason.trim().length > 0 && submittingAction === null;

  async function submitDecision(action: DecisionAction) {
    setSubmittingAction(action);
    setErrorMessage(null);

    try {
      const request = {
        reason: reason.trim(),
        reviewer: reviewer.trim(),
      };
      const result = await recordDecision(action, recommendation.recommendation_id, request);
      const updatedRecommendation = await workbenchApi.getRecommendation(
        recommendation.recommendation_id,
      );

      setDecisionResult(result);
      setRecommendation(updatedRecommendation);
    } catch (error) {
      setErrorMessage(formatApiError(error));
    } finally {
      setSubmittingAction(null);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  return (
    <article className="data-card recommendation-review-panel">
      <div>
        <span className="status-label">Selected recommendation</span>
        <h2>{recommendation.recommended_action}</h2>
      </div>
      <p>{recommendation.rationale}</p>
      <dl className="metric-grid">
        <div>
          <dt>Status</dt>
          <dd>{formatEnum(recommendation.status)}</dd>
        </div>
        <div>
          <dt>Risk level</dt>
          <dd>{formatEnum(recommendation.risk_level)}</dd>
        </div>
        <div>
          <dt>Requires approval</dt>
          <dd>{recommendation.requires_approval ? "Yes" : "No"}</dd>
        </div>
        <div>
          <dt>Linked evidence IDs</dt>
          <dd>{formatEvidenceIds(recommendation.evidence_ids)}</dd>
        </div>
      </dl>
      <form className="review-form" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="reviewer">Reviewer name</label>
          <input
            id="reviewer"
            name="reviewer"
            onChange={(event) => setReviewer(event.target.value)}
            placeholder="quality_engineer"
            type="text"
            value={reviewer}
          />
        </div>
        <div>
          <label htmlFor="reason">Decision reason</label>
          <textarea
            id="reason"
            name="reason"
            onChange={(event) => setReason(event.target.value)}
            placeholder="Evidence supports containment review."
            rows={4}
            value={reason}
          />
        </div>
        <div className="review-actions" aria-label="Recommendation decision actions">
          <button
            disabled={!canSubmit}
            onClick={() => submitDecision("approve")}
            type="button"
          >
            {submittingAction === "approve" ? "Approving..." : "Approve"}
          </button>
          <button
            disabled={!canSubmit}
            onClick={() => submitDecision("reject")}
            type="button"
          >
            {submittingAction === "reject" ? "Rejecting..." : "Reject"}
          </button>
          <button
            disabled={!canSubmit}
            onClick={() => submitDecision("defer")}
            type="button"
          >
            {submittingAction === "defer" ? "Deferring..." : "Defer"}
          </button>
        </div>
      </form>
      {errorMessage !== null ? (
        <div className="state-panel error-panel" role="alert">
          <strong>Decision was not recorded</strong>
          <span>{errorMessage}</span>
        </div>
      ) : null}
      {decisionResult !== null ? (
        <div className="decision-result" role="status">
          <strong>Recorded decision: {formatEnum(decisionResult.decision)}</strong>
          <span>
            {decisionResult.reviewer} recorded this decision at{" "}
            {formatTimestamp(decisionResult.timestamp ?? decisionResult.created_at)}.
          </span>
          <span>Reason: {decisionResult.reason}</span>
          <span>Updated status: {formatEnum(recommendation.status)}</span>
        </div>
      ) : null}
    </article>
  );
}

async function recordDecision(
  action: DecisionAction,
  recommendationId: string,
  request: { reviewer: string; reason: string },
): Promise<ApprovalDecision> {
  if (action === "approve") {
    return workbenchApi.approveRecommendation(recommendationId, request);
  }
  if (action === "reject") {
    return workbenchApi.rejectRecommendation(recommendationId, request);
  }
  return workbenchApi.deferRecommendation(recommendationId, request);
}

function formatEvidenceIds(evidenceIds: string[]): string {
  return evidenceIds.length > 0 ? evidenceIds.join(", ") : "No linked evidence";
}

function formatEnum(value: string): string {
  return value.replaceAll("_", " ");
}

function formatTimestamp(value: string): string {
  return value.replace("T", " ").replace("Z", " UTC");
}
