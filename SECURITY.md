# Security Policy

## Reporting Security Issues

Please do not report security vulnerabilities in public issues.

Until a formal security contact is established, open a private security advisory in GitHub if available.

## Scope

This project is early-stage and simulator-first.

The MVP should not be connected to real industrial systems or used for production control.

## Sensitive Information

Do not submit:

- Plant credentials
- Customer data
- Proprietary process data
- Production connection strings
- API keys
- Network diagrams for real facilities
- Vulnerability details in public issues

## Industrial Safety

The project does not currently support production industrial writeback.

Any future feature that writes to external manufacturing systems must include:

- Human approval
- Policy checks
- Audit logs
- Clear rollback/cancellation behavior where possible
- Security review
- Maintainer approval
