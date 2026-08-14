import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Questionnaire() {
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [answers, setAnswers] = useState({})
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    api('/profile/questionnaire').then(setData).catch((e) => setErr(e.message))
    api('/profile/questionnaire/answers')
      .then((r) => setAnswers(r.answers || {}))
      .catch(() => {})
  }, [])

  const total = data?.questions.length || 1
  const answered = Object.keys(answers).filter((k) => answers[k] !== '' && answers[k] != null).length
  const progress = Math.round((answered / total) * 100)

  const choose = (key, value) => setAnswers((a) => ({ ...a, [key]: value }))

  const submit = async () => {
    setBusy(true)
    setMsg('')
    setErr('')
    try {
      await api('/profile/questionnaire', { method: 'PUT', body: { answers } })
      setMsg('Questionnaire saved! Your matches are now active.')
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
      <h2 className="center">Lifestyle questionnaire</h2>
      <p className="center muted">Honest answers give you honest matches.</p>

      <div className="q-progress"><div className="q-progress-fill" style={{ width: `${progress}%` }} /></div>
      <div className="weights-table">
        <table className="center" style={{ margin: '0 auto' }}>
          <tbody>
            {Object.entries(data.weights).map(([k, v]) => (
              <tr key={k}><td>{k.replace(/_/g, ' ')}</td><td>{v}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        {data.questions.map((q) => (
          <div className="q-question" key={q.key}>
            <h3>{q.label}</h3>
            {q.type === 'scale' ? (
              <>
                <div className="q-scale">
                  {Array.from({ length: q.max - q.min + 1 }, (_, i) => q.min + i).map((n) => (
                    <div key={n} className={`q-option ${Number(answers[q.key]) === n ? 'selected' : ''}`}
                         onClick={() => choose(q.key, n)}>
                      {n}
                    </div>
                  ))}
                </div>
                <div className="range-row"><span>{q.hints[0]}</span><span>{q.hints[1]}</span></div>
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
        <button className="btn btn-primary btn-block" disabled={busy} onClick={submit}>
          {busy ? 'Saving…' : `Save answers (${answered}/${total})`}
        </button>
      </div>
    </div>
  )
}
