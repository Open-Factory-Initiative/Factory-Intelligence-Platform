import { apiBaseUrl } from "./api-config";

export type HealthResponse = {
  status: string;
  simulator_backed: boolean;
  events_store: string;
  sentinel_state_dir: string;
};

export type Detection = {
  detection_id: string;
  detection_type: "quality_drift" | "process_excursion";
  severity: "low" | "medium" | "high";
  status:
    | "new"
    | "investigating"
    | "recommendation_created"
    | "acknowledged"
    | "closed"
    | "false_positive";
  created_at: string;
  time_window_start: string;
  time_window_end: string;
  summary: string;
  confidence: number;
  related_work_order_id: string | null;
  related_asset_ids: string[];
};

export type EvidenceItem = {
  evidence_id: string;
  detection_id: string;
  evidence_type: "process_signal" | "quality_result" | "correlation_window";
  timestamp: string;
  title: string;
  description: string;
  source_event_ids: string[];
  score: number;
};

export type Recommendation = {
  recommendation_id: string;
  detection_id: string;
  status: "draft" | "proposed" | "needs_review" | "approved" | "rejected" | "deferred";
  recommended_action: string;
  rationale: string;
  risk_level: "low" | "medium" | "high";
  requires_approval: boolean;
  evidence_ids: string[];
  created_at: string;
};

export type RecommendationDecisionRequest = {
  reviewer: string;
  reason: string;
};

export type ApprovalDecision = {
  approval_id: string;
  recommendation_id: string;
  reviewer: string;
  decision: "approved" | "rejected" | "deferred" | "needs_more_evidence";
  reason: string;
  created_at: string;
  timestamp: string;
};

export type RcaCapaDraft = {
  detection_id: string;
  title: string;
  problem_statement: string;
  evidence_summary: string[];
  recommended_containment: string;
  capa_placeholder: string;
  human_review_required: boolean;
};

type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
  };
};

export class ApiClientError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

export const workbenchApi = {
  getHealth: () => requestJson<HealthResponse>("/health"),
  listDetections: () => requestJson<Detection[]>("/sentinel/detections"),
  getDetection: (detectionId: string) =>
    requestJson<Detection>(`/sentinel/detections/${encodeURIComponent(detectionId)}`),
  listDetectionEvidence: (detectionId: string) =>
    requestJson<EvidenceItem[]>(
      `/sentinel/detections/${encodeURIComponent(detectionId)}/evidence`,
    ),
  listRecommendations: () => requestJson<Recommendation[]>("/recommendations"),
  getRecommendation: (recommendationId: string) =>
    requestJson<Recommendation>(`/recommendations/${encodeURIComponent(recommendationId)}`),
  approveRecommendation: (recommendationId: string, request: RecommendationDecisionRequest) =>
    postDecision(recommendationId, "approve", request),
  rejectRecommendation: (recommendationId: string, request: RecommendationDecisionRequest) =>
    postDecision(recommendationId, "reject", request),
  deferRecommendation: (recommendationId: string, request: RecommendationDecisionRequest) =>
    postDecision(recommendationId, "defer", request),
  getRcaCapaDraft: (detectionId: string) =>
    requestJson<RcaCapaDraft>(
      `/reports/rca-capa-drafts/${encodeURIComponent(detectionId)}`,
    ),
};

export function getApiBaseUrl(): string {
  return apiBaseUrl;
}

export function formatApiError(error: unknown): string {
  if (error instanceof ApiClientError) {
    const status = error.status ? ` (${error.status})` : "";
    return `${error.message}${status}`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "The API request failed.";
}

function postDecision(
  recommendationId: string,
  decision: "approve" | "reject" | "defer",
  request: RecommendationDecisionRequest,
): Promise<ApprovalDecision> {
  return requestJson<ApprovalDecision>(
    `/recommendations/${encodeURIComponent(recommendationId)}/${decision}`,
    {
      body: JSON.stringify(request),
      method: "POST",
    },
  );
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      accept: "application/json",
      ...(init.body ? { "content-type": "application/json" } : {}),
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw await buildApiError(response);
  }

  return (await response.json()) as T;
}

async function buildApiError(response: Response): Promise<ApiClientError> {
  const fallback = `API request failed for ${response.url}`;

  try {
    const body = (await response.json()) as ApiErrorBody;
    const message = body.error?.message ?? fallback;
    return new ApiClientError(message, response.status, body.error?.code);
  } catch {
    return new ApiClientError(fallback, response.status);
  }
}
