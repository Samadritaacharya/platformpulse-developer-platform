'use client'

import dynamic from 'next/dynamic'
import { motion, useReducedMotion } from 'motion/react'
import { FormEvent, useEffect, useMemo, useState } from 'react'
import { project, type RunResult } from '@/lib/engine'

const ShaderGradientBackdrop = dynamic(() => import('./shader-gradient-backdrop').then((m) => m.ShaderGradientBackdrop), { ssr: false })
const SystemScene = dynamic(() => import('./system-scene').then((m) => m.SystemScene), { ssr: false })

type HistoryItem = { result: RunResult; at: string }

export function CommandCenter() {
  const reducedMotion = Boolean(useReducedMotion())
  const [scenario, setScenario] = useState(project.scenarios[0].id)
  const [intensity, setIntensity] = useState(50)
  const [context, setContext] = useState('')
  const [result, setResult] = useState<RunResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState<HistoryItem[]>([])

  useEffect(() => {
    try {
      const parsed = JSON.parse(localStorage.getItem(`${project.slug}:history`) || '[]')
      if (Array.isArray(parsed)) setHistory(parsed.slice(0, 4))
    } catch { localStorage.removeItem(`${project.slug}:history`) }
  }, [])

  useEffect(() => { setResult(null); setError('') }, [scenario, intensity, context])

  const selected = useMemo(() => project.scenarios.find((item) => item.id === scenario) ?? project.scenarios[0], [scenario])

  async function run(event?: FormEvent) {
    event?.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, intensity, context }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error || 'Simulation failed')
      const next = payload as RunResult
      setResult(next)
      const updated = [{ result: next, at: new Date().toISOString() }, ...history].slice(0, 4)
      setHistory(updated)
      localStorage.setItem(`${project.slug}:history`, JSON.stringify(updated))
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : 'Simulation failed')
    } finally { setLoading(false) }
  }

  const activeIndex = loading ? Math.min(3, project.nodes.length - 1) : -1
  const completed = result ? project.nodes.length : loading ? 2 : 0

  return (
    <main>
      <ShaderGradientBackdrop reducedMotion={reducedMotion} />
      <div className="noise" aria-hidden="true" />
      <nav className="nav glass">
        <a className="brand" href="#top"><span className="brand-dot" />{project.name}</a>
        <div><a href="#simulator">Simulator</a><a href="#system">System</a><a href="#proof">Proof</a></div>
      </nav>

      <section className="hero shell" id="top">
        <div className="hero-copy">
          <span className="eyebrow">{project.eyebrow}</span>
          <h1>{project.title}</h1>
          <p>{project.description}</p>
          <div className="hero-actions">
            <a className="button primary" href="#simulator">Run the product</a>
            <a className="button" href="https://github.com/Samadritaacharya/platformpulse-developer-platform">View source</a>
          </div>
          <div className="proof-strip">{project.proof.map((item) => <span key={item}>{item}</span>)}</div>
        </div>
        <motion.div className="scene glass" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: reducedMotion ? 0 : 0.7 }}>
          <SystemScene activeIndex={activeIndex} completed={completed} reducedMotion={reducedMotion} />
          <div className="scene-caption"><span>Live system map</span><b>{result?.status ?? 'READY'}</b></div>
        </motion.div>
      </section>

      <section className="shell section" id="simulator">
        <div className="section-heading"><span className="eyebrow">Interactive product surface</span><h2>Pressure-test the platform.</h2><p>Choose a synthetic operating scenario, adjust pressure, add context, and run the deterministic web engine.</p></div>
        <div className="sim-grid">
          <form className="glass controls" onSubmit={run}>
            <label>Scenario<select value={scenario} onChange={(e) => setScenario(e.target.value)}>{project.scenarios.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
            <p className="scenario-summary">{selected.summary}</p>
            <label>Operating pressure <span>{intensity}%</span><input type="range" min="0" max="100" value={intensity} onChange={(e) => setIntensity(Number(e.target.value))} /></label>
            <label>Context / notes<textarea value={context} onChange={(e) => setContext(e.target.value)} maxLength={4000} placeholder="Optional: describe a support spike, security concern, self-service push, or reliability issue…" /></label>
            <button className="button primary full" disabled={loading}>{loading ? 'Running evidence path…' : 'Run simulation'}</button>
            <small>Zero-key deterministic engine · synthetic scenarios · no data leaves this app</small>
          </form>

          <div className="glass output" aria-live="polite">
            {!result && !loading && <div className="empty"><span>01</span><h3>Ready for a scenario.</h3><p>The API route will return a scored decision view, signals, and prioritized interventions.</p></div>}
            {loading && <div className="empty"><span className="pulse">●</span><h3>Building the decision view…</h3><p>Normalizing evidence → scoring product health → applying guardrails.</p></div>}
            {error && <div className="error">{error}</div>}
            {result && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <div className="result-head"><div><span className={`status ${result.status.toLowerCase()}`}>{result.status}</span><h3>{result.headline}</h3></div><strong>{result.score}<small>/100</small></strong></div>
                <div className="metric-grid">{result.metrics.map((metric) => <article key={metric.label} className={`metric ${metric.tone}`}><span>{metric.label}</span><b>{metric.value}</b><small>{metric.detail}</small></article>)}</div>
                <div className="result-columns"><div><h4>Signals</h4><ul>{[...result.signals, ...result.contextSignals].map((item) => <li key={item}>{item}</li>)}</ul></div><div><h4>Next actions</h4><ol>{result.recommendations.map((item) => <li key={item}>{item}</li>)}</ol></div></div>
              </motion.div>
            )}
          </div>
        </div>
      </section>

      <section className="shell section" id="system">
        <div className="section-heading"><span className="eyebrow">System model</span><h2>From signal to decision.</h2></div>
        <div className="node-grid">{project.nodes.map((node, index) => <motion.article className="glass node" key={node} whileHover={reducedMotion ? undefined : { y: -5 }}><span>{String(index + 1).padStart(2, '0')}</span><h3>{node}</h3><p>{index === 0 ? 'Capture the operating problem.' : index === project.nodes.length - 1 ? 'Keep the control boundary visible.' : 'Transform evidence into the next measurable decision.'}</p></motion.article>)}</div>
      </section>

      <section className="shell section" id="proof">
        <div className="section-heading"><span className="eyebrow">Engineering proof</span><h2>Built to be inspectable.</h2></div>
        <div className="proof-grid"><article className="glass"><b>No paid runtime dependency</b><p>The hosted web experience requires no model key, database, login, or analytics service.</p></article><article className="glass"><b>Deterministic web backend</b><p>The same input always produces the same result, making behavior testable and portfolio-safe.</p></article><article className="glass"><b>Original Python product preserved</b><p>The existing Streamlit/product logic remains intact while this Next.js layer becomes the modern public surface.</p></article><article className="glass"><b>Local-only history</b><p>Recent runs stay in browser storage and can be cleared by the browser at any time.</p></article></div>
        {history.length > 0 && <div className="history glass"><h3>Recent local runs</h3>{history.map((item) => <div key={item.at}><span>{item.result.status}</span><b>{project.scenarios.find((s) => s.id === item.result.scenarioId)?.name}</b><em>{item.result.score}/100</em></div>)}</div>}
      </section>

      <footer className="shell"><span>{project.name}</span><p>Synthetic data · inspectable logic · governed automation</p></footer>
    </main>
  )
}
