type ApiErrorPanelProps = {
  message: string;
};

type EmptyStateProps = {
  title: string;
  text: string;
};

type LoadingStateProps = {
  title?: string;
};

type StatusBadgeProps = {
  label?: string;
  tone?:
    | "neutral"
    | "success"
    | "warning"
    | "danger"
    | "info"
    | "draft";
  value: string;
};

export function ApiErrorPanel({ message }: ApiErrorPanelProps) {
  return (
    <div className="state-panel error-panel" role="alert">
      <strong>API connection issue</strong>
      <span>{message}</span>
    </div>
  );
}

export function EmptyState({ title, text }: EmptyStateProps) {
  return (
    <div className="state-panel">
      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}

export function LoadingState({ title = "Loading simulator-backed demo data" }: LoadingStateProps) {
  return (
    <section className="content-panel" aria-busy="true">
      <span className="demo-label">Simulator-backed demo data</span>
      <div className="state-panel">
        <strong>{title}</strong>
        <span>Connecting to the local FastAPI demo backend.</span>
      </div>
    </section>
  );
}

export function StatusBadge({
  label,
  tone = "neutral",
  value,
}: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge-${tone}`}>
      {label ? <span className="status-badge-label">{label}</span> : null}
      <span>{formatBadgeValue(value)}</span>
    </span>
  );
}

function formatBadgeValue(value: string): string {
  return value.replaceAll("_", " ");
}
