import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Connections() {
  const navigate = useNavigate()
  const [conns, setConns] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')
  const [fb, setFb] = useState({})        // connection_id -> saved feedback
  const [fbOpen, setFbOpen] = useState(null)
  const [fbForm, setFbForm] = useState({ fits: true, outcome: 'talking', comment: '' })

  const [rv, setRv] = useState({})        // connection_id -> my review
  const [rvOpen, setRvOpen] = useState(null)
  const [rvForm, setRvForm] = useState({ rating: 5, would_live_again: true, comment: '' })

  const saveReview = async (id) => {
    try {
      await api('/reviews', { method: 'POST', body: { connection_id: id, ...rvForm, comment: rvForm.comment || null } })
      setRv({ ...rv, [id]: { rating: rvForm.rating, would_live_again: rvForm.would_live_again } })
      setRvOpen(null)
      setErr('')
    } catch (e) { setErr(e.message) }
  }

  const saveFeedback = async (id) => {
    try {
      await api('/feedback', { method: 'POST', body: { connection_id: id, ...fbForm, comment: fbForm.comment || null } })
      setFb({ ...fb, [id]: { fits: fbForm.fits, outcome: fbForm.outcome } })
      setFbOpen(null)
    } catch (e) { setErr(e.message) }
  }

  const load = () => {
    api('/reviews/mine').then(setRv).catch(() => {})
    api('/feedback/mine').then(setFb).catch(() => {})
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
          <>
            <button className="btn btn-ghost btn-sm" onClick={() => { setFbOpen(fbOpen === c.id ? null : c.id); setFbForm({ fits: fb[c.id]?.fits ?? true, outcome: fb[c.id]?.outcome ?? 'talking', comment: '' }) }}>
              {fb[c.id] ? 'Edit feedback' : 'Give feedback'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={() => { setRvOpen(rvOpen === c.id ? null : c.id); setRvForm({ rating: rv[c.id]?.rating ?? 5, would_live_again: rv[c.id]?.would_live_again ?? true, comment: '' }) }}>
              {rv[c.id] ? `★ ${rv[c.id].rating} · Edit review` : '☆ Review'}
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => navigate(`/chat/${c.id}`)}>
              <span>💬</span> Chat
            </button>
          </>
        )}
      </div>
    </div>
  )

  const FeedbackForm = ({ c }) => (
    <div className="card" style={{ margin: '-4px 0 8px' }}>
      <strong style={{ fontSize: '.9rem' }}>Did {c.peer_name} fit what you were looking for?</strong>
      <div style={{ display: 'flex', gap: 8, margin: '8px 0' }}>
        <button type="button" className={`btn btn-sm ${fbForm.fits ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setFbForm({ ...fbForm, fits: true })}>Yes</button>
        <button type="button" className={`btn btn-sm ${!fbForm.fits ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setFbForm({ ...fbForm, fits: false })}>Not really</button>
      </div>
      <select className="select" value={fbForm.outcome} onChange={(e) => setFbForm({ ...fbForm, outcome: e.target.value })}>
        <option value="talking">We're chatting</option>
        <option value="viewing">We're viewing places together</option>
        <option value="living_together">We decided to live together</option>
        <option value="not_continuing">Not continuing</option>
      </select>
      <input className="input mt-8" maxLength={1000} placeholder="Anything else? (optional)" value={fbForm.comment} onChange={(e) => setFbForm({ ...fbForm, comment: e.target.value })} />
      <button className="btn btn-primary btn-sm mt-8" onClick={() => saveFeedback(c.id)}>Save</button>
    </div>
  )

  const ReviewForm = ({ c }) => (
    <div className="card" style={{ margin: '-4px 0 8px' }}>
      <strong style={{ fontSize: '.9rem' }}>Review {c.peer_name}</strong>
      <p className="muted" style={{ fontSize: '.78rem', margin: '2px 0 8px' }}>Shown on their profile. You can review only after you have both exchanged messages.</p>
      <div style={{ display: 'flex', gap: 4 }}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button key={n} type="button" className={`btn btn-sm ${rvForm.rating >= n ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setRvForm({ ...rvForm, rating: n })}>★</button>
        ))}
      </div>
      <label className="form-note" style={{ display: 'flex', gap: 8, alignItems: 'center', margin: '8px 0' }}>
        <input type="checkbox" checked={rvForm.would_live_again} onChange={(e) => setRvForm({ ...rvForm, would_live_again: e.target.checked })} />
        Would live together again
      </label>
      <input className="input" maxLength={500} placeholder="A line about them (optional)" value={rvForm.comment} onChange={(e) => setRvForm({ ...rvForm, comment: e.target.value })} />
      <button className="btn btn-primary btn-sm mt-8" onClick={() => saveReview(c.id)}>Save review</button>
    </div>
  )

  return (
    <div>
      <h2>Connections</h2>
      {err && <div className="alert mb-16">{err}</div>}
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
          {accepted.map((c) => (<React.Fragment key={c.id}><ConnectionRow c={c} />{fbOpen === c.id && <FeedbackForm c={c} />}{rvOpen === c.id && <ReviewForm c={c} />}</React.Fragment>))}
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
