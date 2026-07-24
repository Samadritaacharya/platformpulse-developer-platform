# Final Release Validation

PlatformPulse is released only when every automated job below is green on the final `main`-based tree.

## Required release gates

- unit tests for data, metrics, prioritisation, reliability, A/B experimentation, AI governance and secure generation;
- Python compilation;
- Bandit static security analysis;
- root dependency audit with `pip-audit`;
- real headless-Chrome navigation across all nine application views;
- browser submission of the Golden Path form;
- generated ZIP download and required-artefact validation;
- Streamlit live health check;
- generated dependency audit;
- generated FastAPI test suite;
- generated Docker build and live `/health` verification.

## Release boundaries

The project uses synthetic data and is suitable as a portfolio demonstration. Automated checks reduce known quality and security risks, but they do not prove the absence of every vulnerability and do not replace production threat modelling, penetration testing, privacy assessment, accessibility testing or organisation-specific architecture review.
