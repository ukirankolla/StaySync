import React, { useState } from 'react'
import { api } from '../api/client'
import Avatar from './Avatar'

export default function MatchCard({ match, onAction, onViewProfile }) {
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

  const scoreColor = match.score >= 80 ? 'var(--gradient-cool)' : match.score >= 60 ? 'var(--gradient)' : 'var(--gradient-warm)'

  return (
    <div className="card match-card">
      {match.photos?.length > 0 && (
        <img className="match-photo" src={match.photos[0]} alt={match.full_name} loading="lazy" />
      )}
      <div className="match-head">
        <Avatar name={match.full_name} photo={match.photos?.[0]} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <strong style={{ fontSize: '1rem' }}>{match.full_name}</strong>
            {match.is_id_verified && <span className="badge badge-green" title="Government ID verified" style={{ fontSize: '.65rem' }}>ID ✓</span>}
            {!match.is_id_verified && match.is_verified && <span className="badge" style={{ fontSize: '.65rem' }}>verified</span>}
          </div>
          <div className="muted" style={{ fontSize: '.83rem', marginTop: 2 }}>
            {match.age && `${match.age} · `}{match.occupation && match.occupation.replace('_', ' ')} · {match.city}
          </div>
        </div>
        <div className="score-badge" style={{ background: scoreColor }}>{Math.round(match.score)}%</div>
      </div>

      <div className="match-meta">
        {match.budget_min && <span className="chip">₹{match.budget_min.toLocaleString('en-IN')}+/mo</span>}
        {match.preferred_area && <span className="chip chip-gray">{match.preferred_area}</span>}
        {match.move_in_date && <span className="chip chip-gray">moves {match.move_in_date}</span>}
      </div>

      {match.bio && <p className="muted" style={{ fontSize: '.87rem', margin: 0, lineHeight: 1.5 }}>{match.bio}</p>}

      <div className="reasons">
        {match.reasons.slice(0, 4).map((r, i) => <div className="reason" key={i}>{r}</div>)}
      </div>

      {err && <div className="alert">{err}</div>}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <button className="btn btn-primary btn-sm" disabled={busy} onClick={connect}>
          {busy ? 'Connecting…' : '🔗 Connect'}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={() => onViewProfile?.(match.user_id)}>View profile</button>
        <button className="btn btn-ghost btn-sm" onClick={report} title="Report">Report</button>
        <button className="btn btn-ghost btn-sm" onClick={block} title="Block">Block</button>
      </div>
    </div>
  )
}
