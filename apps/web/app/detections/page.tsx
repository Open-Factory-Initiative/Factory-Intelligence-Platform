import { apiBaseUrl } from "../../lib/api-config";

export default function DetectionsPage() {
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
      <ul className="placeholder-list">
        <li>
          <strong>Detection list</strong>
          <span>
            Future UI will read from <code>GET /sentinel/detections</code>.
          </span>
        </li>
        <li>
          <strong>Detection detail</strong>
          <span>
            Future UI will show severity, confidence, related work order, and affected
            assets.
          </span>
        </li>
        <li>
          <strong>Evidence timeline</strong>
          <span>
            Future UI will follow <code>docs/EVIDENCE_TIMELINE_API_CONTRACT.md</code>.
          </span>
        </li>
      </ul>
      <div className="api-panel">
        <p>
          Configured API target: <code>{apiBaseUrl}</code>
        </p>
      </div>
    </section>
  );
}
