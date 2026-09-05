# PlatformPulse — Developer Experience & Internal Platform Product Lab

[![PlatformPulse CI](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/ci.yml)
[![Visual Site](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/pages.yml/badge.svg)](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/pages.yml)
[![Security Gates](https://img.shields.io/badge/security-Bandit%20%2B%20pip--audit-2ea44f)](docs/QA_SECURITY_REPORT.md)

**PlatformPulse is an end-to-end developer-platform product prototype connecting developer discovery, secure self-service golden paths, service ownership, CI/CD and SLO metrics, experimentation, AI governance, reliability, and evidence-based roadmap decisions.**

[**Open live product →**](https://samadritaacharya.github.io/platformpulse-developer-platform/) · [Source](https://github.com/Samadritaacharya/platformpulse-developer-platform)

> All people, services, incidents, surveys, experiments, and AI use cases are synthetic. The project is independent and contains no proprietary employer or client information.

## Product surface

| Area | What is implemented |
|---|---|
| Developer discovery | Personas, journey mapping, evidence register, pain-point analysis |
| Golden path | Downloadable secure FastAPI starter with Docker, Kubernetes, Helm, CI, and service metadata |
| Service catalogue | Ownership, SLOs, environment metadata, health, and operational guidance |
| Platform metrics | Developer Experience Score, adoption, delivery, reliability, and SLO views |
| Experimentation | Control/treatment events, SRM check, uplift, confidence interval, and guardrails |
| Roadmap | Weighted prioritisation, Now/Next/Later planning, trade-offs, and decision evidence |
| AI governance | Use-case inventory, risk scoring, oversight, access, and audit controls |
| Reliability | Incidents, service health, first-action guidance, and operational ownership |

## Nine working views

1. Executive Overview
2. Developer Discovery
3. Golden Path Generator
4. Service Catalogue
5. Platform Metrics
6. Experiment Lab
7. Roadmap & Decisions
8. AI Governance & Security
9. Reliability

## Secure-by-default service generator

The generated starter service includes:

```text
app/main.py                     FastAPI health and readiness endpoints
tests/test_health.py            automated API tests
.github/workflows/ci.yml        least-privilege CI
Dockerfile                      non-root container
kubernetes/deployment.yaml      seccomp + restricted privileges
kubernetes/service.yaml         service exposure
helm/                           chart metadata
service-catalog.yaml            owner, SLO, environment, security metadata
README.md                       run, test, production-security checklist
```

## Verification

GitHub Actions validates the Python application, every Streamlit view, generated service artefacts, generated-service tests, live health checks, security scanning, and the visual site's interactions and asset references.

The committed datasets are deterministic and synthetic so product decisions, experiments, and governance logic are reproducible.

## Technology

`Python` · `Streamlit` · `Pandas` · `Plotly` · `PyYAML` · `pytest` · `Selenium` · `GitHub Actions` · `Docker` · `Kubernetes` · `Helm`

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

## Run containerized

```bash
docker compose up --build
```

Open `http://localhost:8501`.

## Documentation

- [A/B testing](docs/AB_TESTING.md)
- [AI governance](docs/AI_GOVERNANCE.md)
- [Demo data](docs/DEMO_DATA.md)
- [QA and security report](docs/QA_SECURITY_REPORT.md)
- [Security policy](SECURITY.md)
- [Deployment](DEPLOYMENT.md)

## Design principle

PlatformPulse treats the internal platform as a product: start with developer problems, create safe self-service paths, measure adoption and reliability, and use evidence to decide what the platform should do next.
