# PlatformPulse — Developer Experience & Internal Platform Product Lab

[![PlatformPulse CI](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/ci.yml)
[![Security](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/security.yml/badge.svg)](https://github.com/Samadritaacharya/platformpulse-developer-platform/actions/workflows/security.yml)
[![Visual Site](https://img.shields.io/badge/Visual%20Site-GitHub%20Pages-40d7c7)](https://samadritaacharya.github.io/platformpulse-developer-platform/)

PlatformPulse is an independent, end-to-end Developer Platform product prototype. It connects developer discovery, a secure self-service golden path, service ownership, CI/CD and SLO metrics, A/B experimentation, AI governance, feedback prioritisation and an evidence-based product roadmap.

> **Responsible portfolio use:** every person, service, incident, survey response, experiment and AI use case is synthetic. The project is not affiliated with Kaufland e-commerce or any employer and contains no proprietary company information.

## Public experiences

- **Visual product website:** `https://samadritaacharya.github.io/platformpulse-developer-platform/`
- **Complete interactive application:** deploy `app.py` free on Streamlit Community Cloud using the steps in [DEPLOYMENT.md](DEPLOYMENT.md).
- **Source, tests and product documentation:** this repository.

The GitHub Pages website is a recruiter-friendly visual front door. The Streamlit application is the complete product experience with all nine views and downloadable artefacts.

## Recruiter quick view

| Product-management capability | Working evidence |
|---|---|
| Active discovery | personas, journey mapping, evidence register and pain-point analysis |
| User-centric goals | Developer Experience Score, time to first deployment and self-service adoption |
| Technical product fluency | CI/CD, Docker, Kubernetes, Helm, APIs, SLOs and observability concepts |
| Product decisions | weighted prioritisation, Now/Next/Later roadmap and explicit trade-offs |
| Experimentation | Control/Treatment events, SRM check, uplift, confidence interval and guardrails |
| Secure self-service | downloadable FastAPI starter with non-root container and Kubernetes controls |
| AI governance | use-case inventory, risk scoring, human oversight, access and audit controls |
| Operational excellence | service catalogue, health score, incidents, ownership and first-action guidance |

## Nine working views

1. **Executive Overview**
2. **Developer Discovery**
3. **Golden Path Generator**
4. **Service Catalogue**
5. **Platform Metrics**
6. **Experiment Lab**
7. **Roadmap & Decisions**
8. **AI Governance & Security**
9. **Reliability**

## Secure-by-default generator

The generated starter service includes:

```text
app/main.py                     FastAPI health and readiness endpoints
tests/test_health.py            automated API tests
.github/workflows/ci.yml        least-privilege CI with pinned actions
Dockerfile                      non-root container
kubernetes/deployment.yaml      seccomp, no privilege escalation, dropped capabilities
kubernetes/service.yaml         service exposure
helm/                           chart metadata
service-catalog.yaml            owner, SLO, environment and security metadata
README.md                       run, test and production security checklist
```

## A/B experiment

The Experiment Lab compares manual onboarding with the secure golden path. It validates assignment balance, conversion uplift, a 95% confidence interval and guardrails for deployment time, support requests and satisfaction. The committed event dataset is deterministic and synthetic.

## AI governance

The governance view evaluates synthetic AI use cases across data classification, external models, residency, personal data, automated decisions, human oversight, access controls and audit logging. It is a transparent demonstration—not legal advice or a compliance claim.

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

## Run hardened container

```bash
docker compose up --build
```

Open `http://localhost:8501`.

## Automated quality gates

The CI pipeline validates:

- all unit and Streamlit UI tests;
- Python compilation;
- Bandit static security analysis;
- pip-audit dependency scanning;
- Streamlit live health check;
- generated FastAPI tests;
- generated Docker build and live health check.

## Documentation

- [Recruiter demo](docs/RECRUITER_DEMO.md)
- [A/B testing](docs/AB_TESTING.md)
- [AI governance](docs/AI_GOVERNANCE.md)
- [Demo data](docs/DEMO_DATA.md)
- [QA and security report](docs/QA_SECURITY_REPORT.md)
- [Security policy](SECURITY.md)
- [Free website deployment](DEPLOYMENT.md)

## Author

**Samadrita Acharya**  
[LinkedIn](https://www.linkedin.com/in/samadrita-acharya-a07266184/) · [GitHub](https://github.com/Samadritaacharya)
