import React, { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Groups() {
  const [groups, setGroups] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', city: '', target_area: '', budget_min: '', budget_max: '' })
  const [invite, setInvite] = useState('')
  const [err, setErr] = useState('')
  const [notice, setNotice] = useState('')

  const load = () => api('/groups').then(setGroups).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])

  const create = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      const payload = {
        name: form.name, city: form.city, target_area: form.target_area || null,
        budget_min: form.budget_min === '' ? null : Number(form.budget_min),
        budget_max: form.budget_max === '' ? null : Number(form.budget_max),
      }
      await api('/groups', { method: 'POST', body: payload })
      setForm({ name: '', city: '', target_area: '', budget_min: '', budget_max: '' })
      setShowForm(false)
      load()
    } catch (e2) { setErr(e2.message) }
  }

  const inviteTo = async (groupId) => {
    if (!invite) return
    try {
      await api(`/groups/${groupId}/invite`, { method: 'POST', body: { user_id: Number(invite) } })
      setInvite('')
      setNotice('Invited!')
      setTimeout(() => setNotice(''), 3000)
      load()
    } catch (e) { setErr(e.message) }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <h2>Roommate groups</h2>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Close' : '+ New group'}
        </button>
      </div>
      <p className="muted mb-16">Form a group with compatible people, then find a flat together.</p>

      {notice && <div className="alert alert-success mb-16">{notice}</div>}
      {err && <div className="alert mb-16">{err}</div>}

      {showForm && (
        <form className="card mb-16" onSubmit={create}>
          <div className="form-row mb-8">
            <div className="field">
              <label>Group name</label>
              <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div className="field">
              <label>City</label>
              <input className="input" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })}
                     placeholder="Any city — e.g. Bengaluru, London, New York" required />
            </div>
          </div>
          <div className="form-row mb-8">
            <div className="field">
              <label>Target area</label>
              <input className="input" value={form.target_area} onChange={(e) => setForm({ ...form, target_area: e.target.value })} />
            </div>
            <div className="form-row" style={{ gap: 8 }}>
              <div className="field">
                <label>Budget min</label>
                <input className="input" type="number" value={form.budget_min} onChange={(e) => setForm({ ...form, budget_min: e.target.value })} />
              </div>
              <div className="field">
                <label>Budget max</label>
                <input className="input" type="number" value={form.budget_max} onChange={(e) => setForm({ ...form, budget_max: e.target.value })} />
              </div>
            </div>
          </div>
          <button className="btn btn-primary btn-block">Create group</button>
        </form>
      )}

      {groups.length === 0 ? (
        <div className="empty">No groups yet. Create one to start flat-hunting together.</div>
      ) : (
        <div className="grid grid-2">
          {groups.map((g) => (
            <div className="card" key={g.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0 }}>{g.name}</h3>
                <span className={`status-pill status-${g.status}`} style={{ fontSize: '.75rem' }}>{g.status}</span>
              </div>
              <div className="match-meta mt-8">
                <span className="chip">{g.city}</span>
                {g.target_area && <span className="chip chip-gray">{g.target_area}</span>}
                {g.budget_min != null && <span className="chip chip-gray">₹{g.budget_min.toLocaleString('en-IN')}–{g.budget_max?.toLocaleString('en-IN')}</span>}
                <span className="chip chip-gray">{g.members.length} member{g.members.length !== 1 ? 's' : ''}</span>
              </div>
              <div className="mt-8" style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {g.members.map((m) => (
                  <div key={m.user_id} className="muted" style={{ fontSize: '.85rem' }}>
                    {m.full_name} {m.is_owner && <span className="badge">owner</span>}
                  </div>
                ))}
              </div>
              {g.owner_id === g.members.find((m) => m.is_owner)?.user_id && (
                <div className="mt-8" style={{ display: 'flex', gap: 8 }}>
                  <input className="input" placeholder="Invite by user ID" value={invite}
                         onChange={(e) => setInvite(e.target.value)} style={{ flex: 1 }} />
                  <button className="btn btn-ghost btn-sm" onClick={() => inviteTo(g.id)}>Invite</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
