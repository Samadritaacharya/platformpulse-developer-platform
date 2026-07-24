# Publish PlatformPulse as a free visual website

PlatformPulse has two complementary public experiences:

1. **GitHub Pages visual showcase** — a polished, responsive product website with interactive discovery, golden-path, A/B experiment and AI-governance demos.
2. **Streamlit Community Cloud application** — the complete Python product with all nine views, downloadable starter-service ZIPs, charts, filters and decision exports.

## 1. Enable the GitHub Pages showcase

The repository contains `site/` and `.github/workflows/pages.yml`.

1. Open the repository on GitHub.
2. Select **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open **Actions → PlatformPulse Visual Site**.
5. Select **Run workflow** on branch `main` if the workflow did not start automatically.
6. After deployment, open:

   `https://samadritaacharya.github.io/platformpulse-developer-platform/`

The workflow always runs structural and real-browser validation first. If Pages has not yet been enabled, validation remains green, deployment is skipped, and the workflow summary displays the exact one-time setting required. After the setting is enabled, rerun the same workflow to publish the site.

The static site uses no cookies or analytics, sends no form data, requires no secrets and is tested against its strict Content Security Policy.

## 2. Deploy the full Streamlit application

1. Sign in to Streamlit Community Cloud with GitHub.
2. Select **Create app**.
3. Choose repository `Samadritaacharya/platformpulse-developer-platform`.
4. Select branch `main`.
5. Set the entry point to `app.py`.
6. Choose a memorable subdomain such as `samadrita-platformpulse` if available.
7. Deploy without secrets; the application uses synthetic local data only.
8. Make the app public and copy its `*.streamlit.app` URL.
9. Add that URL to the repository **About** section and README.

## Automated pre-deployment checks

The Visual Site workflow verifies:

- JavaScript syntax and every local CSS/JavaScript reference;
- absence of inline styles and inline scripts that would violate the strict CSP;
- all tabs and dynamic product views in headless Chrome;
- developer-persona switching and journey visualisation;
- manifest sanitisation and browser download;
- A/B experiment calculations and progress visualisations;
- AI-governance readiness interactions;
- absence of severe browser-console errors.

## Pre-share checklist

- GitHub CI and Visual Site workflows are green.
- The GitHub Pages showcase opens on desktop and mobile.
- All nine Streamlit navigation views render.
- The Golden Path Generator downloads a valid ZIP.
- The Experiment Lab exports a decision record.
- The repository and both websites clearly label data as synthetic.
- No API keys, tokens, personal data or employer information are present.
- The public Streamlit URL opens without authentication.
