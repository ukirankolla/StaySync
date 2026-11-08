import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import MatchCard from '../components/MatchCard'
import ProfileModal from '../components/ProfileModal'

export default function Discover() {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState('')
  const [notice, setNotice] = useState('')
  const [blocked, setBlocked] = useState(new Set())
  const [connected, setConnected] = useState(new Set())
  const [viewing, setViewing] = useState(null)
  const [filters, setFilters] = useState({ area: '', maxBudget: '', sort: 'score' })
  const [applied, setApplied] = useState(null)
  const [needQuestionnaire, setNeedQuestionnaire] = useState(false)

  useEffect(() => {
    api('/profile/questionnaire/answers')
      .then((d) => setNeedQuestionnaire(!d.completed))
      .catch(() => setNeedQuestionnaire(true))
  }, [])

  useEffect(() => {
    const params = new URLSearchParams()
    if (applied?.area) params.set('area', applied.area)
    if (applied?.maxBudget) params.set('max_budget', applied.maxBudget)
    const qs = params.toString()
    api(`/matching/recommendations${qs ? `?${qs}` : ''}`)
      .then(setMatches)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false))
    api('/moderation/blocked')
      .then((ids) => setBlocked(new Set(ids)))
      .catch(() => {})
    api('/matching/connections')
      .then((conns) => setConnected(new Set(conns.filter((c) => ['pending', 'accepted'].includes(c.status)).map((c) => c.peer_id))))
      .catch(() => {})
  }, [applied])

  const handleAction = (type, userId) => {
    if (type === 'connected') {
      setConnected((s) => new Set(s).add(userId))
      setNotice('Connection request sent!')
      setTimeout(() => setNotice(''), 3000)
    }
    if (type === 'blocked') {
      setBlocked((s) => new Set(s).add(userId))
      setNotice('User blocked.')
      setTimeout(() => setNotice(''), 3000)
    }
  }

  const visible = matches.filter((m) => !blocked.has(m.user_id))
  const sorted = [...visible].sort((a, b) => {
    if (filters.sort === 'score') return (b.score ?? -1) - (a.score ?? -1)
    if (filters.sort === 'budget') return (a.budget_min || 0) - (b.budget_min || 0)
    return ((b.score ?? -1) - (a.score ?? -1))
  })
  const fallback = visible.find((m) => m.is_fallback)

  if (loading) return (
    <div className="page-muted">
      <div style={{ fontSize: '2.5rem', marginBottom: 16 }}>🧠</div>
      <div style={{ marginBottom: 12 }}>AI is analyzing compatibility…</div>
      <div className="typing-indicator" style={{ margin: '0 auto' }}>
        <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
      </div>
    </div>
  )
  if (err) return <div className="page-muted">{err}</div>

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ marginBottom: 4 }}>Discover matches</h2>
          <div className="live-indicator">
            <span className="live-dot" /> AI-powered recommendations
          </div>
        </div>
        <Link to="/questionnaire" className="btn btn-ghost btn-sm">Update questionnaire</Link>
      </div>
      <p className="muted mb-16">Ranked by AI compatibility score. Transparency first — every score comes with reasons.</p>

      <div className="card mb-16 filter-bar">
        <div className="field">
          <label>Location</label>
          <input className="input" placeholder="e.g. Delhi, Hyderabad, Koramangala" value={filters.area}
                 onChange={(e) => setFilters({ ...filters, area: e.target.value })} />
        </div>
        <div className="field">
          <label>Max budget (₹/mo)</label>
          <input className="input" type="number" placeholder="15000" value={filters.maxBudget}
                 onChange={(e) => setFilters({ ...filters, maxBudget: e.target.value })} />
        </div>
        <div className="field">
          <label>Sort by</label>
          <select className="select" value={filters.sort} onChange={(e) => setFilters({ ...filters, sort: e.target.value })}>
            <option value="score">Best compatibility</option>
            <option value="score">Compatibility score</option>
            <option value="budget">Lowest budget</option>
          </select>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setApplied({ area: filters.area, maxBudget: filters.maxBudget })}>
          <span>🔍</span> Apply
        </button>
        <button className="btn btn-ghost btn-sm" onClick={() => { setFilters({ area: '', maxBudget: '', sort: 'score' }); setApplied(null) }}>Reset</button>
      </div>

      {notice && <div className="alert alert-success mb-16">{notice}</div>}
      {fallback && <div className="alert mb-16">{fallback.fallback_note}</div>}
      {needQuestionnaire && (
        <div className="alert alert-info mb-16">
          Complete your{' '}
          <Link to="/questionnaire">lifestyle questionnaire</Link> to see compatibility scores for each person.
        </div>
      )}

      {sorted.length === 0 ? (
        <div className="empty">
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>🔍</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 8 }}>No members found here yet</div>
          <p>StaySync only shows real members. Try a nearby city, or invite friends to join.</p>
          {matches.length === 0 && (
            <p>Complete your profile and lifestyle questionnaire to unlock personalised recommendations.</p>
          )}
          <p>
            <Link to="/questionnaire" className="btn btn-primary btn-sm mt-8">Complete questionnaire</Link>
          </p>
        </div>
      ) : (
        <>
        <p className="muted" style={{ fontSize: '.8rem', margin: '0 0 12px' }}>
          Scores are recommendations, not guarantees. Read the reasons, chat, and agree on expectations before you decide.
        </p>
        <div className="grid grid-2">
          {sorted.map((m) => (
            <MatchCard key={m.user_id} match={m} onAction={handleAction} onViewProfile={setViewing} />
          ))}
        </div>
        </>
      )}

      {viewing && (
        <ProfileModal
          userId={viewing}
          onClose={() => setViewing(null)}
          onConnected={(type, id) => {
            setViewing(null)
            handleAction(type || 'connected', id || viewing)
          }}
        />
      )}
    </div>
  )
}
