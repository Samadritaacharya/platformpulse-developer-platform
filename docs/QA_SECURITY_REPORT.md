# QA, Cybersecurity and Release Readiness Report

## Scope

End-to-end validation covers product logic, demo data, Streamlit navigation, generated starter artefacts, container execution, security configuration, A/B analysis and AI governance.

## Automated checks

- schema and type validation for all six datasets;
- unit tests for metrics, prioritisation, reliability, experiments, governance and generator controls;
- Streamlit AppTest navigation across all nine views;
- secure golden-path ZIP content and path-safety tests;
- generated FastAPI service tests;
- generated Docker build and live `/health` verification;
- main Streamlit `/_stcore/health` smoke test;
- Python compilation;
- dependency consistency check;
- Bandit static security analysis;
- pip-audit dependency vulnerability scan.

## Security improvements

- changed Streamlit from disabled CORS to enabled CORS and XSRF protection;
- changed main and generated containers from root to non-root;
- added read-only filesystem, dropped capabilities and no-new-privileges runtime controls;
- added Kubernetes seccomp, non-root, no privilege escalation and disabled automatic service-account tokens;
- added allow-list validation for generated names, owners and configuration enums;
- pinned GitHub Actions to immutable commit SHAs and restricted workflow permissions;
- added responsible AI governance inventory and explicit limitations.

## Manual pre-share checks

1. Deploy from `main` using `app.py` with no secrets.
2. Confirm every sidebar page renders on desktop and mobile widths.
3. Generate and download the secure starter ZIP.
4. Verify the repository Actions page is green.
5. Confirm the public URL opens without authentication.
6. Add the live URL to the repository About section and README.
7. Do not add employer logos, internal screenshots or proprietary data.
