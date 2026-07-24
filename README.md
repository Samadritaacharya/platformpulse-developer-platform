# PlatformPulse — Developer Experience & Internal Platform Product Lab

[![CI](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/ci.yml)
[![Security](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/security.yml/badge.svg)](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/security.yml)

PlatformPulse is an independent, end-to-end portfolio project exploring how an internal Developer Platform can reduce developer friction and improve delivery reliability. It combines developer discovery, a self-service golden path, service ownership, CI/CD telemetry, platform-health metrics, privacy-safe A/B testing, feedback prioritisation, and an evidence-based product roadmap.

> **Responsible portfolio use:** All platform, engineering, survey, service, incident, experiment and pipeline data in this repository is synthetic. This project is not affiliated with Kaufland e-commerce or any employer and contains no proprietary company information.

## Recruiter quick view

| Product-management capability | Evidence in PlatformPulse |
|---|---|
| Active discovery | Developer personas, journey mapping, survey analysis, pain-point clustering |
| User-centric goals | Developer Experience Score, time to first deployment, self-service adoption, support demand |
| Technical product fluency | CI/CD, Docker, Kubernetes, Helm, APIs, service ownership, SLOs and observability concepts |
| Product decisions | Weighted RICE scoring, trade-off explanation, decision log and Now/Next/Later roadmap |
| Experimentation | Interactive A/B lab, significance testing, guardrails, rollout recommendation and downloadable decision record |
| Delivery breakdown | User stories, acceptance criteria, dependencies, risks and measurable outcomes |
| Platform self-service | Downloadable FastAPI starter service with tests, CI, Docker, hardened Kubernetes, Helm and ownership metadata |
| Operational excellence | Service catalogue, deployment health, incident signals, SLO status and runbook recommendations |
| Security & governance | Input allow-lists, non-root containers, least-privilege workflows, vulnerability scans and AI-governance controls |

## What the application does

1. **Discovery Hub** — analyses synthetic developer feedback across onboarding, repository setup, build, test, deploy, monitoring and incident response.
2. **Golden Path Generator** — creates a downloadable, production-minded starter service from user inputs.
3. **Service Catalogue** — surfaces missing owners, documentation gaps, failed pipelines, stale deployments and SLO risks.
4. **Platform Metrics** — tracks product and delivery indicators such as time to first deployment, adoption, pipeline success, lead time, change-failure rate and MTTR.
5. **Feedback to Roadmap** — converts evidence into prioritised opportunities, user stories, acceptance criteria and a Now/Next/Later plan.
6. **Decision Simulator** — makes trade-offs transparent by adjusting reach, impact, confidence, effort, strategic alignment and reliability risk.
7. **Reliability View** — translates platform signals into health status, accountable ownership and recommended action.
8. **A/B Testing Lab** — compares the current setup flow with a guided golden path using aggregate synthetic data, a two-proportion significance test and responsible rollout guardrails.

## Three-minute demo path

1. Open **Discovery Hub** and select the *New Backend Engineer* persona.
2. Review the journey-stage friction and highest-impact evidence.
3. Open **Golden Path Generator**, configure a service and download the generated ZIP.
4. Open **A/B Testing Lab** to evaluate whether the guided path improves first-deployment success.
5. Open **Roadmap & Decisions** to see how evidence becomes a prioritised product decision.
6. Finish in **Reliability** with SLO, deployment and runbook recommendations.

## Technology

`Python` · `Streamlit` · `Pandas` · `Plotly` · `PyYAML` · `pytest` · `GitHub Actions` · `Docker` · `Kubernetes` · `Helm`

## Run locally

```bash
git clone https://github.com/Samadritaacharya/platformpulse-developer-platform.git
cd platformpulse-developer-platform
python -m venv .venv
```

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

## Run with Docker

```bash
docker compose up --build
```

Then open `http://localhost:8501`. Streamlit automatically exposes the A/B Testing Lab in the multipage navigation.

## Quality and security

Pull requests run functional tests, compilation, dependency vulnerability scanning, static security analysis and focused security regression tests. The generated service uses a non-root container user, read-only Kubernetes root filesystem, dropped capabilities, no privilege escalation and read-only GitHub workflow permissions.

See [QA, Cybersecurity and AI Governance](docs/QA_SECURITY_AI_GOVERNANCE.md) before sharing or extending the project.

## Product documentation

- [Product vision](docs/PRODUCT_VISION.md)
- [Discovery report](docs/DISCOVERY_REPORT.md)
- [Personas and developer journey](docs/PERSONAS_AND_JOURNEY.md)
- [Product requirements](docs/PRD.md)
- [Metrics dictionary](docs/METRICS_DICTIONARY.md)
- [Prioritisation and roadmap](docs/PRIORITISATION_AND_ROADMAP.md)
- [Architecture and decision log](docs/ARCHITECTURE_AND_DECISIONS.md)
- [Validation report](docs/VALIDATION_REPORT.md)
- [QA, cybersecurity and AI governance](docs/QA_SECURITY_AI_GOVERNANCE.md)

## Product hypothesis

> A developer platform creates measurable value when it removes repeated setup work, makes supported paths easy to discover, improves ownership and operability, and gives teams fast feedback without reducing engineering autonomy.

## Scope and limitations

PlatformPulse is a portfolio prototype, not a production platform. It deliberately generates deployment-ready **artefacts** rather than provisioning real cloud infrastructure. This keeps the demo safe, reproducible and vendor-neutral while demonstrating technical product judgement and platform concepts. Statistical significance in the A/B lab is decision support, not an automatic rollout instruction.

## Author

**Samadrita Acharya**  
[LinkedIn](https://www.linkedin.com/in/samadrita-acharya-a07266184/) · [GitHub](https://github.com/Samadritaacharya)
