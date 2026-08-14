import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const OCCUPATIONS = ['student', 'professional', 'other']
const CITIES = ['Bengaluru', 'Mumbai', 'Delhi', 'Pune', 'Hyderabad', 'Chennai', 'Kolkata']

export default function Profile() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: '', age: '', occupation: 'student', occupation_detail: '',
    city: 'Bengaluru', preferred_area: '', budget_min: '', budget_max: '',
    move_in_date: '', bio: '', is_visible: true,
  })
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState(null)

  useEffect(() => {
    api('/profile/me').then((p) => {
      setForm({
        full_name: p.full_name || '', age: p.age || '', occupation: p.occupation || 'student',
        occupation_detail: p.occupation_detail || '', city: p.city || 'Bengaluru',
        preferred_area: p.preferred_area || '', budget_min: p.budget_min || '',
        budget_max: p.budget_max || '', move_in_date: p.move_in_date || '',
        bio: p.bio || '', is_visible: p.is_visible,
      })
    }).catch(() => {})
    api('/matching/agents/onboarding').then(setProgress).catch(() => {})
  }, [user])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const setNum = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value === '' ? '' : Number(e.target.value) }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const payload = {
        full_name: form.full_name, age: form.age === '' ? null : Number(form.age),
        occupation: form.occupation, occupation_detail: form.occupation_detail,
        city: form.city, preferred_area: form.preferred_area,
        budget_min: form.budget_min === '' ? null : Number(form.budget_min),
        budget_max: form.budget_max === '' ? null : Number(form.budget_max),
        move_in_date: form.move_in_date, bio: form.bio, is_visible: form.is_visible,
      }
      await api('/profile/me', { method: 'PUT', body: payload })
      setSaved(true)
      const p = await api('/matching/agents/onboarding')
      setProgress(p)
      setTimeout(() => setSaved(false), 2500)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-8">
      {progress && (
        <div className="card mb-16">
          <strong>Profile completion: {progress.progress}%</strong>
          <div className="q-progress mt-8"><div className="q-progress-fill" style={{ width: `${progress.progress}%` }} /></div>
          <p className="muted mb-8">{progress.tip}</p>
        </div>
      )}
      <form className="form card" onSubmit={submit} style={{ maxWidth: 640 }}>
        <h2 className="center">Your profile</h2>
        {error && <div className="alert">{error}</div>}
        {saved && <div className="alert alert-success">Saved!</div>}

        <div className="field">
          <label>Full name</label>
          <input className="input" value={form.full_name} onChange={set('full_name')} required />
        </div>

        <div className="form-row">
          <div className="field">
            <label>Age</label>
            <input className="input" type="number" min={16} max={100} value={form.age} onChange={setNum('age')} />
          </div>
          <div className="field">
            <label>Occupation</label>
            <select className="select" value={form.occupation} onChange={set('occupation')}>
              <option value="student">Student</option>
              <option value="professional">Professional</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div className="field">
          <label>Occupation detail</label>
          <input className="input" value={form.occupation_detail} onChange={set('occupation_detail')}
                 placeholder="e.g. Software Engineer, MBA student" />
        </div>

        <div className="form-row">
          <div className="field">
            <label>City</label>
            <select className="select" value={form.city} onChange={set('city')}>
              {CITIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Preferred area</label>
            <input className="input" value={form.preferred_area} onChange={set('preferred_area')}
                   placeholder="e.g. Koramangala" />
          </div>
        </div>

        <div className="form-row">
          <div className="field">
            <label>Budget min (₹/mo)</label>
            <input className="input" type="number" value={form.budget_min} onChange={setNum('budget_min')} placeholder="10000" />
          </div>
          <div className="field">
            <label>Budget max (₹/mo)</label>
            <input className="input" type="number" value={form.budget_max} onChange={setNum('budget_max')} placeholder="18000" />
          </div>
        </div>

        <div className="field">
          <label>Move-in date</label>
          <input className="input" type="date" value={form.move_in_date} onChange={set('move_in_date')} />
        </div>

        <div className="field">
          <label>About you</label>
          <textarea className="input" rows={3} value={form.bio} onChange={set('bio')}
                    placeholder="Short intro — routines, interests, what you're looking for" />
        </div>

        <label className="form-note" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input type="checkbox" checked={form.is_visible} onChange={(e) => setForm((f) => ({ ...f, is_visible: e.target.checked }))} />
          Show my profile to potential roommates
        </label>

        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Saving…' : 'Save profile'}</button>
        <button type="button" className="btn btn-ghost btn-block" onClick={() => navigate('/questionnaire')}>
          Complete lifestyle questionnaire →
        </button>
      </form>
    </div>
  )
}
