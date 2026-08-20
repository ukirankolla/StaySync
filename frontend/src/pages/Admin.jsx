import React, { useEffect, useState } from 'react'
import { api } from '../api/client'

function Stat({ label, value, icon }) {
  return (
    <div className="card stat">
      <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
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

  return (
    <div>
      <h2 style={{ marginBottom: 4 }}>Admin Dashboard</h2>
      <div className="live-indicator mb-16"><span className="live-dot" /> Live analytics</div>
      {err && <div className="alert">{err}</div>}
      {notice && <div className="alert alert-success mt-8">{notice}</div>}

      <div className="tabs mt-16">
        {['overview', 'users', 'reports', 'listings'].map((t) => (
          <button key={t} className={`btn btn-sm ${tab === t ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab(t)}>
            {t[0].toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {tab === 'overview' && stats && (
        <div>
          <div className="admin-grid">
            <Stat label="Registered users" value={stats.total_users} icon="👥" />
            <Stat label="Questionnaire done" value={stats.questionnaire_completed} icon="📋" />
            <Stat label="Profiles completed" value={stats.profiles_completed} icon="👤" />
            <Stat label="Connections" value={stats.total_connections} icon="🔗" />
            <Stat label="Accepted" value={stats.accepted_connections} icon="✓" />
            <Stat label="Messages" value={stats.total_messages} icon="💬" />
            <Stat label="Groups" value={stats.total_groups} icon="👥" />
            <Stat label="Listings" value={stats.total_listings} icon="🏢" />
            <Stat label="Approved listings" value={stats.approved_listings} icon="✅" />
            <Stat label="Pending reports" value={stats.pending_reports} icon="⚠️" />
            <Stat label="Suspended users" value={stats.suspended_users} icon="🚫" />
          </div>

          <div className="grid grid-2 mt-24">
            <div className="card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><span>📍</span> Users by city</h3>
              {stats.users_by_city.length === 0 ? <p className="muted">No data</p> : (
                <table className="table"><tbody>
                  {stats.users_by_city.map((c) => (
                    <tr key={c.city}><td>{c.city}</td><td><strong>{c.count}</strong></td></tr>
                  ))}
                </tbody></table>
              )}
            </div>
            <div className="card">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><span>📈</span> Registrations per day</h3>
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
                  <td><span className="chip chip-gray">{u.role}</span></td>
                  <td>{u.is_suspended ? <span className="status-pill status-declined">suspended</span> : <span className="status-pill status-accepted">active</span>}</td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td>
                    {u.role !== 'admin' && (
                      <button className="btn btn-ghost btn-sm" onClick={() => suspend(u.id, !u.is_suspended)}>
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
                    <td><span className={`chip ${r.severity === 'high' ? '' : 'chip-gray'}`} style={r.severity === 'high' ? { background: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', border: '1px solid rgba(239, 68, 68, 0.2)' } : r.severity === 'medium' ? { background: 'rgba(245, 158, 11, 0.15)', color: '#fcd34d', border: '1px solid rgba(245, 158, 11, 0.2)' } : {}}>{r.severity}</span></td>
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
                  <td><span className="chip chip-gray">{l.status}</span></td>
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
