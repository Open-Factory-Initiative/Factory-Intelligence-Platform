import Link from "next/link";

import { ApiErrorPanel } from "./components/demo-state";
import { formatApiError, getApiBaseUrl, workbenchApi } from "../lib/api-client";

export const dynamic = "force-dynamic";

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

export default async function OverviewPage() {
  const health = await loadHealth();

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
            <span className="status-value">{getApiBaseUrl()}</span>
          </div>
          <div className="status-row">
            <span className="status-label">Demo source</span>
            <span className="status-value">
              {health.ok && health.data.simulator_backed
                ? "Synthetic Factory Simulator"
                : "Synthetic Factory Simulator expected"}
            </span>
          </div>
          <div className="status-row">
            <span className="status-label">API health</span>
            <span className="status-value">{health.ok ? health.data.status : "Unavailable"}</span>
          </div>
        </aside>
      </section>

      {!health.ok ? <ApiErrorPanel message={health.message} /> : null}

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

async function loadHealth() {
  try {
    return { data: await workbenchApi.getHealth(), ok: true as const };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}
