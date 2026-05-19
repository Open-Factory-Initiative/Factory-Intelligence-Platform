import { ApiErrorPanel, EmptyState } from "../components/demo-state";
import { formatApiError, getApiBaseUrl, workbenchApi } from "../../lib/api-client";

export const dynamic = "force-dynamic";

export default async function DetectionsPage() {
  const result = await loadDetections();

  return (
    <section className="content-panel">
      <span className="demo-label">Simulator-backed demo data</span>
      <div>
        <h1>Detections</h1>
        <p className="lead">
          Placeholder route for the Process Sentinel detection list and detail view.
          The first demo detection is expected to be{" "}
          <code>det_fill_weight_gradual_drift</code>.
        </p>
      </div>
      {!result.ok ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok && result.detections.length === 0 ? (
        <EmptyState
          text="Run the demo simulator, ingestion, and Process Sentinel commands to populate detections."
          title="No detections returned"
        />
      ) : null}
      {result.ok && result.selected ? (
        <div className="data-stack">
          <article className="data-card">
            <div>
              <span className="status-label">Detection detail</span>
              <h2>{result.selected.summary}</h2>
            </div>
            <dl className="metric-grid">
              <div>
                <dt>Severity</dt>
                <dd>{result.selected.severity}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{result.selected.status}</dd>
              </div>
              <div>
                <dt>Confidence</dt>
                <dd>{Math.round(result.selected.confidence * 100)}%</dd>
              </div>
              <div>
                <dt>Work order</dt>
                <dd>{result.selected.related_work_order_id ?? "Not linked"}</dd>
              </div>
            </dl>
          </article>
          <div className="data-list">
            <h2>Evidence timeline</h2>
            {result.evidence.map((item) => (
              <article className="data-card compact" key={item.evidence_id}>
                <span className="status-label">{item.evidence_type}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <span className="meta-line">
                  {item.timestamp} · score {Math.round(item.score * 100)}%
                </span>
              </article>
            ))}
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

async function loadDetections() {
  try {
    const detections = await workbenchApi.listDetections();
    if (detections.length === 0) {
      return { detections, ok: true as const };
    }
    const selected = await workbenchApi.getDetection(detections[0].detection_id);
    const evidence = await workbenchApi.listDetectionEvidence(selected.detection_id);
    return { detections, evidence, ok: true as const, selected };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}
