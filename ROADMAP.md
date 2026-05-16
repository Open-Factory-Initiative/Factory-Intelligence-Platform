# Roadmap

The Factory Intelligence Platform roadmap starts with the simulator-backed
Process Sentinel MVP, then expands into local-first AI, site-specific context,
model governance, and validation-aware workflows. AI work must remain
model-agnostic, open-source friendly, and limited to human-reviewed decision
support and governed recommendations.

## Phase 0: Repository Foundation

- Professional README
- Codex instructions
- Architecture docs
- Testing docs
- Contribution docs
- Issue/PR templates
- CI baseline

## Phase 1: Simulator-First Foundation

- Synthetic site/area/line/asset model
- Seeded scenarios
- Process measurement generation
- Quality measurement generation
- Drift scenarios
- Test fixtures

## Phase 2: Event Contracts + Ingestion

- Unified event envelope
- Event validation
- Ingestion worker
- Event storage
- Contract tests

## Phase 3: Process Sentinel MVP

- Drift detection rules
- Evidence timeline
- Detection records
- Recommendation generation
- Human-reviewed decision support language
- Unit and integration tests

## Phase 4: Governed Workflow

- Recommendation review states
- Approval/rejection/defer workflow
- Audit events
- RCA/CAPA draft output
- AI outputs routed through governed recommendations only

## Phase 5: Web Workbench

- Dashboard
- Detection list
- Detection detail
- Evidence timeline
- Approval panel
- Draft report view

## Phase 6: E2E Hardening

- Full Playwright workflow
- CI checks
- Docs polish
- Demo scenario
- Contributor onboarding
- Validation-aware documentation patterns

## Phase 7: Local AI + Site Intelligence Foundation

- Model-agnostic Local Model Gateway
- Initial provider targets: Ollama, llama.cpp, vLLM, and OpenAI-compatible endpoints
- Provider abstraction with common request/response schemas
- Tool-call boundaries for read-only and recommendation-only AI use cases
- Model usage logging for audit-friendly review
- Streaming support as a later gateway capability
- Model Router for SLM-first and LLM-fallback behavior
- Routing criteria: task type, confidence, context size, cost, latency, risk level, and GxP impact
- Clear separation between SLM tasks, LLM tasks, rules/analytics tasks, and human approval gates

## Phase 8: Site AI Package + RAG Foundation

- Standard Site AI Package for site-specific onboarding
- Site profile, area/line/asset hierarchy, process context, and equipment metadata
- Tag mappings, event contracts, prompt templates, model routing config, and tool registry config
- Document corpus ingestion, chunking, metadata, embeddings, and retrieval indexes
- RAG before fine-tuning for site-specific context
- Factory Memory integration for similar-event retrieval and investigation history
- Cited evidence for Process Sentinel, evidence timelines, RCA/CAPA drafts, and future investigations
- Permission-aware retrieval and retrieval audit logging as future requirements
- Synthetic documents and test fixtures for local development

## Phase 9: SLM/LLM Training + Evaluation Pipeline

- Curated, approved, and traceable site-specific datasets
- Data cleaning, redaction, sanitization, and instruction dataset generation
- Evaluation dataset generation from approved site materials
- LoRA/PEFT adapters preferred over full fine-tuning for site adaptation
- Model adapter training, packaging, registry metadata, and deployment manifests
- Developer-friendly local scripts and documented workflows
- Evaluation harness for grounded answers, retrieval quality, refusal behavior, hallucination checks, cited evidence, deterministic regressions, task accuracy, latency, and resource use
- Model promotion states: draft, evaluated, approved for non-GxP demo use, approved for site pilot, retired

## Phase 10: Model Governance + Validation-Aware Onboarding

- Model registry, prompt registry, tool registry, and dataset registry
- Evaluation records, model cards, adapter/version tracking, approval history, audit events, and rollback support
- Site AI Validation Package workstream
- Intended use statement and GxP impact assessment
- Risk classification and data flow diagram
- Model/tool inventory and prompt inventory
- Training data and RAG corpus traceability
- Evaluation protocol, acceptance criteria, and audit log requirements
- Human approval workflow and change control record
- Validation summary report template
- Validation-ready documentation pattern for future site validation work, not automatic regulatory compliance

## Phase 11: Agent Orchestration

- Agents call the Local Model Gateway and Tool Registry instead of direct model providers
- Evidence summarization agent
- RCA/CAPA draft language assistant
- Investigation path suggestion agent
- Similar prior event lookup from Factory Memory
- Drift signal explanation agent
- No autonomous execution or closed-loop factory control

## Later Phases

- MQTT connector
- OPC UA connector
- Historian connector
- QMS/MES integration stubs
- Role-based access
- Plugin framework
- Production deployment examples
- Advanced analytics
- Multi-site AI package management
- Permission-aware enterprise RAG
- Site pilot validation support

## AI Safety and Validation Principles

- AI outputs are advisory, evidence-cited, and human-reviewed.
- High-impact actions remain governed recommendations with explicit approval.
- No autonomous control of factory systems.
- Local-first model deployment is preferred for site data boundaries.
- Remote-compatible providers must be explicitly configured and approved.
- No unapproved site data should leave the site boundary.
- RAG should precede fine-tuning for site-specific context.
- LoRA/PEFT adapters should be preferred over full fine-tuning.
- cGMP-related work should be validation-aware, audit-friendly, and suitable for future site validation, not described as certified, regulatory-approved, or production-ready.
