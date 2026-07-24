# QA, Cybersecurity and AI Governance

## Quality gates

PlatformPulse is validated through automated tests, Python compilation, dependency scanning and static security analysis. The public demo must not be shared unless both the main CI workflow and the security workflow are green.

### Functional coverage

- all Streamlit views import and render;
- synthetic data files load with the required schema;
- product metrics and opportunity ranking return deterministic outputs;
- the golden path creates a valid ZIP with safe relative paths;
- generated FastAPI code includes a health endpoint, test, CI, Docker, Kubernetes, Helm and service metadata;
- the A/B testing engine validates counts and returns a deterministic two-proportion test;
- the recruiter-ready experiment demonstrates the guided golden path without using personal data.

## Security threat model

| Threat | Control |
|---|---|
| Path traversal in generated ZIP | Service names are normalised and every generated path is controlled by the application. Regression tests reject traversal. |
| Code/YAML injection through user input | Team and enum inputs are allow-listed; generated Python string values use JSON escaping; YAML is emitted with `safe_dump`. |
| Privileged containers | Generated Docker image runs as a non-root user. Kubernetes drops capabilities, blocks privilege escalation, uses a read-only root filesystem and disables automatic service-account token mounting. |
| Mutable image risk | Generated examples use a versioned tag rather than `latest`. Production users should pin immutable image digests. |
| Excess GitHub token access | Generated and repository workflows declare read-only `contents` permission. |
| Vulnerable dependencies | Weekly and pull-request `pip-audit` scan. Dependencies remain pinned for reproducibility. |
| Unsafe source disclosure | Demo data is synthetic and the application contains no employer, client, repository secret or production telemetry. |
| Formula manipulation | A/B inputs are bounded and validated; impossible conversion counts are rejected. |

## Data protection

PlatformPulse operates without authentication, cookies, external APIs or a database. The supplied demo uses aggregate synthetic data. A production implementation should apply data minimisation, purpose limitation, documented retention, role-based access, encryption, audit logging and a data-protection review before ingesting employee or repository telemetry.

Do not collect names, emails, raw source code, secrets, commit contents, protected characteristics or individual productivity scores for this portfolio demonstration.

## AI governance

No generative-AI model is called by the current application. The project nevertheless demonstrates governance-ready product controls:

1. **Human accountability:** roadmap and rollout decisions remain with named human owners.
2. **Risk classification:** intended use, affected users, data classes and reliability consequences should be recorded before any AI feature is enabled.
3. **Data governance:** prohibit credentials, confidential code and unnecessary personal data from prompts or training datasets.
4. **Evaluation:** define task-specific quality, safety, bias, privacy and reliability tests before release.
5. **Transparency:** clearly label AI-generated recommendations and synthetic evidence.
6. **Human override:** provide escalation, correction, rollback and appeal paths.
7. **Monitoring:** measure drift, failures, security events and user impact after release.
8. **Vendor governance:** assess data residency, retention, subprocessors, model access, auditability and exit strategy.

AI outputs must never be used by this project for employment, disciplinary, access-control or other high-impact individual decisions.

## Responsible A/B testing

- pre-register the hypothesis, primary metric, guardrails, duration and stop conditions;
- use aggregate events and random assignment only where operationally safe;
- avoid experiments that disadvantage protected or vulnerable groups;
- monitor reliability, privacy, security and support-demand guardrails;
- preserve a rollback path and document negative or inconclusive findings;
- treat statistical significance as one input, not an automatic product decision.

## Manual release checklist

- [ ] Main CI and Security workflows are green.
- [ ] Public Streamlit URL opens without authentication.
- [ ] Every navigation view loads at desktop and mobile widths.
- [ ] Golden Path ZIP downloads and passes local tests.
- [ ] A/B demo produces a result and exports the decision CSV.
- [ ] No secrets are present in the repository history or application settings.
- [ ] Synthetic-data disclosure remains visible in the README and UI.
- [ ] Repository About section contains the live demo URL.
