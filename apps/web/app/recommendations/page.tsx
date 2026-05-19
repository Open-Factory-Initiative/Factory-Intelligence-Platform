import { ApiErrorPanel, EmptyState } from "../components/demo-state";
import { formatApiError, getApiBaseUrl, workbenchApi } from "../../lib/api-client";

export const dynamic = "force-dynamic";

export default async function RecommendationsPage() {
  const result = await loadRecommendations();

  return (
    <section className="content-panel">
      <span className="demo-label">Human-reviewed recommendation placeholder</span>
      <div>
        <h1>Recommendations</h1>
        <p className="lead">
          Placeholder route for the governed recommendation queue. The MVP remains
          advisory and requires a human decision before any high-impact action is
          considered.
        </p>
      </div>
      {!result.ok ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok && result.recommendations.length === 0 ? (
        <EmptyState
          text="Run Process Sentinel against the simulator-backed demo state to populate recommendations."
          title="No recommendations returned"
        />
      ) : null}
      {result.ok && result.selected ? (
        <div className="data-stack">
          <article className="data-card">
            <div>
              <span className="status-label">Selected recommendation</span>
              <h2>{result.selected.recommended_action}</h2>
            </div>
            <p>{result.selected.rationale}</p>
            <dl className="metric-grid">
              <div>
                <dt>Status</dt>
                <dd>{result.selected.status}</dd>
              </div>
              <div>
                <dt>Risk</dt>
                <dd>{result.selected.risk_level}</dd>
              </div>
              <div>
                <dt>Approval</dt>
                <dd>{result.selected.requires_approval ? "Required" : "Not required"}</dd>
              </div>
              <div>
                <dt>Evidence</dt>
                <dd>{result.selected.evidence_ids.length} linked items</dd>
              </div>
            </dl>
          </article>
          <div className="decision-note">
            Approve, reject, and defer API client methods are available for the next
            review-panel issue. This page remains read-only in issue #100.
          </div>
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

async function loadRecommendations() {
  try {
    const recommendations = await workbenchApi.listRecommendations();
    if (recommendations.length === 0) {
      return { ok: true as const, recommendations };
    }
    const selected = await workbenchApi.getRecommendation(recommendations[0].recommendation_id);
    return { ok: true as const, recommendations, selected };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}
