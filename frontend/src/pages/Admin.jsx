import React, { useEffect, useState } from 'react'
import { api } from '../api/client'

function Stat({ label, value }) {
  return <div className="card stat"><div className="stat-value">{value}</div><div className="stat-label">{label}</div></div>
}

export default function Admin() {
  const [tab, setTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [reports, setReports] = useState([])
  const [listings, setListings] = useState([])
  const [err, setErr] = useState('')
  const [notice, setNotice] = useState('')

  const loadStats = () => api('/admin/analytics').then(setStats).catch((e) => setErr(e.message))
  const loadUsers = () => api('/admin/users').then(setUsers).catch(() => {})
  const loadReports = () => api('/admin/reports').then(setReports).catch(() => {})
  const loadListings = () => api('/admin/listings').then(setListings).catch(() => {})

  useEffect(() => { loadStats() }, [])
  useEffect(() => { if (tab === 'users') loadUsers() }, [tab])
  useEffect(() => { if (tab === 'reports') loadReports() }, [tab])
  useEffect(() => { if (tab === 'listings') loadListings() }, [tab])

  const flash = (m) => { setNotice(m); setTimeout(() => setNotice(''), 3000) }

  const suspend = async (id, val) => {
    await api(`/admin/users/${id}/${val ? 'suspend' : 'unsuspend'}`, { method: 'POST' })
    flash(val ? 'User suspended' : 'User restored')
    loadUsers()
  }

  const reviewReport = async (id, action) => {
    await api(`/admin/reports/${id}/review?action=${action}`, { method: 'POST' })
    flash(`Report ${action}`)
    loadReports()
  }

  const reviewListing = async (id, action) => {
    await api(`/admin/listings/${id}/review?action=${action}`, { method: 'POST' })
    flash(`Listing ${action}d`)
    loadListings()
  }

  const toggle = (t) => setTab(t)

  return (
    <div>
      <h2>Admin dashboard</h2>
      {err && <div className="alert">{err}</div>}
      {notice && <div className="alert alert-success mt-8">{notice}</div>}

      <div className="tabs mt-16">
        {['overview', 'users', 'reports', 'listings'].map((t) => (
          <button key={t} className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`} onClick={() => toggle(t)}>
            {t[0].toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'overview' && stats && (
        <div>
          <div className="admin-grid">
            <Stat label="Registered users" value={stats.total_users} />
            <Stat label="Questionnaire done" value={stats.questionnaire_completed} />
            <Stat label="Profiles completed" value={stats.profiles_completed} />
            <Stat label="Connections" value={stats.total_connections} />
            <Stat label="Accepted" value={stats.accepted_connections} />
            <Stat label="Messages" value={stats.total_messages} />
            <Stat label="Groups" value={stats.total_groups} />
            <Stat label="Listings" value={stats.total_listings} />
            <Stat label="Approved listings" value={stats.approved_listings} />
            <Stat label="Pending reports" value={stats.pending_reports} />
            <Stat label="Suspended users" value={stats.suspended_users} />
          </div>

          <div className="grid grid-2 mt-24">
            <div className="card">
              <h3>Users by city</h3>
              {stats.users_by_city.length === 0 ? <p className="muted">No data</p> : (
                <table className="table"><tbody>
                  {stats.users_by_city.map((c) => (
                    <tr key={c.city}><td>{c.city}</td><td><strong>{c.count}</strong></td></tr>
                  ))}
                </tbody></table>
              )}
            </div>
            <div className="card">
              <h3>Registrations per day</h3>
              {stats.registrations_per_day.length === 0 ? <p className="muted">No data</p> : (
                <table className="table"><tbody>
                  {stats.registrations_per_day.map((r) => (
                    <tr key={r.date}><td>{r.date}</td><td><strong>{r.count}</strong></td></tr>
                  ))}
                </tbody></table>
              )}
            </div>
          </div>
        </div>
      )}

      {tab === 'users' && (
        <div className="card">
          <table className="table">
            <thead><tr><th>ID</th><th>Email / phone</th><th>Role</th><th>Status</th><th>Joined</th><th></th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.email || u.phone}</td>
                  <td>{u.role}</td>
                  <td>{u.is_suspended ? <span className="status-pill status-declined">suspended</span> : <span className="status-pill status-accepted">active</span>}</td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td>
                    {u.role !== 'admin' && (
                      <button className="btn btn-ghost btn-sm"
                              onClick={() => suspend(u.id, !u.is_suspended)}>
                        {u.is_suspended ? 'Restore' : 'Suspend'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'reports' && (
        <div className="card">
          {reports.length === 0 ? <p className="muted">No reports.</p> : (
            <table className="table">
              <thead><tr><th>ID</th><th>Type</th><th>Reason</th><th>Severity</th><th>Status</th><th>Reported</th><th></th></tr></thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.id}>
                    <td>{r.id}</td>
                    <td>{r.target_type} #{r.target_user_id || r.listing_id}</td>
                    <td>{r.reason}</td>
                    <td><span className={`chip ${r.severity === 'high' ? 'chip' : 'chip-gray'}`} style={r.severity === 'high' ? { background: '#fee2e2', color: '#991b1b' } : r.severity === 'medium' ? { background: '#fef9c3', color: '#854d0e' } : {}}>{r.severity}</span></td>
                    <td>{r.status}</td>
                    <td>{new Date(r.created_at).toLocaleDateString()}</td>
                    <td>
                      {r.status === 'pending' && (
                        <div style={{ display: 'flex', gap: 6 }}>
                          <button className="btn btn-sm btn-success" onClick={() => reviewReport(r.id, 'resolve')}>Resolve</button>
                          <button className="btn btn-sm btn-danger" onClick={() => reviewReport(r.id, 'suspend_user')}>Suspend</button>
                          <button className="btn btn-sm btn-ghost" onClick={() => reviewReport(r.id, 'dismiss')}>Dismiss</button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'listings' && (
        <div className="card">
          <table className="table">
            <thead><tr><th>ID</th><th>Title</th><th>City</th><th>Rent</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {listings.map((l) => (
                <tr key={l.id}>
                  <td>{l.id}</td>
                  <td>{l.title}</td>
                  <td>{l.city}{l.area ? ` · ${l.area}` : ''}</td>
                  <td>₹{l.rent.toLocaleString('en-IN')}</td>
                  <td>{l.status}</td>
                  <td>
                    {l.status === 'pending' && (
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-sm btn-success" onClick={() => reviewListing(l.id, 'approve')}>Approve</button>
                        <button className="btn btn-sm btn-danger" onClick={() => reviewListing(l.id, 'reject')}>Reject</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
