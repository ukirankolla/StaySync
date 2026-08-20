import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Connections() {
  const navigate = useNavigate()
  const [conns, setConns] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')

  const load = () => {
    api('/matching/connections').then(setConns).catch((e) => setErr(e.message)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const respond = async (id, action) => {
    try {
      await api(`/matching/connections/${id}/respond?action=${action}`, { method: 'POST' })
      load()
    } catch (e) {
      setErr(e.message)
    }
  }

  if (loading) return <div className="page-muted">Loading connections…</div>
  if (err) return <div className="page-muted">{err}</div>

  const pending = conns.filter((c) => c.status === 'pending')
  const accepted = conns.filter((c) => c.status === 'accepted')
  const declined = conns.filter((c) => c.status === 'declined')

  const ConnectionRow = ({ c }) => (
    <div className="conn-item" style={{ display: 'flex', alignItems: 'center', gap: 14, justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1 }}>
        <div style={{
          width: 42, height: 42, borderRadius: 14,
          background: c.status === 'accepted' ? 'rgba(16, 185, 129, 0.1)' : c.status === 'pending' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem', flexShrink: 0,
        }}>
          {c.status === 'accepted' ? '✓' : c.status === 'pending' ? '⏳' : '✕'}
        </div>
        <div>
          <strong style={{ fontSize: '.95rem' }}>{c.peer_name}</strong>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 2 }}>
            <span className={`status-pill status-${c.status}`} style={{ fontSize: '.72rem' }}>{c.status}</span>
            {c.unread_count > 0 && <span className="badge" style={{ fontSize: '.7rem' }}>{c.unread_count} new</span>}
          </div>
          <div className="muted" style={{ fontSize: '.82rem', marginTop: 2 }}>{c.last_message || (c.status === 'accepted' ? 'Start chatting!' : '')}</div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        {c.status === 'pending' && (
          <>
            <button className="btn btn-success btn-sm" onClick={() => respond(c.id, 'accept')}>Accept</button>
            <button className="btn btn-ghost btn-sm" onClick={() => respond(c.id, 'decline')}>Decline</button>
          </>
        )}
        {c.status === 'accepted' && (
          <button className="btn btn-primary btn-sm" onClick={() => navigate(`/chat/${c.id}`)}>
            <span>💬</span> Chat
          </button>
        )}
      </div>
    </div>
  )

  return (
    <div>
      <h2>Connections</h2>
      <div className="live-indicator mb-16"><span className="live-dot" /> Real-time updates</div>

      <h3 className="mt-16 mb-8" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: '1.1rem' }}>⏳</span> Pending requests
        {pending.length > 0 && <span className="badge">{pending.length}</span>}
      </h3>
      {pending.length === 0 ? <p className="muted">No pending requests.</p> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {pending.map((c) => <ConnectionRow key={c.id} c={c} />)}
        </div>
      )}

      <h3 className="mt-24 mb-8" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: '1.1rem' }}>✓</span> Accepted
        {accepted.length > 0 && <span className="badge badge-green">{accepted.length}</span>}
      </h3>
      {accepted.length === 0 ? <p className="muted">No accepted connections yet.</p> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {accepted.map((c) => <ConnectionRow key={c.id} c={c} />)}
        </div>
      )}

      {declined.length > 0 && (
        <>
          <h3 className="mt-24 mb-8" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: '1.1rem' }}>✕</span> Declined
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {declined.map((c) => <ConnectionRow key={c.id} c={c} />)}
          </div>
        </>
      )}
    </div>
  )
}
