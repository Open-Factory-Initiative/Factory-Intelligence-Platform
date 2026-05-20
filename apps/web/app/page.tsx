import Link from "next/link";

import { ApiErrorPanel } from "./components/demo-state";
import {
  type Area,
  type Batch,
  type Detection,
  type Equipment,
  type Recommendation,
  type Site,
  formatApiError,
  getApiBaseUrl,
  workbenchApi,
} from "../lib/api-client";

export const dynamic = "force-dynamic";

const activeDetectionStatuses = new Set<Detection["status"]>([
  "new",
  "investigating",
  "recommendation_created",
  "acknowledged",
]);

const pendingRecommendationStatuses = new Set<Recommendation["status"]>([
  "draft",
  "proposed",
  "needs_review",
]);

export default async function OverviewPage() {
  const overview = await loadOverview();

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="demo-label">Simulator-backed demo data</span>
          <h1>{overview.ok ? overview.context.siteName : "Operations Workbench"}</h1>
          <p className="lead">
            {overview.ok
              ? overview.context.siteDescription
              : "The manufacturer demo overview needs the local FastAPI backend to show current factory context."}
          </p>
          <div className="hero-actions">
            <Link className="primary-action" href="/detections">
              Open detection
            </Link>
          </div>
        </div>
        <aside className="status-panel" aria-label="Demo configuration">
          <div className="status-row">
            <span className="status-label">API base URL</span>
            <span className="status-value">{getApiBaseUrl()}</span>
          </div>
          <div className="status-row">
            <span className="status-label">Demo source</span>
            <span className="status-value">
              {overview.ok && overview.health.simulator_backed
                ? "Synthetic Factory Simulator"
                : "Synthetic Factory Simulator expected"}
            </span>
          </div>
          <div className="status-row">
            <span className="status-label">API health</span>
            <span className="status-value">
              {overview.ok ? overview.health.status : "Unavailable"}
            </span>
          </div>
        </aside>
      </section>

      {!overview.ok ? <ApiErrorPanel message={overview.message} /> : null}

      {overview.ok ? (
        <section className="overview-grid" aria-label="Factory demo overview">
          <article className="overview-panel context-panel">
            <span className="status-label">Current demo context</span>
            <h2>{overview.context.areaName}</h2>
            <dl className="context-list">
              <div>
                <dt>Line</dt>
                <dd>{overview.context.lineDescription}</dd>
              </div>
              <div>
                <dt>Asset</dt>
                <dd>{overview.context.assetName}</dd>
              </div>
              <div>
                <dt>Work order</dt>
                <dd>{overview.context.workOrderId}</dd>
              </div>
              <div>
                <dt>Product</dt>
                <dd>{overview.context.productName}</dd>
              </div>
            </dl>
          </article>

          <div className="overview-metrics" aria-label="Demo counts">
            <article className="metric-card">
              <span className="status-label">Active detections</span>
              <strong>{overview.activeDetections.length}</strong>
              <p>Open Process Sentinel cases from simulator-backed data.</p>
            </article>
            <article className="metric-card">
              <span className="status-label">Pending recommendations</span>
              <strong>{overview.pendingRecommendations.length}</strong>
              <p>Human-reviewed recommendations awaiting a demo decision.</p>
            </article>
          </div>

          <article className="overview-panel detection-panel">
            <div>
              <span className="status-label">Most important detection</span>
              {overview.importantDetection ? (
                <>
                  <h2>{overview.importantDetection.summary}</h2>
                  <p>
                    Severity {overview.importantDetection.severity}; confidence{" "}
                    {Math.round(overview.importantDetection.confidence * 100)}%.
                  </p>
                </>
              ) : (
                <>
                  <h2>No active detections</h2>
                  <p>Run the demo simulator and Process Sentinel to populate this panel.</p>
                </>
              )}
            </div>
            <Link className="secondary-action" href="/detections">
              Open detection
            </Link>
          </article>
        </section>
      ) : null}
    </>
  );
}

async function loadOverview() {
  try {
    const [health, sites, areas, equipment, batches, detections, recommendations] =
      await Promise.all([
        workbenchApi.getHealth(),
        workbenchApi.listSites(),
        workbenchApi.listAreas(),
        workbenchApi.listEquipment(),
        workbenchApi.listBatches(),
        workbenchApi.listDetections(),
        workbenchApi.listRecommendations(),
      ]);
    const activeDetections = detections.filter((detection) =>
      activeDetectionStatuses.has(detection.status),
    );
    const pendingRecommendations = recommendations.filter((recommendation) =>
      pendingRecommendationStatuses.has(recommendation.status),
    );
    const importantDetection = selectImportantDetection(activeDetections);

    return {
      activeDetections,
      context: buildOverviewContext({ areas, batches, equipment, importantDetection, sites }),
      health,
      importantDetection,
      ok: true as const,
      pendingRecommendations,
    };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}

function selectImportantDetection(detections: Detection[]): Detection | null {
  const severityRank: Record<Detection["severity"], number> = {
    high: 3,
    medium: 2,
    low: 1,
  };

  return (
    [...detections].sort((left, right) => {
      const severityDelta = severityRank[right.severity] - severityRank[left.severity];
      if (severityDelta !== 0) {
        return severityDelta;
      }
      return right.confidence - left.confidence;
    })[0] ?? null
  );
}

function buildOverviewContext({
  areas,
  batches,
  equipment,
  importantDetection,
  sites,
}: {
  areas: Area[];
  batches: Batch[];
  equipment: Equipment[];
  importantDetection: Detection | null;
  sites: Site[];
}) {
  const currentBatch =
    batches.find((batch) => batch.status === "running" || batch.status === "held") ?? batches[0];
  const relatedAsset = importantDetection?.related_asset_ids[0];
  const currentEquipment =
    equipment.find((asset) => asset.equipment_id === relatedAsset) ?? equipment[0];
  const currentArea =
    areas.find((area) => area.area_id === currentEquipment?.area_id) ??
    areas.find((area) => area.area_id === currentBatch?.area_id) ??
    areas[0];
  const currentSite =
    sites.find((site) => site.site_id === currentArea?.site_id) ??
    sites.find((site) => site.site_id === currentBatch?.site_id) ??
    sites[0];

  return {
    areaName: currentArea?.name ?? "Demo production area",
    assetName: currentEquipment?.name ?? "Demo asset unavailable",
    lineDescription: currentArea?.description ?? "Demo line context unavailable",
    productName: currentBatch?.product_name ?? "Demo product unavailable",
    siteDescription:
      currentSite?.description ??
      "Simulator-backed site context will appear when the local FastAPI backend is available.",
    siteName: currentSite?.name ?? "Factory Intelligence Platform demo",
    workOrderId: importantDetection?.related_work_order_id ?? "Demo work order unavailable",
  };
}
