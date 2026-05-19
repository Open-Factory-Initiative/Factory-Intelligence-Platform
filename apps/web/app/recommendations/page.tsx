import { apiBaseUrl } from "../../lib/api-config";

export default function RecommendationsPage() {
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
      <ul className="placeholder-list">
        <li>
          <strong>Queue</strong>
          <span>Future UI will read from <code>GET /recommendations</code>.</span>
        </li>
        <li>
          <strong>Review actions</strong>
          <span>
            Future UI will call approve, reject, and defer endpoints with reviewer and
            reason.
          </span>
        </li>
        <li>
          <strong>Decision feedback</strong>
          <span>
            Future UI will display recommendation ID, reviewer, decision, reason, and
            timestamp.
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
