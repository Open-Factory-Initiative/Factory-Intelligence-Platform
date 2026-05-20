import Link from "next/link";

import { ApiErrorPanel } from "../../components/demo-state";
import {
  ApiClientError,
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
      {!result.ok && result.notFound ? (
        <div className="state-panel error-panel" role="alert">
          <strong>Detection not found</strong>
          <span>
            The simulator-backed demo API did not return a detection for{" "}
            <code>{detectionId}</code>. Open the detection list and choose a
            current demo detection.
          </span>
        </div>
      ) : null}
      {!result.ok && !result.notFound ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok ? (
        <div className="data-stack">
          <article className="data-card">
            <div>
              <span className="status-label">Detection summary</span>
              <h2>{result.detection.summary}</h2>
            </div>
            <dl className="metric-grid">
              <div>
                <dt>Detection type</dt>
                <dd>{formatEnum(result.detection.detection_type)}</dd>
              </div>
              <div>
                <dt>Severity</dt>
                <dd>{formatEnum(result.detection.severity)}</dd>
              </div>
              <div>
                <dt>Confidence</dt>
                <dd>{Math.round(result.detection.confidence * 100)}%</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{formatEnum(result.detection.status)}</dd>
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
          <section className="data-card compact" aria-labelledby="why-flagged-heading">
            <span className="status-label">Why this was flagged</span>
            <h2 id="why-flagged-heading">Why this was flagged</h2>
            <p>{buildFlagExplanation(result.detection)}</p>
          </section>
          <section className="workflow-links" aria-label="Detection workflow sections">
            <article className="data-card compact" id="evidence-timeline">
              <span className="status-label">Evidence timeline</span>
              <h2>Evidence timeline</h2>
              <p>
                Review the process and quality signals that support this
                finding before acting on any recommendation.
              </p>
              <Link
                className="secondary-action"
                href={`/detections/${result.detection.detection_id}#evidence-timeline`}
              >
                Evidence timeline
              </Link>
            </article>
            <article className="data-card compact">
              <span className="status-label">Recommendation review</span>
              <h2>Recommendation review</h2>
              <p>
                Continue to the governed recommendation queue for human review,
                approval, rejection, or deferral.
              </p>
              <Link className="secondary-action" href="/recommendations">
                Recommendation review
              </Link>
            </article>
            <article className="data-card compact">
              <span className="status-label">RCA/CAPA draft</span>
              <h2>RCA/CAPA draft</h2>
              <p>
                Preview the human-reviewed RCA/CAPA draft language generated
                from the selected simulator-backed detection.
              </p>
              <Link className="secondary-action" href="/rca-capa-draft">
                RCA/CAPA draft
              </Link>
            </article>
          </section>
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

async function loadDetection(detectionId: string) {
  try {
    return { detection: await workbenchApi.getDetection(detectionId), ok: true as const };
  } catch (error) {
    return {
      message: formatApiError(error),
      notFound: isMissingDetection(error),
      ok: false as const,
    };
  }
}

function isMissingDetection(error: unknown): boolean {
  return (
    error instanceof ApiClientError &&
    (error.status === 404 || error.code === "detection_not_found")
  );
}

function buildFlagExplanation(detection: Detection): string {
  const typeContext =
    detection.detection_type === "quality_drift"
      ? "Process Sentinel saw a quality trend move away from the expected demo baseline"
      : "Process Sentinel saw a process signal move outside the expected demo operating range";
  const assetContext =
    detection.related_asset_ids.length > 0
      ? ` for ${formatAssets(detection.related_asset_ids)}`
      : "";
  const workOrderContext = detection.related_work_order_id
    ? ` during work order ${detection.related_work_order_id}`
    : "";

  return `${typeContext}${assetContext}${workOrderContext}. It is marked ${formatEnum(
    detection.severity,
  )} severity with ${Math.round(
    detection.confidence * 100,
  )}% confidence over ${formatTimeWindow(
    detection,
  )}. This is advisory simulator-backed context for human review, not an autonomous action.`;
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

function formatEnum(value: string): string {
  return value.replaceAll("_", " ");
}
