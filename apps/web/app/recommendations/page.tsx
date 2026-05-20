import Link from "next/link";

import { ApiErrorPanel, EmptyState } from "../components/demo-state";
import {
  type Recommendation,
  formatApiError,
  getApiBaseUrl,
  workbenchApi,
} from "../../lib/api-client";
import { RecommendationReviewPanel } from "./recommendation-review-panel";

export const dynamic = "force-dynamic";

type RecommendationsPageProps = {
  searchParams: Promise<{
    detection_id?: string;
  }>;
};

export default async function RecommendationsPage({
  searchParams,
}: RecommendationsPageProps) {
  const { detection_id: detectionId } = await searchParams;
  const result = await loadRecommendation(detectionId);

  return (
    <section className="content-panel">
      <span className="demo-label">Simulator-backed governed recommendation</span>
      <div>
        <h1>Recommendation review</h1>
        <p className="lead">
          Review the advisory Process Sentinel recommendation and record a human
          decision. The demo does not execute industrial writeback.
        </p>
      </div>
      {!result.ok ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok && result.recommendations.length === 0 ? (
        <EmptyState
          text="Run Process Sentinel against the simulator-backed demo state to populate recommendations."
          title="No recommendations returned"
        />
      ) : null}
      {result.ok && result.recommendations.length > 0 && !result.selected ? (
        <EmptyState
          text={`No recommendation is linked to detection ${detectionId}. Return to the detection list and choose a current demo detection.`}
          title="No linked recommendation found"
        />
      ) : null}
      {result.ok && result.selected ? (
        <div className="data-stack">
          <div className="decision-note">
            Recommendations are advisory decision support. A named human reviewer
            must approve, reject, or defer before any high-impact action is
            considered, and this demo records only local simulator state.
          </div>
          <RecommendationReviewPanel initialRecommendation={result.selected} />
          <section className="workflow-links" aria-label="Recommendation workflow links">
            <article className="data-card compact">
              <span className="status-label">Linked detection</span>
              <h2>Detection context</h2>
              <p>
                Return to the detection, evidence timeline, and explanation
                before recording a decision.
              </p>
              <Link
                className="secondary-action"
                href={`/detections/${result.selected.detection_id}`}
              >
                Open detection
              </Link>
            </article>
            <article className="data-card compact">
              <span className="status-label">RCA/CAPA draft</span>
              <h2>RCA/CAPA draft</h2>
              <p>
                Preview draft investigation language after the governed
                recommendation decision is recorded.
              </p>
              <Link
                className="secondary-action"
                href={`/rca-capa-draft?detection_id=${encodeURIComponent(
                  result.selected.detection_id,
                )}`}
              >
                RCA/CAPA draft
              </Link>
            </article>
          </section>
        </div>
      ) : null}
      <div className="api-panel">
        <p>
          Configured API target: <code>{getApiBaseUrl()}</code>
        </p>
      </div>
    </section>
  );
}

async function loadRecommendation(detectionId?: string) {
  try {
    const recommendations = await workbenchApi.listRecommendations();
    if (recommendations.length === 0) {
      return { ok: true as const, recommendations };
    }

    const selectedSummary = selectRecommendation(recommendations, detectionId);
    const selected =
      selectedSummary === undefined
        ? undefined
        : await workbenchApi.getRecommendation(selectedSummary.recommendation_id);

    return { ok: true as const, recommendations, selected };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}

function selectRecommendation(
  recommendations: Recommendation[],
  detectionId?: string,
): Recommendation | undefined {
  if (detectionId !== undefined) {
    return recommendations.find(
      (recommendation) => recommendation.detection_id === detectionId,
    );
  }

  return recommendations[0];
}
