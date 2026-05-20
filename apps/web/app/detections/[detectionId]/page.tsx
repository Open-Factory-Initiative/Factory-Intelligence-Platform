import Link from "next/link";

import { ApiErrorPanel } from "../../components/demo-state";
import {
  ApiClientError,
  type Detection,
  type EvidenceItem,
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
          <EvidenceTimeline evidenceItems={result.evidenceItems} />
          <section className="workflow-links" aria-label="Detection workflow sections">
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
    const [detection, evidenceItems] = await Promise.all([
      workbenchApi.getDetection(detectionId),
      workbenchApi.listDetectionEvidence(detectionId),
    ]);

    return {
      detection,
      evidenceItems: sortEvidenceChronologically(evidenceItems),
      ok: true as const,
    };
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

function EvidenceTimeline({ evidenceItems }: { evidenceItems: EvidenceItem[] }) {
  return (
    <section
      className="data-card evidence-timeline"
      id="evidence-timeline"
      aria-labelledby="evidence-timeline-heading"
    >
      <div>
        <span className="demo-label">Simulator-backed evidence</span>
        <h2 id="evidence-timeline-heading">Evidence timeline</h2>
        <p>
          Chronological Process Sentinel evidence from the local demo API. Use
          this to understand why the finding exists before reviewing any
          recommendation.
        </p>
      </div>
      <section className="what-this-means" aria-labelledby="what-this-means-heading">
        <span className="status-label">What this means</span>
        <h3 id="what-this-means-heading">What this means</h3>
        <p>{buildTimelineMeaning(evidenceItems)}</p>
      </section>
      {evidenceItems.length === 0 ? (
        <div className="state-panel">
          <strong>No evidence available</strong>
          <span>
            This detection exists, but the simulator-backed API did not return
            evidence items for it yet.
          </span>
        </div>
      ) : (
        <ol className="timeline-list">
          {evidenceItems.map((item) => (
            <li
              className={`timeline-item ${evidenceTypeClass(item.evidence_type)}`}
              key={item.evidence_id}
            >
              <div className="timeline-marker" aria-hidden="true" />
              <article>
                <div className="timeline-heading">
                  <div>
                    <span className="evidence-type">{formatEnum(item.evidence_type)}</span>
                    <h3>{item.title}</h3>
                  </div>
                  <time dateTime={item.timestamp}>{formatTimestamp(item.timestamp)}</time>
                </div>
                <p>{item.description}</p>
                <dl className="evidence-meta">
                  <div>
                    <dt>Score / relevance</dt>
                    <dd>{Math.round(item.score * 100)}%</dd>
                  </div>
                  <div>
                    <dt>Source event IDs</dt>
                    <dd>{formatSourceEventIds(item.source_event_ids)}</dd>
                  </div>
                </dl>
              </article>
            </li>
          ))}
        </ol>
      )}
    </section>
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

function buildTimelineMeaning(evidenceItems: EvidenceItem[]): string {
  if (evidenceItems.length === 0) {
    return "The detection is present, but there is no supporting timeline evidence available yet in the simulator-backed demo state.";
  }

  const evidenceTypes = [
    ...new Set(evidenceItems.map((item) => formatEnum(item.evidence_type))),
  ];
  return `Process Sentinel found ${evidenceItems.length} supporting evidence item${
    evidenceItems.length === 1 ? "" : "s"
  } across ${evidenceTypes.join(
    ", ",
  )}. Read the timeline from oldest to newest to see how the process and quality context support this advisory finding.`;
}

function sortEvidenceChronologically(evidenceItems: EvidenceItem[]): EvidenceItem[] {
  return [...evidenceItems].sort(
    (left, right) => Date.parse(left.timestamp) - Date.parse(right.timestamp),
  );
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

function formatSourceEventIds(eventIds: string[]): string {
  return eventIds.length > 0 ? eventIds.join(", ") : "No source events linked";
}

function formatEnum(value: string): string {
  return value.replaceAll("_", " ");
}

function evidenceTypeClass(evidenceType: EvidenceItem["evidence_type"]): string {
  return `evidence-${evidenceType.replaceAll("_", "-")}`;
}
