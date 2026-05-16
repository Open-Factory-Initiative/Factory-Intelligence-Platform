# Security Model

## MVP Security Posture

The MVP is local-development-first and simulator-first. It should not be connected to real industrial control systems.

## Security Principles

- No secrets in git
- Validate all external input
- Use least privilege
- Separate recommendations from actions
- Audit human decisions
- Make demo/simulator behavior explicit
- Do not build unsafe industrial writeback paths

## Secrets

Use `.env.example` to document required variables.

Never commit:

- API keys
- Plant credentials
- Customer data
- Historian credentials
- QMS/MES/ERP credentials
- Production connection strings

## Industrial Safety

The MVP must not:

- Write to real PLCs
- Write to real SCADA/DCS
- Change machine parameters
- Release product
- Close deviations
- Create production CAPA records

Future production integrations must use explicit approval, policy checks, and audit trails.

## Local AI Data Boundaries

Future model-enabled workflows should be local-first and site-aware. Local model
deployment is preferred for site-specific data, and remote-compatible model
providers must be explicitly configured, approved, and audited before use.

- No unapproved site data should leave the site boundary.
- RAG corpora, training datasets, prompts, model adapters, and evaluation
  records should be traceable to approved sources.
- Model outputs remain advisory and must not trigger factory-state changes
  outside governed review workflows.
- Tool access for agents should be registered, permissioned, and logged.

## Dependency Security

Before adding dependencies:

- Check license
- Check maintenance status
- Check known security issues
- Prefer mature packages
- Avoid unnecessary packages
