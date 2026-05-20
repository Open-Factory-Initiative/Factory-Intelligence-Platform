import Link from "next/link";

import { ApiErrorPanel } from "../../components/demo-state";
import {
  type Detection,
  formatApiError,
  getApiBaseUrl,
  workbenchApi,
} from "../../../lib/api-client";

export const dynamic = "force-dynamic";

type DetectionDetailPageProps = {
  params: Promise<{
    detectionId: string;
  }>;
};

export default async function DetectionDetailPage({ params }: DetectionDetailPageProps) {
  const { detectionId } = await params;
  const result = await loadDetection(detectionId);

  return (
    <section className="content-panel">
      <span className="demo-label">Simulator-backed demo data</span>
      <div>
        <Link className="back-link" href="/detections">
          Back to detections
        </Link>
        <h1>Detection detail</h1>
        <p className="lead">
          Read-only Process Sentinel detection context from the local demo API.
        </p>
      </div>
      {!result.ok ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok ? (
        <article className="data-card">
          <div>
            <span className="status-label">{result.detection.detection_type}</span>
            <h2>{result.detection.summary}</h2>
          </div>
          <dl className="metric-grid">
            <div>
              <dt>Severity</dt>
              <dd>{result.detection.severity}</dd>
            </div>
            <div>
              <dt>Confidence</dt>
              <dd>{Math.round(result.detection.confidence * 100)}%</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{result.detection.status}</dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>{formatTimestamp(result.detection.created_at)}</dd>
            </div>
            <div>
              <dt>Time window</dt>
              <dd>{formatTimeWindow(result.detection)}</dd>
            </div>
            <div>
              <dt>Work order</dt>
              <dd>{result.detection.related_work_order_id ?? "Not linked"}</dd>
            </div>
            <div>
              <dt>Related assets</dt>
              <dd>{formatAssets(result.detection.related_asset_ids)}</dd>
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

async function loadDetection(detectionId: string) {
  try {
    return { detection: await workbenchApi.getDetection(detectionId), ok: true as const };
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
