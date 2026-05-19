import Link from "next/link";

import { apiBaseUrl } from "../lib/api-config";

const routes = [
  {
    href: "/detections",
    title: "Detections",
    text: "Open the Process Sentinel detection placeholder for the demo drift case.",
  },
  {
    href: "/recommendations",
    title: "Recommendations",
    text: "Review where governed approve, reject, and defer workflows will appear.",
  },
  {
    href: "/rca-capa-draft",
    title: "RCA/CAPA Draft",
    text: "Preview the future quality-facing draft output route.",
  },
  {
    href: "/",
    title: "Overview",
    text: "Confirm the local API target and simulator-backed demo framing.",
  },
];

export default function OverviewPage() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="demo-label">Simulator-backed demo data</span>
          <h1>Operations Workbench for the Process Sentinel demo</h1>
          <p className="lead">
            This shell is the first visible UI layer for the manufacturer demo. It
            keeps the scope to placeholder views while making the backend API target,
            demo status, and core workflow routes visible.
          </p>
        </div>
        <aside className="status-panel" aria-label="Demo configuration">
          <div className="status-row">
            <span className="status-label">API base URL</span>
            <span className="status-value">{apiBaseUrl}</span>
          </div>
          <div className="status-row">
            <span className="status-label">Demo source</span>
            <span className="status-value">Synthetic Factory Simulator</span>
          </div>
          <div className="status-row">
            <span className="status-label">Workflow</span>
            <span className="status-value">Detection, evidence, review, draft</span>
          </div>
        </aside>
      </section>

      <section className="content-grid" aria-label="Workbench routes">
        {routes.map((route) => (
          <Link className="route-card" href={route.href} key={route.title}>
            <div>
              <h2>{route.title}</h2>
              <p>{route.text}</p>
            </div>
            <span>Open route</span>
          </Link>
        ))}
      </section>
    </>
  );
}
