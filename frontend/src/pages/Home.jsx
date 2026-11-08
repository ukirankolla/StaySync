import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const TILES = [
  ['/discover', '🔍', 'Find roommates'],
  ['/listings', '🏢', 'Browse flats'],
  ['/groups', '👥', 'Groups'],
  ['/connections', '💬', 'Chats'],
]

export default function Home() {
  const { user } = useAuth()
  const [strength, setStrength] = useState(null)
  const [top, setTop] = useState([])
  const [unread, setUnread] = useState(0)
  const [needQ, setNeedQ] = useState(false)

  useEffect(() => {
    api('/profile/me/strength').then(setStrength).catch(() => {})
    api('/profile/questionnaire/answers').then((d) => setNeedQ(!d.completed)).catch(() => {})
    api('/matching/recommendations').then((r) => setTop(r.slice(0, 3))).catch(() => {})
    api('/matching/connections')
      .then((c) => setUnread(c.reduce((n, x) => n + (x.unread_count || 0), 0)))
      .catch(() => {})
  }, [])

  const name = (user?.full_name || user?.email || '').split(/[ @]/)[0]
  return (
    <div>
      <h2 style={{ marginBottom: 4 }}>Hi{name ? `, ${name}` : ''} 👋</h2>
      <p className="muted mb-16">Here's where you stand today.</p>

      {needQ && (
        <div className="alert alert-info mb-16">
          Finish your <Link to="/questionnaire"><strong>lifestyle profile</strong></Link> to unlock compatibility scores.
        </div>
      )}

      {strength && (
        <div className="card mb-16" style={{ padding: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.9rem' }}>
            <strong>Profile strength</strong><span>{strength.percent}%</span>
          </div>
          <div className="q-progress" style={{ margin: '8px 0' }}><div className="q-progress-fill" style={{ width: `${strength.percent}%` }} /></div>
          {strength.missing.length > 0 && (
            <Link to="/profile" className="muted" style={{ fontSize: '.8rem' }}>
              {strength.missing[0].label} (+{strength.missing[0].points}%) →
            </Link>
          )}
        </div>
      )}

      <div className="mb-16" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {TILES.map(([to, icon, label]) => (
          <Link key={to} to={to} className="card" style={{ textAlign: 'center', padding: 18, textDecoration: 'none' }}>
            <div style={{ fontSize: '1.8rem' }} aria-hidden="true">{icon}</div>
            <strong>{label}</strong>
            {to === '/connections' && unread > 0 && <span className="badge" style={{ marginLeft: 6 }}>{unread}</span>}
          </Link>
        ))}
      </div>

      {top.length > 0 && (
        <>
          <h3 className="mb-8">Top matches for you</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {top.map((m) => (
              <Link key={m.user_id} to="/discover" className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 14, textDecoration: 'none' }}>
                <span><strong>{m.full_name}</strong><span className="muted"> · {m.city}</span></span>
                <span className="score-badge">{m.score != null ? `${Math.round(m.score)}%` : '—'}</span>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
