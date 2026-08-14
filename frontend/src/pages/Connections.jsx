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

  const Row = ({ c }) => (
    <div className="conn-item" style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'space-between' }}>
      <div>
        <strong>{c.peer_name}</strong>
        <span className={`status-pill status-${c.status}`} style={{ marginLeft: 8 }}>{c.status}</span>
        <div className="muted" style={{ fontSize: '.85rem' }}>{c.last_message || (c.status === 'accepted' ? 'Start chatting!' : '')}</div>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        {c.status === 'pending' && (
          <>
            <button className="btn btn-success btn-sm" onClick={() => respond(c.id, 'accept')}>Accept</button>
            <button className="btn btn-ghost btn-sm" onClick={() => respond(c.id, 'decline')}>Decline</button>
          </>
        )}
        {c.status === 'accepted' && (
          <button className="btn btn-primary btn-sm" onClick={() => navigate(`/chat/${c.id}`)}>Chat</button>
        )}
      </div>
    </div>
  )

  return (
    <div>
      <h2>Connections</h2>
      <h3 className="mt-16 mb-8">Pending requests</h3>
      {pending.length === 0 ? <p className="muted">No pending requests.</p> : pending.map((c) => <Row key={c.id} c={c} />)}

      <h3 className="mt-24 mb-8">Accepted</h3>
      {accepted.length === 0 ? <p className="muted">No accepted connections yet.</p> : accepted.map((c) => <Row key={c.id} c={c} />)}

      {declined.length > 0 && (
        <>
          <h3 className="mt-24 mb-8">Declined</h3>
          {declined.map((c) => <Row key={c.id} c={c} />)}
        </>
      )}
    </div>
  )
}
