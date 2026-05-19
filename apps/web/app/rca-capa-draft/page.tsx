import { apiBaseUrl } from "../../lib/api-config";

export default function RcaCapaDraftPage() {
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
      <ul className="placeholder-list">
        <li>
          <strong>Draft endpoint</strong>
          <span>
            Future UI will read from{" "}
            <code>GET /reports/rca-capa-drafts/det_fill_weight_gradual_drift</code>.
          </span>
        </li>
        <li>
          <strong>Preview fields</strong>
          <span>
            Title, problem statement, evidence summary, containment, CAPA placeholder,
            and human review requirement.
          </span>
        </li>
        <li>
          <strong>Safety boundary</strong>
          <span>No automatic CAPA creation, production validation claim, or external writeback.</span>
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
