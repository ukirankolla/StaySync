import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Questionnaire() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [answers, setAnswers] = useState({})
  const [step, setStep] = useState(1)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/profile/questionnaire').then(setData).catch((e) => setErr(e.message))
    api('/profile/questionnaire/answers')
      .then((r) => setAnswers(r.answers || {}))
      .catch(() => {})
  }, [])

  const optional = new Set(['personality', 'fitness', 'study_hours'])
  const questions = data?.questions || []
  const total = questions.length || 1
  const answered = Object.keys(answers).filter((k) => answers[k] !== '' && answers[k] != null).length
  const progress = Math.round((answered / total) * 100)
  const stepQs = questions.filter((q) => (q.step || 1) === step)
  const stepMissing = stepQs.filter((q) => !optional.has(q.key) && (answers[q.key] === '' || answers[q.key] == null))

  const choose = (key, value) => setAnswers((a) => ({ ...a, [key]: value }))

  const next = () => {
    if (stepMissing.length) { setErr(`Please answer: ${stepMissing.map((q) => q.label).join(', ')}`); return }
    setErr('')
    setStep(2)
    window.scrollTo?.(0, 0)
  }

  const submit = async () => {
    if (stepMissing.length) { setErr(`Please answer: ${stepMissing.map((q) => q.label).join(', ')}`); return }
    setBusy(true)
    setMsg('')
    setErr('')
    try {
      await api('/profile/questionnaire', { method: 'PUT', body: { answers } })
      setMsg('Lifestyle profile saved! Your matches are now active.')
      setTimeout(() => navigate('/discover'), 900)
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  if (!data) return <div className="page-muted">{err || 'Loading questionnaire…'}</div>

  return (
    <div className="q-card">
      <h2 className="center">Lifestyle profile</h2>
      <p className="center muted">Step {step} of 2 · honest answers give honest matches. You can edit them any time.</p>

      <div className="q-progress"><div className="q-progress-fill" style={{ width: `${step === 1 ? 50 : 100}%` }} /></div>
      <div className="center muted" style={{ fontSize: '.85rem', marginBottom: 20 }}>
        {answered}/{total} answered — {progress}% complete
      </div>

      <div className="card" style={{ padding: 28 }}>
        {stepQs.map((q) => (
          <div className="q-question" key={q.key}>
            <h3>
              {q.icon && <span style={{ marginRight: 8 }}>{q.icon}</span>}
              {q.label}
              {optional.has(q.key) && <span className="muted" style={{ fontSize: '.8rem', marginLeft: 8 }}>(optional)</span>}
            </h3>
            {q.type === 'scale' ? (
              <>
                <div className="q-scale">
                  {Array.from({ length: q.max - q.min + 1 }, (_, i) => q.min + i).map((n, i) => (
                    <div key={n} className={`q-option ${Number(answers[q.key]) === n ? 'selected' : ''}`}
                         onClick={() => choose(q.key, n)}>
                      {q.labels?.[i] || n}
                    </div>
                  ))}
                </div>
                {!q.labels && <div className="range-row"><span>{q.hints?.[0]}</span><span>{q.hints?.[1]}</span></div>}
              </>
            ) : (
              <div className="q-options">
                {q.options.map((opt) => (
                  <div key={opt} className={`q-option ${answers[q.key] === opt ? 'selected' : ''}`}
                       onClick={() => choose(q.key, opt)}>
                    {opt}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {msg && <div className="alert alert-success">{msg}</div>}
        {err && <div className="alert">{err}</div>}
        {step === 1 ? (
          <button className="btn btn-primary btn-block" onClick={next}>Continue →</button>
        ) : (
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-outline" onClick={() => { setErr(''); setStep(1) }}>← Back</button>
            <button className="btn btn-primary btn-block" disabled={busy} onClick={submit}>
              {busy ? 'Saving…' : 'Save & activate matching'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
