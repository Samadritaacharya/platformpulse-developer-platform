# Security Policy

PlatformPulse is a public portfolio prototype that uses synthetic data only. It must never receive employer, client, production, credential, personal, confidential or regulated data.

## Supported version

Only the latest commit on `main` is supported.

## Reporting a vulnerability

Please open a private GitHub security advisory where available. Do not disclose credentials, exploit details or personal data in a public issue. For non-sensitive defects, use the repository issue tracker.

## Security boundaries

- No authentication, user accounts or production persistence are implemented.
- No secrets or API keys are required.
- Generated artefacts are examples and require an organisation-specific security review before production use.
- AI governance scoring is a demonstration model, not legal advice, certification or a replacement for Security, Privacy or Legal review.
- A/B testing data and all service telemetry are synthetic.

## Implemented controls

- allow-listed local datasets and strict schema validation;
- sanitised and validated generator inputs;
- archive path traversal checks;
- non-root Docker execution;
- read-only filesystem and dropped Linux capabilities in Compose;
- Kubernetes non-root, seccomp, no privilege escalation and no automatic service-account token;
- CORS and XSRF protections enabled for Streamlit;
- least-privilege GitHub Actions permissions;
- pinned GitHub Actions commit SHAs;
- automated unit, UI, generated-service, container-health, Bandit and dependency-audit checks.
