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

## Dependency Security

Before adding dependencies:

- Check license
- Check maintenance status
- Check known security issues
- Prefer mature packages
- Avoid unnecessary packages
