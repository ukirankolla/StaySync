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
  const [filters, setFilters] = useState({ area: '', maxBudget: '', sort: 'ml', verifiedOnly: false })
  const [applied, setApplied] = useState(null)

  useEffect(() => {
    const params = new URLSearchParams()
    if (applied?.area) params.set('area', applied.area)
    if (applied?.maxBudget) params.set('max_budget', applied.maxBudget)
    if (applied?.verifiedOnly) params.set('verified_only', 1)
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
    if (filters.sort === 'score') return b.score - a.score
    if (filters.sort === 'budget') return (a.budget_min || 0) - (b.budget_min || 0)
    return (b.ml_score ?? b.score) - (a.ml_score ?? a.score)
  })

  if (loading) return <div className="page-muted">Finding compatible roommates…</div>
  if (err) return <div className="page-muted">{err}</div>

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <h2>Recommended roommates</h2>
        <Link to="/questionnaire" className="btn btn-ghost btn-sm">Update questionnaire</Link>
      </div>
      <p className="muted mb-16">Ranked by compatibility score and our ML model. Transparency first — every score comes with reasons.</p>

      <div className="card mb-16" style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'end' }}>
        <div className="field">
          <label>Location (any city / area)</label>
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
            <option value="ml">Best match (ML)</option>
            <option value="score">Compatibility score</option>
            <option value="budget">Lowest budget</option>
          </select>
        </div>
        <div className="field">
          <label>&nbsp;</label>
          <label className="form-note" style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '8px 0' }}>
            <input type="checkbox" checked={filters.verifiedOnly}
                   onChange={(e) => setFilters({ ...filters, verifiedOnly: e.target.checked })} />
            Verified only
          </label>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setApplied({ area: filters.area, maxBudget: filters.maxBudget, verifiedOnly: filters.verifiedOnly })}>Apply</button>
        <button className="btn btn-ghost btn-sm" onClick={() => { setFilters({ area: '', maxBudget: '', sort: 'ml', verifiedOnly: false }); setApplied(null) }}>Reset</button>
      </div>

      {notice && <div className="alert alert-success mb-16">{notice}</div>}

      {sorted.length === 0 ? (
        <div className="empty">
          No matches yet.
          {matches.length === 0 && (
            <p>Complete your profile and lifestyle questionnaire to unlock recommendations.</p>
          )}
        </div>
      ) : (
        <div className="grid grid-2">
          {sorted.map((m) => (
            <MatchCard key={m.user_id} match={m} onAction={handleAction} onViewProfile={setViewing} />
          ))}
        </div>
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
