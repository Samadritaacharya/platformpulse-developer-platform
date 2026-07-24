"use strict";

const REPO_URL = "https://github.com/Samadritaacharya/platformpulse-developer-platform";

const personaData = {
  new: {
    metrics: [
      ["Weekly time lost", "74 min", "Repository, access and deployment setup"],
      ["Friction score", "4.4 / 5", "Highest at first deployment"],
      ["Support demand", "3.2", "Requests per engineer / month"],
      ["Opportunity", "89 / 100", "Strong self-service case"]
    ],
    bars: [["Access", 63], ["Repository", 88], ["Build", 57], ["Deploy", 94], ["Monitor", 49]],
    title: "Repository and first-deployment setup",
    text: "New engineers repeatedly assemble ownership, CI and deployment controls before they can deliver useful product changes.",
    quote: "I know what service I want to build; the slow part is finding the supported setup."
  },
  owner: {
    metrics: [
      ["Weekly time lost", "46 min", "Support and recurring delivery friction"],
      ["Friction score", "3.7 / 5", "Highest at incident handoff"],
      ["Support demand", "2.1", "Requests per owner / month"],
      ["Opportunity", "72 / 100", "Ownership and runbook coverage"]
    ],
    bars: [["Access", 28], ["Repository", 42], ["Build", 58], ["Deploy", 67], ["Monitor", 82]],
    title: "Service ownership and operability",
    text: "Experienced owners need faster visibility into SLO health, recurring incidents, documentation gaps and accountable escalation paths.",
    quote: "The deployment is not the hard part; proving who owns the next action often is."
  },
  platform: {
    metrics: [
      ["Weekly time lost", "91 min", "Repeated support and exception handling"],
      ["Friction score", "4.1 / 5", "Highest at unsupported variation"],
      ["Support demand", "12.4", "Requests per platform engineer / month"],
      ["Opportunity", "93 / 100", "Reduce toil and fragmentation"]
    ],
    bars: [["Access", 54], ["Repository", 65], ["Build", 78], ["Deploy", 84], ["Monitor", 71]],
    title: "Platform fragmentation and support toil",
    text: "Platform teams lose capacity when local variations bypass supported templates and create repeated diagnosis and maintenance work.",
    quote: "Every unsupported path becomes a platform support commitment later."
  }
};

function animateCounters() {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll("[data-counter]").forEach((node) => {
    const target = Number(node.dataset.counter || 0);
    if (prefersReduced) {
      node.textContent = String(target);
      return;
    }
    const start = performance.now();
    const duration = 700;
    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      node.textContent = String(Math.round(target * progress));
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
}

function setupTabs() {
  const tabs = [...document.querySelectorAll("[role='tab']")];
  const panels = [...document.querySelectorAll("[role='tabpanel']")];

  function activate(tab) {
    const target = tab.dataset.tab;
    tabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
    panels.forEach((panel) => {
      const active = panel.dataset.panel === target;
      panel.hidden = !active;
      panel.classList.toggle("active", active);
    });
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      let next = index;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      tabs[next].focus();
      activate(tabs[next]);
    });
  });
}

function renderPersona(key) {
  const data = personaData[key] || personaData.new;
  const metrics = document.getElementById("persona-metrics");
  const bars = document.getElementById("journey-bars");
  metrics.replaceChildren();
  bars.replaceChildren();

  data.metrics.forEach(([label, value, note]) => {
    const article = document.createElement("article");
    const span = document.createElement("span");
    const strong = document.createElement("strong");
    const small = document.createElement("small");
    span.textContent = label;
    strong.textContent = value;
    small.textContent = note;
    article.append(span, strong, small);
    metrics.append(article);
  });

  data.bars.forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    const name = document.createElement("span");
    name.textContent = label;
    const progress = document.createElement("progress");
    progress.className = "bar-progress";
    progress.max = 100;
    progress.value = value;
    progress.setAttribute("aria-label", `${label} friction ${value} out of 100`);
    const score = document.createElement("strong");
    score.textContent = String(value);
    row.append(name, progress, score);
    bars.append(row);
  });

  document.getElementById("persona-insight-title").textContent = data.title;
  document.getElementById("persona-insight-text").textContent = data.text;
  document.getElementById("persona-quote").textContent = `“${data.quote}”`;
}

function sanitizeServiceName(value) {
  return value.toLowerCase().trim().replace(/_/g, "-").replace(/[^a-z0-9-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "").slice(0, 63);
}

function sanitizeTeam(value) {
  return value.trim().replace(/[^A-Za-z0-9 ._-]+/g, "").slice(0, 64) || "unassigned-team";
}

function buildManifest() {
  const service = sanitizeServiceName(document.getElementById("service-name").value) || "example-service";
  const team = sanitizeTeam(document.getElementById("team-name").value);
  const environment = document.getElementById("environment").value;
  const slo = Number(document.getElementById("slo").value).toFixed(2);
  return `apiVersion: platformpulse.dev/v1\nkind: Service\nmetadata:\n  name: ${service}\n  owner: ${team}\nspec:\n  environment: ${environment}\n  language: Python\n  slo:\n    availabilityTarget: ${slo}\n  delivery:\n    ci: required\n    signedArtifacts: true\n  security:\n    runAsNonRoot: true\n    readOnlyRootFilesystem: true\n    allowPrivilegeEscalation: false\n    auditLogging: required\n`;
}

function updateManifestPreview() {
  document.getElementById("manifest-preview").textContent = buildManifest();
  const slo = Number(document.getElementById("slo").value).toFixed(2);
  document.getElementById("slo-output").textContent = `${slo}%`;
}

function downloadText(filename, content, mime = "text/plain") {
  const blob = new Blob([content], { type: `${mime};charset=utf-8` });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 500);
}

