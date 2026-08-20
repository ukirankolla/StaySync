import React, { useEffect, useState } from 'react'
import { api } from '../api/client'
import Avatar from './Avatar'

const CATEGORY_LABELS = {
  lifestyle: 'Lifestyle',
  sleep_noise: 'Sleep & noise',
  budget_location: 'Budget & location',
  cleanliness: 'Cleanliness',
  routine: 'Routine',
  social: 'Social',
}

export default function ProfileModal({ userId, onClose, onConnected }) {
  const [profile, setProfile] = useState(null)
  const [score, setScore] = useState(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api(`/profile/${userId}`).then(setProfile).catch((e) => setErr(e.message))
    api(`/matching/score/${userId}`).then(setScore).catch(() => {})
  }, [userId])

  const connect = async () => {
    setBusy(true)
    setErr('')
    try {
      await api('/matching/connect', { method: 'POST', body: { recipient_id: userId } })
      onConnected?.()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  const report = async () => {
    const reason = prompt('Reason for reporting this profile?', 'Fake profile')
    if (!reason) return
    try {
      await api('/moderation/report', { method: 'POST', body: { target_type: 'user', target_user_id: userId, reason } })
      alert('Report submitted. Our moderation team will review it.')
    } catch (e) {
      alert(e.message)
    }
  }

  const block = async () => {
    if (!confirm(`Block ${profile?.full_name || 'this user'}?`)) return
    try {
      await api('/moderation/block', { method: 'POST', body: { user_id: userId } })
      onConnected?.('blocked', userId)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <Avatar name={profile?.full_name} photo={profile?.photos?.[0]} size={56} />
            <div>
              <h3 style={{ margin: 0 }}>{profile?.full_name || 'Profile'}</h3>
              {profile?.is_id_verified && <span className="badge badge-green" title="Government ID verified">ID verified</span>}
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {err && <div className="alert">{err}</div>}
        {!profile && !err && <p className="muted">Loading profile…</p>}

        {profile && (
          <>
            {profile.photos.length > 0 && (
              <div className="photo-strip" style={{ marginTop: 16 }}>
                {profile.photos.map((p, i) => <img key={i} src={p} alt="" className="photo-thumb" />)}
              </div>
            )}
            <div className="match-meta mt-8">
              {profile.age && <span className="chip">{profile.age} yrs</span>}
              {profile.occupation && <span className="chip chip-gray">{profile.occupation}</span>}
              {profile.occupation_detail && <span className="chip chip-gray">{profile.occupation_detail}</span>}
              <span className="chip chip-gray">{profile.city}</span>
              {profile.preferred_area && <span className="chip chip-gray">{profile.preferred_area}</span>}
            </div>
            {profile.budget_min != null && (
              <p className="muted mt-8">Budget ₹{profile.budget_min.toLocaleString('en-IN')}–{profile.budget_max?.toLocaleString('en-IN')}/mo · moves {profile.move_in_date || 'flexible'}</p>
            )}
            {profile.bio && <p className="mt-8" style={{ lineHeight: 1.6 }}>{profile.bio}</p>}

            {score && (
              <div className="mt-16">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span>🧠</span> AI Compatibility
                  </h4>
                  <span className="score-badge">{Math.round(score.score)}%</span>
                </div>
                <div className="breakdown mt-8">
                  {Object.entries(score.category_scores || {}).map(([key, val]) => (
                    <div key={key} className="breakdown-row">
                      <span style={{ width: 130, color: 'var(--text-muted)' }}>{CATEGORY_LABELS[key] || key}</span>
                      <div className="breakdown-bar"><div style={{ width: `${val}%` }} /></div>
                      <span className="muted" style={{ width: 44, textAlign: 'right', fontWeight: 600 }}>{Math.round(val)}%</span>
                    </div>
                  ))}
                </div>
                <div className="reasons mt-8">
                  {(score.reasons || []).map((r, i) => <div className="reason" key={i}>{r}</div>)}
                </div>
                {score.explanation?.summary && (
                  <div style={{ marginTop: 12, padding: '12px 16px', background: 'rgba(99, 102, 241, 0.06)', borderRadius: 12, fontSize: '.85rem', color: 'var(--text-muted)' }}>
                    🤖 {score.explanation.summary}
                  </div>
                )}
              </div>
            )}

            <div style={{ display: 'flex', gap: 10, marginTop: 22, flexWrap: 'wrap' }}>
              <button className="btn btn-primary btn-sm" disabled={busy} onClick={connect}>
                {busy ? 'Connecting…' : '🔗 Connect'}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={report}>Report</button>
              <button className="btn btn-ghost btn-sm" onClick={block}>Block</button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
