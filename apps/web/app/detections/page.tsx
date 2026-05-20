import Link from "next/link";

import { ApiErrorPanel, EmptyState, StatusBadge } from "../components/demo-state";
import {
  type Detection,
  formatApiError,
  getApiBaseUrl,
  workbenchApi,
} from "../../lib/api-client";

export const dynamic = "force-dynamic";

export default async function DetectionsPage() {
  const result = await loadDetections();

  return (
    <section className="content-panel">
      <span className="demo-label">Simulator-backed demo data</span>
      <div>
        <h1>Detections</h1>
        <p className="lead">
          Process Sentinel detections from the local demo run. Open a detection to
          inspect the current summary and routing context.
        </p>
      </div>
      {!result.ok ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok && result.detections.length === 0 ? (
        <EmptyState
          text="Run make demo-data, make demo-ingest, and make demo-sentinel-run, then start the API to populate this list."
          title="No detections returned"
        />
      ) : null}
      {result.ok && result.detections.length > 0 ? (
        <div className="detection-list" aria-label="Process Sentinel detections">
          {result.detections.map((detection) => (
            <article className="detection-card" key={detection.detection_id}>
              <div className="detection-card-main">
                <div>
                  <span className="status-label">Detection</span>
                  <h2>{detection.summary}</h2>
                </div>
                <dl className="detection-fields">
                  <div>
                    <dt>Severity</dt>
                    <dd>
                      <StatusBadge
                        tone={severityTone(detection.severity)}
                        value={detection.severity}
                      />
                    </dd>
                  </div>
                  <div>
                    <dt>Confidence</dt>
                    <dd>{Math.round(detection.confidence * 100)}%</dd>
                  </div>
                  <div>
                    <dt>Status</dt>
                    <dd>
                      <StatusBadge
                        tone={detectionStatusTone(detection.status)}
                        value={detection.status}
                      />
                    </dd>
                  </div>
                  <div>
                    <dt>Time window</dt>
                    <dd>{formatTimeWindow(detection)}</dd>
                  </div>
                  <div>
                    <dt>Work order</dt>
                    <dd>{detection.related_work_order_id ?? "Not linked"}</dd>
                  </div>
                  <div>
                    <dt>Related assets</dt>
                    <dd>{formatAssets(detection.related_asset_ids)}</dd>
                  </div>
                </dl>
              </div>
              <Link className="secondary-action" href={`/detections/${detection.detection_id}`}>
                Open detection
              </Link>
            </article>
          ))}
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
    return { detections: await workbenchApi.listDetections(), ok: true as const };
  } catch (error) {
    return { message: formatApiError(error), ok: false as const };
  }
}

function formatTimeWindow(detection: Detection): string {
  return `${formatTimestamp(detection.time_window_start)} to ${formatTimestamp(
    detection.time_window_end,
  )}`;
}

function formatTimestamp(value: string): string {
  return value.replace("T", " ").replace("Z", " UTC");
}

function formatAssets(assetIds: string[]): string {
  return assetIds.length > 0 ? assetIds.join(", ") : "No assets linked";
}

function severityTone(severity: Detection["severity"]) {
  if (severity === "high") {
    return "danger";
  }
  if (severity === "medium") {
    return "warning";
  }
  return "success";
}

function detectionStatusTone(status: Detection["status"]) {
  if (status === "closed" || status === "acknowledged") {
    return "success";
  }
  if (status === "false_positive") {
    return "draft";
  }
  return "info";
}
