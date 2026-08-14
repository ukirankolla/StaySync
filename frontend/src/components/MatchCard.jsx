import React, { useState } from 'react'
import { api } from '../api/client'
import { useNavigate } from 'react-router-dom'

export default function MatchCard({ match, onAction }) {
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const connect = async () => {
    setBusy(true)
    setErr('')
    try {
      await api('/matching/connect', { method: 'POST', body: { recipient_id: match.user_id } })
      onAction('connected', match.user_id)
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
      await api('/moderation/report', {
        method: 'POST',
        body: { target_type: 'user', target_user_id: match.user_id, reason },
      })
      alert('Report submitted. Our moderation team will review it.')
    } catch (e) {
      alert(e.message)
    }
  }

  const block = async () => {
    if (!confirm(`Block ${match.full_name}? You won't see them or be able to chat.`)) return
    try {
      await api('/moderation/block', { method: 'POST', body: { user_id: match.user_id } })
      onAction('blocked', match.user_id)
    } catch (e) {
      alert(e.message)
    }
  }

  const initials = (match.full_name || 'U').split(' ').map((s) => s[0]).slice(0, 2).join('').toUpperCase()

  return (
    <div className="card match-card">
      <div className="match-head">
        <div className="avatar">{initials}</div>
        <div>
          <strong>{match.full_name}</strong>
          {match.is_verified && <span className="badge" style={{ marginLeft: 6 }}>verified</span>}
          <div className="muted" style={{ fontSize: '.85rem' }}>
            {match.age && `${match.age} · `}{match.occupation && match.occupation.replace('_', ' ')} · {match.city}
          </div>
        </div>
        <div className="score-badge">{Math.round(match.score)}%</div>
      </div>

      <div className="match-meta">
        {match.budget_min && <span className="chip">₹{match.budget_min.toLocaleString('en-IN')}+/mo</span>}
        {match.preferred_area && <span className="chip chip-gray">{match.preferred_area}</span>}
        {match.move_in_date && <span className="chip chip-gray">moves {match.move_in_date}</span>}
        {match.ml_score != null && <span className="chip chip-green">ML {Math.round(match.ml_score)}</span>}
      </div>

      {match.bio && <p className="muted" style={{ fontSize: '.88rem', margin: 0 }}>{match.bio}</p>}

      <div className="reasons">
        {match.reasons.slice(0, 4).map((r, i) => <div className="reason" key={i}>{r}</div>)}
      </div>

      {err && <div className="alert">{err}</div>}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button className="btn btn-primary btn-sm" disabled={busy} onClick={connect}>
          {busy ? 'Connecting…' : 'Connect'}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate(`/chat/new`)} disabled>View profile</button>
        <button className="btn btn-ghost btn-sm" onClick={report} title="Report">Report</button>
        <button className="btn btn-ghost btn-sm" onClick={block} title="Block">Block</button>
      </div>
    </div>
  )
}
