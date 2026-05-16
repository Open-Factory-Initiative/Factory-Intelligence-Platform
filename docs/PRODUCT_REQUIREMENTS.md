# Product Requirements

## Product Name

Factory Intelligence Platform

## Community

Open Factory Initiative

## Product Thesis

Manufacturing operations are fragmented across ERP, MES, SCADA, historians, QMS, CMMS, spreadsheets, and tribal knowledge. The Factory Intelligence Platform creates an open-source intelligence layer that connects those systems, understands operational state, detects risk, explains why risk is emerging, and supports governed human-approved action.

## First Wedge

The first wedge is **Process Sentinel**, a quality drift and deviation intelligence workflow.

## Primary Users

### Quality Engineer

Needs to understand why quality drift is happening, what production context matters, and what containment/RCA/CAPA steps should be considered.

### Process Engineer

Needs to connect process changes to quality outcomes and identify which parameters are driving risk.

### Manufacturing Engineer

Needs to understand line behavior, asset context, and process stability.

### Plant Manager

Needs quick visibility into risk, blocked production, and containment status.

### Controls / Automation Engineer

Needs clear integration boundaries and safe treatment of industrial systems.

### Software / Data Engineer

Needs stable schemas, APIs, tests, and docs to extend the platform.

## MVP User Story

As a quality engineer, I want the system to detect early quality drift from synthetic factory data, show the process evidence that likely contributed to the drift, and generate a human-reviewable recommendation with RCA/CAPA draft content so I can investigate faster without losing traceability.

## MVP Features

1. Simulated factory events
2. Normalized event model
3. Ingestion pipeline
4. Drift detection
5. Evidence timeline
6. Recommendation generation
7. Human approval workflow
8. RCA/CAPA draft export
9. Learning log / incident memory
10. Developer documentation and tests

## Non-Goals For MVP

- Real plant connection
- Autonomous control action
- Production deployment
- Enterprise RBAC
- Advanced ML models
- Local Model Gateway implementation
- Site-specific RAG and fine-tuning workflows
- Production GxP validation claims
- Full MES/QMS/ERP integration
- Multi-site federation
- Mobile app
- Paid SaaS features

## Success Criteria

The MVP is successful when a contributor can:

1. Clone the repo.
2. Run the platform locally.
3. Generate synthetic factory data.
4. Trigger a known drift scenario.
5. See the detection in the UI.
6. Inspect supporting evidence.
7. Approve/reject a recommendation.
8. Export or view RCA/CAPA draft text.
9. Run unit, integration, and e2e tests.
10. Understand the architecture from docs.

## Post-MVP AI Requirements

Future AI capabilities should strengthen the Factory Intelligence Layer while
preserving human-reviewed decision support and open-source-friendly deployment:

1. Provide a local-first, model-agnostic gateway for platform AI calls.
2. Route routine tasks to small specialized local models where practical.
3. Use larger local or external LLMs only for complex reasoning,
   summarization, or fallback cases.
4. Implement site-specific RAG and Factory Memory before fine-tuning.
5. Prefer LoRA/PEFT adapters over full fine-tuning for site adaptation.
6. Curate, approve, sanitize, and trace training and evaluation data.
7. Evaluate model behavior for grounded answers, cited evidence, retrieval
   quality, refusals, hallucination risk, task accuracy, latency, and resource
   use.
8. Maintain model, prompt, tool, dataset, adapter, and evaluation registries.
9. Package site-specific context through a Site AI Package.
10. Support validation-aware documentation for future site validation work
    without claiming automatic cGMP compliance.

## Product Principles

- Explain before acting.
- Simulate before integrating.
- Test contracts before adding services.
- Keep AI recommendations human-governed.
- Keep model outputs advisory and evidence-cited.
- Prefer local-first, model-agnostic AI infrastructure.
- Treat cGMP-related workflows as validation-aware until site validation is performed.
- Prefer practical workflows over impressive demos.
- Make the system teachable.
