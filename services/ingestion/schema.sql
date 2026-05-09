create table if not exists factory_events (
    event_id text primary key,
    event_type text not null,
    schema_version text not null,
    event_timestamp timestamptz not null,
    trace_id text not null,
    simulated boolean not null,
    event_body jsonb not null,
    ingested_at timestamptz not null default now()
);

create index if not exists factory_events_type_timestamp_idx
    on factory_events (event_type, event_timestamp desc);

create table if not exists detections (
    detection_id text primary key,
    detection_type text not null,
    severity text not null,
    status text not null,
    created_at timestamptz not null,
    time_window_start timestamptz not null,
    time_window_end timestamptz not null,
    summary text not null,
    confidence numeric not null,
    related_work_order_id text,
    related_asset_ids jsonb not null default '[]'::jsonb
);

create table if not exists evidence_items (
    evidence_id text primary key,
    detection_id text not null references detections(detection_id),
    evidence_type text not null,
    evidence_timestamp timestamptz not null,
    title text not null,
    description text not null,
    source_event_ids jsonb not null,
    score numeric not null
);

create table if not exists recommendations (
    recommendation_id text primary key,
    detection_id text not null references detections(detection_id),
    status text not null,
    recommended_action text not null,
    rationale text not null,
    risk_level text not null,
    requires_approval boolean not null,
    created_at timestamptz not null
);

create table if not exists approval_decisions (
    approval_id text primary key,
    recommendation_id text not null references recommendations(recommendation_id),
    reviewer text not null,
    decision text not null,
    reason text not null,
    created_at timestamptz not null
);

create table if not exists audit_events (
    audit_event_id text primary key,
    audit_timestamp timestamptz not null,
    actor text not null,
    action text not null,
    entity_type text not null,
    entity_id text not null,
    details jsonb not null default '{}'::jsonb
);

