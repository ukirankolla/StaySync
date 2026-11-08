import React, { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const OCCUPATIONS = ['student', 'professional', 'other']
const PRIVACY_FIELDS = [
  ['age', 'my age'],
  ['occupation', 'my occupation'],
  ['budget', 'my budget'],
  ['bio', 'my bio'],
  ['move_in_date', 'my move-in date'],
  ['photos', 'my photos'],
  ['lifestyle', 'my lifestyle badges'],
]

export default function Profile() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [strength, setStrength] = useState(null)
  const [delOpen, setDelOpen] = useState(false)
  const [delText, setDelText] = useState('')
  const [delBusy, setDelBusy] = useState(false)
  const [delErr, setDelErr] = useState('')
  const [form, setForm] = useState({
    full_name: '', age: '', occupation: 'student', occupation_detail: '',
    city: '', preferred_area: '', budget_min: '', budget_max: '',
    move_in_date: '', bio: '', is_visible: true, photos: [],
    privacy: {},
  })
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [pw, setPw] = useState({ current_password: '', new_password: '' })
  const [pwMsg, setPwMsg] = useState('')

  useEffect(() => {
    api('/profile/me/strength').then(setStrength).catch(() => {})
  }, [saved])

  useEffect(() => {
    api('/profile/me').then((p) => {
      setForm({
        full_name: p.full_name || '', age: p.age || '', occupation: p.occupation || 'student',
        occupation_detail: p.occupation_detail || '', city: p.city || '',
        preferred_area: p.preferred_area || '', budget_min: p.budget_min || '',
        budget_max: p.budget_max || '', move_in_date: p.move_in_date || '',
        bio: p.bio || '', is_visible: p.is_visible, photos: p.photos || [],
        privacy: p.privacy || {},
      })
    }).catch(() => {})
    api('/matching/agents/onboarding').then(setProgress).catch(() => {})
  }, [user])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const setNum = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value === '' ? '' : Number(e.target.value) }))

  const uploadPhoto = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true); setError('')
    try {
      const fd = new FormData(); fd.append('file', file)
      const res = await fetch('/api/upload/image', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('staysync_token')}` },
        body: fd,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Upload failed')
      setForm((f) => ({ ...f, photos: [...(f.photos || []), data.url] }))
    } catch (err2) { setError(err2.message) } finally { setUploading(false); e.target.value = '' }
  }

  const removePhoto = (url) => setForm((f) => ({ ...f, photos: (f.photos || []).filter((p) => p !== url) }))

  const changePassword = async (e) => {
    e.preventDefault(); setPwMsg('')
    try {
      await api('/auth/change-password', { method: 'POST', body: pw })
      setPwMsg('Password updated'); setPw({ current_password: '', new_password: '' })
    } catch (err) { setPwMsg(err.message) }
  }

  const submit = async (e) => {
    e.preventDefault(); setError(''); setBusy(true)
    try {
      const payload = {
        full_name: form.full_name, age: form.age === '' ? null : Number(form.age),
        occupation: form.occupation, occupation_detail: form.occupation_detail,
        city: form.city, preferred_area: form.preferred_area,
        budget_min: form.budget_min === '' ? null : Number(form.budget_min),
        budget_max: form.budget_max === '' ? null : Number(form.budget_max),
        move_in_date: form.move_in_date, bio: form.bio, is_visible: form.is_visible,
        photos: form.photos || [], privacy: form.privacy || {},
      }
      await api('/profile/me', { method: 'PUT', body: payload })
      setSaved(true)
      const p = await api('/matching/agents/onboarding'); setProgress(p)
      setTimeout(() => setSaved(false), 2500)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const deleteAccount = async () => {
    setDelBusy(true); setDelErr('')
    try {
      await api('/auth/me', { method: 'DELETE', body: { confirm: delText } })
      logout(); navigate('/')
    } catch (e) { setDelErr(e.message) } finally { setDelBusy(false) }
  }

  return (
    <div className="mt-8">
      {/* Progress */}
      {progress && (
        <div className="card mb-16">
          <strong style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📊</span> Profile completion: {progress.progress}%
          </strong>
          <div className="q-progress mt-8"><div className="q-progress-fill" style={{ width: `${progress.progress}%` }} /></div>
          <p className="muted mb-8">{progress.tip}</p>
        </div>
      )}

      {/* Profile Form */}
      <form className="form card" onSubmit={submit} style={{ maxWidth: 640 }}>
        <h2 className="center">Your profile</h2>
        {strength && (
          <div className="mb-16">
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.88rem' }}>
              <strong>Profile strength</strong><span>{strength.percent}%</span>
            </div>
            <div className="q-progress" style={{ margin: '6px 0' }}><div className="q-progress-fill" style={{ width: `${strength.percent}%` }} /></div>
            {strength.missing.length > 0 && (
              <div className="muted" style={{ fontSize: '.8rem' }}>
                To improve: {strength.missing.map((x) => `${x.label} (+${x.points}%)`).join(', ')}
              </div>
            )}
          </div>
        )}
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
            <label>City / State / Country</label>
            <input className="input" value={form.city} onChange={set('city')} placeholder="Anywhere" />
          </div>
          <div className="field">
            <label>Preferred area</label>
            <input className="input" value={form.preferred_area} onChange={set('preferred_area')} placeholder="e.g. Koramangala" />
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
        <div className="field">
          <label>Photos</label>
          {form.photos?.length > 0 && (
            <div className="photo-strip mb-8">
              {form.photos.map((p) => (
                <div key={p} style={{ position: 'relative' }}>
                  <img src={p} alt="" className="photo-thumb" />
                  <button type="button" onClick={() => removePhoto(p)}
                          style={{ position: 'absolute', top: -6, right: -6, borderRadius: '50%', background: 'var(--danger)', color: '#fff', border: 'none', width: 22, height: 22, cursor: 'pointer', fontSize: '.7rem' }}>×</button>
                </div>
              ))}
            </div>
          )}
          <div className="photo-upload">
            <input type="file" accept="image/jpeg,image/png,image/webp" onChange={uploadPhoto}
                   disabled={uploading} className="input" style={{ width: 'auto' }} />
            {uploading && <span className="muted">Uploading…</span>}
          </div>
        </div>
        <label className="form-note" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input type="checkbox" checked={form.is_visible} onChange={(e) => setForm((f) => ({ ...f, is_visible: e.target.checked }))} />
          Show my profile to potential roommates
        </label>
        <hr className="mt-16 mb-16" />
        <strong>Privacy — what others can see about you</strong>
        <p className="muted mb-8" style={{ fontSize: '.85rem' }}>You always control your info.</p>
        <div className="grid grid-2">
          {PRIVACY_FIELDS.map(([key, label]) => (
            <label key={key} className="form-note" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input type="checkbox" checked={form.privacy[key] !== false}
                     onChange={(e) => setForm((f) => ({ ...f, privacy: { ...f.privacy, [key]: e.target.checked } }))} />
              Show {label}
            </label>
          ))}
        </div>
        <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Saving…' : 'Save profile'}</button>
        <button type="button" className="btn btn-ghost btn-block" onClick={() => navigate('/questionnaire')}>
          🤖 Complete lifestyle questionnaire →
        </button>
      </form>

      {/* Password */}
      <form className="card mt-16" style={{ maxWidth: 640 }} onSubmit={changePassword}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><span>🔑</span> Change password</h3>
        {pwMsg && <div className={pwMsg.includes('updated') ? 'alert alert-success' : 'alert'}>{pwMsg}</div>}
        <div className="form-row">
          <div className="field">
            <label>Current password</label>
            <input className="input" type="password" value={pw.current_password}
                   onChange={(e) => setPw({ ...pw, current_password: e.target.value })} required />
          </div>
          <div className="field">
            <label>New password</label>
            <input className="input" type="password" value={pw.new_password}
                   onChange={(e) => setPw({ ...pw, new_password: e.target.value })} required minLength={8} />
          </div>
        </div>
        <button className="btn btn-sm">Update password</button>
      </form>

      {/* Account deletion: required by the App Store / Google Play */}
      <div className="card mt-16" style={{ borderColor: 'rgba(239, 68, 68, 0.35)' }}>
        <strong>Delete account</strong>
        <p className="muted mt-8" style={{ fontSize: '.88rem' }}>
          Permanently erases your profile, matches, chats and group memberships, and takes your listings down. This can't be undone.
        </p>
        {!delOpen ? (
          <button type="button" className="btn btn-ghost btn-sm mt-8" style={{ color: '#fca5a5' }} onClick={() => setDelOpen(true)}>
            Delete my account…
          </button>
        ) : (
          <div className="mt-8" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <input className="input" style={{ flex: 1, minWidth: 160 }} placeholder='Type DELETE to confirm'
                   value={delText} onChange={(e) => setDelText(e.target.value)} autoCapitalize="characters" />
            <button type="button" className="btn btn-sm" style={{ background: '#dc2626', color: '#fff' }}
                    disabled={delBusy || delText.trim().toUpperCase() !== 'DELETE'} onClick={deleteAccount}>
              {delBusy ? 'Deleting…' : 'Delete forever'}
            </button>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setDelOpen(false); setDelText(''); setDelErr('') }}>Cancel</button>
          </div>
        )}
        {delErr && <div className="alert mt-8">{delErr}</div>}
      </div>

      {/* Phones have no top nav links: account actions live here */}
      <div className="card mt-16 mobile-only" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <Link to="/hostels" className="btn btn-ghost btn-block">College / hostel allocation</Link>
        {user?.role === 'admin' && <Link to="/admin" className="btn btn-ghost btn-block">Admin dashboard</Link>}
        <button type="button" className="btn btn-ghost btn-block" onClick={() => { logout(); navigate('/') }}>Log out</button>
      </div>
    </div>
  )
}
