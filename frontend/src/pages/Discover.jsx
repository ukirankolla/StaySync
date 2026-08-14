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

  useEffect(() => {
    api('/matching/recommendations')
      .then(setMatches)
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false))
    api('/moderation/blocked')
      .then((ids) => setBlocked(new Set(ids)))
      .catch(() => {})
    api('/matching/connections')
      .then((conns) => setConnected(new Set(conns.filter((c) => ['pending', 'accepted'].includes(c.status)).map((c) => c.peer_id))))
      .catch(() => {})
  }, [])

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

  if (loading) return <div className="page-muted">Finding compatible roommates…</div>
  if (err) return <div className="page-muted">{err}</div>

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <h2>Recommended roommates</h2>
        <Link to="/questionnaire" className="btn btn-ghost btn-sm">Update questionnaire</Link>
      </div>
      <p className="muted mb-16">Ranked by compatibility score and our ML model. Transparency first — every score comes with reasons.</p>

      {notice && <div className="alert alert-success mb-16">{notice}</div>}

      {visible.length === 0 ? (
        <div className="empty">
          No matches yet.
          {matches.length === 0 && (
            <p>Complete your profile and lifestyle questionnaire to unlock recommendations.</p>
          )}
        </div>
      ) : (
        <div className="grid grid-2">
          {visible.map((m) => (
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