function setupManifestGenerator() {
  ["service-name", "team-name", "environment", "slo"].forEach((id) => {
    document.getElementById(id).addEventListener("input", updateManifestPreview);
  });
  document.getElementById("manifest-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const rawName = document.getElementById("service-name").value;
    const service = sanitizeServiceName(rawName);
    const status = document.getElementById("manifest-status");
    if (!service) {
      status.textContent = "Enter a service name containing letters or numbers.";
      return;
    }
    downloadText(`${service}-service-catalog.yaml`, buildManifest(), "application/yaml");
    status.textContent = `Downloaded ${service}-service-catalog.yaml. No data left your browser.`;
  });
  updateManifestPreview();
}

function erfApprox(x) {
  const sign = x < 0 ? -1 : 1;
  const value = Math.abs(x);
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;
  const t = 1 / (1 + p * value);
  const y = 1 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-value * value);
  return sign * y;
}

function normalCdf(x) {
  return 0.5 * (1 + erfApprox(x / Math.sqrt(2)));
}

function updateExperiment() {
  const control = Number(document.getElementById("control-rate").value);
  const treatment = Number(document.getElementById("treatment-rate").value);
  const sample = Number(document.getElementById("sample-size").value);
  const p1 = control / 100;
  const p2 = treatment / 100;
  const pooled = (p1 + p2) / 2;
  const standardError = Math.sqrt(Math.max(pooled * (1 - pooled) * (2 / sample), Number.EPSILON));
  const z = (p2 - p1) / standardError;
  const pValue = Math.max(0, Math.min(1, 2 * (1 - normalCdf(Math.abs(z)))));
  const absolute = treatment - control;
  const relative = control > 0 ? (absolute / control) * 100 : 0;

  document.getElementById("control-output").textContent = `${control}%`;
  document.getElementById("treatment-output").textContent = `${treatment}%`;
  document.getElementById("sample-output").textContent = String(sample);
  document.getElementById("control-result").textContent = `${control}%`;
  document.getElementById("treatment-result").textContent = `${treatment}%`;
  document.getElementById("control-bar").value = control;
  document.getElementById("treatment-bar").value = treatment;
  document.getElementById("absolute-uplift").textContent = `${absolute.toFixed(1)} pts`;
  document.getElementById("relative-uplift").textContent = `${relative.toFixed(1)}%`;
  document.getElementById("p-value").textContent = pValue < 0.0001 ? "<0.0001" : pValue.toFixed(4);

  let decision = "Continue the experiment and gather more evidence.";
  if (pValue < 0.05 && absolute > 0) decision = "Ship progressively with monitoring and rollback guardrails.";
  if (pValue < 0.05 && absolute < 0) decision = "Stop the treatment and investigate the negative impact.";
  if (sample < 100) decision = "Sample is small: treat the result as directional, not final.";
  document.getElementById("experiment-decision").textContent = decision;
}

function setupExperiment() {
  ["control-rate", "treatment-rate", "sample-size"].forEach((id) => {
    document.getElementById(id).addEventListener("input", updateExperiment);
  });
  updateExperiment();
}

function updateGovernance() {
  const controls = [...document.querySelectorAll("#governance-controls input[type='checkbox']")];
  const checked = controls.filter((control) => control.checked).length;
  const score = Math.round((checked / controls.length) * 100);
  document.getElementById("governance-score").textContent = String(score);
  const progress = document.getElementById("score-ring");
  progress.value = score;
  progress.setAttribute("aria-label", `Governance readiness ${score} out of 100`);
  let message = "Critical governance controls remain incomplete.";
  if (score >= 50) message = "Core ownership exists; complete operational controls before broad rollout.";
  if (score >= 84) message = "Strong readiness: validate evidence, approvals and continuous monitoring.";
  document.getElementById("governance-message").textContent = message;
}

function setupGovernance() {
  document.querySelectorAll("#governance-controls input[type='checkbox']").forEach((control) => {
    control.addEventListener("change", updateGovernance);
  });
  updateGovernance();
}

function setExternalLinks() {
  document.querySelectorAll("a[href^='http']").forEach((anchor) => {
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
  });
  document.getElementById("year").textContent = String(new Date().getFullYear());
  if (!REPO_URL.startsWith("https://github.com/")) console.warn("Unexpected repository URL configuration.");
}

document.addEventListener("DOMContentLoaded", () => {
  animateCounters();
  setupTabs();
  renderPersona("new");
  document.getElementById("persona").addEventListener("change", (event) => renderPersona(event.target.value));
  setupManifestGenerator();
  setupExperiment();
  setupGovernance();
  setExternalLinks();
});
