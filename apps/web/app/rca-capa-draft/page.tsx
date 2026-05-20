import Link from "next/link";

import { ApiErrorPanel, EmptyState } from "../components/demo-state";
import {
  ApiClientError,
  type RcaCapaDraft,
  formatApiError,
  getApiBaseUrl,
  workbenchApi,
} from "../../lib/api-client";
import { DraftCopyButton } from "./draft-copy-button";

export const dynamic = "force-dynamic";

type RcaCapaDraftPageProps = {
  searchParams: Promise<{
    detection_id?: string;
  }>;
};

export default async function RcaCapaDraftPage({
  searchParams,
}: RcaCapaDraftPageProps) {
  const { detection_id: detectionId } = await searchParams;
  const result = await loadDraft(detectionId);

  return (
    <section className="content-panel">
      <span className="demo-label">Demo-generated draft</span>
      <div>
        <h1>RCA/CAPA Draft</h1>
        <p className="lead">
          Preview investigation-ready RCA/CAPA draft language for the selected
          simulator-backed Process Sentinel detection. Draft content is human-review
          required and is not automatically submitted to QMS or MES systems.
        </p>
      </div>
      {!result.ok && result.notFound ? (
        <div className="state-panel error-panel" role="alert">
          <strong>Draft not found</strong>
          <span>
            The simulator-backed API did not return an RCA/CAPA draft for{" "}
            <code>{result.detectionId}</code>. Open a current demo detection and
            use its RCA/CAPA draft link.
          </span>
        </div>
      ) : null}
      {!result.ok && !result.notFound ? <ApiErrorPanel message={result.message} /> : null}
      {result.ok && !result.draft ? (
        <EmptyState
          text="Run the demo state setup and Process Sentinel before previewing the draft."
          title="No detection available for draft preview"
        />
      ) : null}
      {result.ok && result.draft ? (
        <div className="data-stack">
          <div className="decision-note">
            This RCA/CAPA draft is generated from demo detection, evidence, and
            recommendation state. It is advisory decision support for human
            review only; it is not a validated production record and it does not
            submit anything to QMS or MES.
          </div>
          <article className="data-card rca-draft-card">
            <div className="draft-heading">
              <div>
                <span className="status-label">Draft preview</span>
                <h2>{result.draft.title}</h2>
              </div>
              <DraftCopyButton draftText={formatDraftForCopy(result.draft)} />
            </div>
            <dl className="metric-grid">
              <div>
                <dt>Detection ID</dt>
                <dd>{result.draft.detection_id}</dd>
              </div>
              <div>
                <dt>Human review</dt>
                <dd>{result.draft.human_review_required ? "Required" : "Not required"}</dd>
              </div>
              <div>
                <dt>System submission</dt>
                <dd>Not submitted to QMS</dd>
              </div>
              <div>
                <dt>Source</dt>
                <dd>Simulator-backed demo state</dd>
              </div>
            </dl>
            <section className="draft-section" aria-labelledby="problem-statement-heading">
              <span className="status-label">Problem statement</span>
              <h3 id="problem-statement-heading">Problem statement</h3>
              <p>{result.draft.problem_statement}</p>
            </section>
            <section className="draft-section" aria-labelledby="evidence-summary-heading">
              <span className="status-label">Evidence summary</span>
              <h3 id="evidence-summary-heading">Evidence summary</h3>
              <ul>
                {result.draft.evidence_summary.map((summary) => (
                  <li key={summary}>{summary}</li>
                ))}
              </ul>
            </section>
            <section
              className="draft-section"
              aria-labelledby="recommended-containment-heading"
            >
              <span className="status-label">Recommended containment</span>
              <h3 id="recommended-containment-heading">Recommended containment</h3>
              <p>{result.draft.recommended_containment}</p>
            </section>
            <section className="draft-section" aria-labelledby="capa-placeholder-heading">
              <span className="status-label">CAPA placeholder</span>
              <h3 id="capa-placeholder-heading">CAPA placeholder</h3>
              <p>{result.draft.capa_placeholder}</p>
            </section>
          </article>
          <section className="workflow-links" aria-label="RCA/CAPA workflow links">
            <article className="data-card compact">
              <span className="status-label">Linked detection</span>
              <h2>Detection detail</h2>
              <p>Return to the detection and evidence timeline that generated this draft.</p>
              <Link
                className="secondary-action"
                href={`/detections/${result.draft.detection_id}`}
              >
                Open detection
              </Link>
            </article>
            <article className="data-card compact">
              <span className="status-label">Governed review</span>
              <h2>Recommendation review</h2>
              <p>Review the governed recommendation before using draft language.</p>
              <Link
                className="secondary-action"
                href={`/recommendations?detection_id=${encodeURIComponent(
                  result.draft.detection_id,
                )}`}
              >
                Open recommendation
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

async function loadDraft(detectionId?: string) {
  try {
    const selectedDetectionId = detectionId ?? (await getFirstDetectionId());
    if (selectedDetectionId === undefined) {
      return { draft: null, ok: true as const };
    }
    const draft = await workbenchApi.getRcaCapaDraft(selectedDetectionId);
    return { draft, ok: true as const };
  } catch (error) {
    return {
      detectionId: detectionId ?? "selected detection",
      message: formatApiError(error),
      notFound: isMissingDraft(error),
      ok: false as const,
    };
  }
}

async function getFirstDetectionId(): Promise<string | undefined> {
  const detections = await workbenchApi.listDetections();
  return detections[0]?.detection_id;
}

function isMissingDraft(error: unknown): boolean {
  return (
    error instanceof ApiClientError &&
    (error.status === 404 || error.code === "detection_not_found")
  );
}

function formatDraftForCopy(draft: RcaCapaDraft): string {
  return [
    draft.title,
    "",
    `Detection ID: ${draft.detection_id}`,
    "Human review required: yes",
    "Demo-generated draft; not submitted to QMS/MES.",
    "",
    "Problem statement",
    draft.problem_statement,
    "",
    "Evidence summary",
    ...draft.evidence_summary.map((summary) => `- ${summary}`),
    "",
    "Recommended containment",
    draft.recommended_containment,
    "",
    "CAPA placeholder",
    draft.capa_placeholder,
  ].join("\n");
}
