# Architecture and Decision Log

## Architecture

```text
Streamlit application
├── Discovery and product views
├── Golden-path configuration and ZIP download
├── Service catalogue
├── Metrics and visualisations
├── Prioritisation and roadmap
└── Reliability recommendations

PlatformPulse Python package
├── data.py              repository-relative data loading
├── generator.py         starter-service artefact generation
├── metrics.py           product and delivery KPIs
├── prioritization.py    weighted RICE scoring
└── reliability.py       transparent service-health logic

Synthetic CSV data
├── survey_results.csv
├── feedback.csv
├── services.csv
└── pipeline_metrics.csv
```

## Decision 001 — Streamlit plus modular Python

**Decision:** Use a polished Streamlit interface with isolated product logic.

**Why:** It provides a reliable public demo while keeping scoring, generation and health logic testable outside the UI.

## Decision 002 — Generate artefacts rather than provision infrastructure

**Decision:** Produce a downloadable starter-service ZIP instead of deploying cloud resources.

**Why:** The portfolio project must remain safe, reproducible, vendor-neutral and free of credentials while still demonstrating platform concepts.

## Decision 003 — Synthetic data by default

**Decision:** Label all public research and operational data as synthetic.

**Why:** It avoids fabricated interviews and protects employer, customer and participant information.

## Decision 004 — Transparent scoring over opaque recommendations

**Decision:** Expose score inputs and decision logic.

**Why:** A Technical Product Manager should be able to explain trade-offs, challenge assumptions and change the recommendation when evidence changes.

## Decision 005 — Product discovery before infrastructure depth

**Decision:** Prioritise user journeys, metrics and roadmap evidence over building a complex Kubernetes environment.

**Why:** The target capability is technical product management, not a platform-engineering coding assessment.
