import { ApiErrorPanel, EmptyState } from "../components/demo-state";
import { formatApiError, getApiBaseUrl, workbenchApi } from "../../lib/api-client";

export const dynamic = "force-dynamic";

export default async function RcaCapaDraftPage() {
  const result = await loadDraft();

  return (
    <section className="content-panel">
      <span className="demo-label">Human review required</span>
      <div>
        <h1>RCA/CAPA Draft</h1>
        <p className="lead">
          Placeholder route for the quality-facing draft preview. Draft content is
          decision support only and does not create a CAPA or write to QMS/MES systems.
        </p>
      </div>
      {!result.ok ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok && !result.draft ? (
        <EmptyState
          text="Run the demo state setup and Process Sentinel before previewing the draft."
          title="No detection available for draft preview"
        />
      ) : null}
      {result.ok && result.draft ? (
        <article className="data-card">
          <div>
            <span className="status-label">Draft preview</span>
            <h2>{result.draft.title}</h2>
          </div>
          <p>{result.draft.problem_statement}</p>
          <div className="data-list">
            <h3>Evidence summary</h3>
            <ul>
              {result.draft.evidence_summary.map((summary) => (
                <li key={summary}>{summary}</li>
              ))}
            </ul>
          </div>
          <dl className="metric-grid">
            <div>
              <dt>Containment</dt>
              <dd>{result.draft.recommended_containment}</dd>
            </div>
            <div>
              <dt>CAPA placeholder</dt>
              <dd>{result.draft.capa_placeholder}</dd>
            </div>
            <div>
              <dt>Human review</dt>
              <dd>{result.draft.human_review_required ? "Required" : "Not required"}</dd>
            </div>
          </dl>
        </article>
      ) : null}
      <div className="api-panel">
        <p>
          Configured API target: <code>{getApiBaseUrl()}</code>
        </p>
      </div>
    </section>
  );
}

async function loadDraft() {
  try {
    const detections = await workbenchApi.listDetections();
    if (detections.length === 0) {
      return { draft: null, ok: true as const };
    }
    const draft = await workbenchApi.getRcaCapaDraft(detections[0].detection_id);
    return { draft, ok: true as const };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}
