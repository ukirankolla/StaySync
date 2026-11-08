import React, { useEffect, useState } from 'react'
import { api } from '../api/client'

function Staff({ id, onBack }) {
  const [d, setD] = useState(null)
  const [ins, setIns] = useState(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const load = () => api(`/hostels/${id}`).then(setD).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [id])

  const act = async (path, opts) => {
    setBusy(true); setErr('')
    try { await api(`/hostels/${id}${path}`, opts); await load() } catch (e) { setErr(e.message) } finally { setBusy(false) }
  }
  const move = (uid) => {
    const room = prompt('Move to which room? (e.g. R3). Leave empty to unassign.', '')
    if (room === null) return
    act(`/members/${uid}`, { method: 'PATCH', body: { room_no: room } })
  }
  const showInsights = async () => {
    try { setIns(await api(`/hostels/${id}/insights`)) } catch (e) { setErr(e.message) }
  }

  if (!d) return <div className="page-muted">{err || 'Loading…'}</div>
  const h = d.hostel
  return (
    <div>
      <button className="btn btn-ghost btn-sm" onClick={onBack}>← All hostels</button>
      <h2 style={{ marginTop: 12 }}>{h.name}</h2>
      <p className="muted">
        Student join code: <strong style={{ letterSpacing: 2 }}>{h.join_code}</strong> · {h.room_size} per room ·{' '}
        {h.allocation_final ? 'Allocation final' : 'Draft allocation'}
      </p>
      {err && <div className="alert">{err}</div>}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', margin: '12px 0' }}>
        {!h.allocation_final && <button className="btn btn-primary btn-sm" disabled={busy} onClick={() => act('/suggest', { method: 'POST' })}>Suggest rooms</button>}
        {!h.allocation_final && <button className="btn btn-success btn-sm" disabled={busy} onClick={() => confirm('Finalise this allocation? Students will see their roommates.') && act('/finalize', { method: 'POST' })}>Finalise allocation</button>}
        {h.allocation_final && <button className="btn btn-ghost btn-sm" disabled={busy} onClick={() => act('/reopen', { method: 'POST' })}>Reopen</button>}
        <button className="btn btn-ghost btn-sm" onClick={showInsights}>Campus insights</button>
      </div>
      <p className="muted" style={{ fontSize: '.8rem' }}>
        Suggestions are based on lifestyle answers only and are not guarantees. You review, edit and make the final decision.
      </p>

      {ins && (
        <div className="card" style={{ margin: '12px 0' }}>
          <strong>{ins.students} students · {ins.room_change_requests} change requests</strong>
          <div className="muted" style={{ fontSize: '.85rem', marginTop: 6 }}>
            {Object.entries(ins.preferences).map(([k, v]) => (
              <div key={k}>{k.replace('_', ' ')}: {Object.entries(v).map(([a, n]) => `${a} (${n})`).join(' · ')}</div>
            ))}
          </div>
        </div>
      )}

      {d.unassigned.length > 0 && (
        <>
          <h3 className="mt-16">Not yet assigned ({d.unassigned.length})</h3>
          {d.unassigned.map((u) => (
            <div className="conn-item" key={u.user_id} style={{ display: 'flex', justifyContent: 'space-between', gap: 8 }}>
              <div><strong>{u.name}</strong> <span className="chip chip-gray">{u.block}</span>
                {u.special_request && <div className="muted" style={{ fontSize: '.82rem' }}>Request: {u.special_request}</div>}</div>
              {!h.allocation_final && <button className="btn btn-ghost btn-sm" onClick={() => move(u.user_id)}>Assign</button>}
            </div>
          ))}
        </>
      )}

      <h3 className="mt-16">Rooms ({d.rooms.length})</h3>
      <div className="grid grid-2">
        {d.rooms.map((r) => (
          <div className="card" key={r.room_no}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong>{r.room_no} <span className="chip chip-gray">{r.block}</span></strong>
              <span className="badge">{r.score != null ? `${Math.round(r.score)}%` : '—'}</span>
            </div>
            {r.needs_attention && <div className="alert" style={{ marginTop: 8 }}>Low compatibility — please review.</div>}
            {r.over_capacity && <div className="alert" style={{ marginTop: 8 }}>Over capacity.</div>}
            {r.members.map((m) => (
              <div key={m.user_id} style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
                <span>{m.name}{m.special_request && <span className="muted" style={{ fontSize: '.8rem' }}> · {m.special_request}</span>}</span>
                {!h.allocation_final && <button className="btn btn-ghost btn-sm" onClick={() => move(m.user_id)}>Move</button>}
              </div>
            ))}
            <div className="reasons" style={{ marginTop: 8 }}>{r.reasons.map((x, i) => <div className="reason" key={i}>{x}</div>)}</div>
          </div>
        ))}
      </div>

      <h3 className="mt-24">Change requests</h3>
      {d.change_requests.length === 0 ? <p className="muted">None.</p> : d.change_requests.map((c) => (
        <div className="card" key={c.id} style={{ marginBottom: 8 }}>
          <strong>{c.student}</strong> <span className={`status-pill status-${c.status === 'approved' ? 'accepted' : c.status}`}>{c.status}</span>
          <p style={{ margin: '6px 0' }}>{c.reason}</p>
          {c.status === 'pending' && (
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-success btn-sm" onClick={() => act(`/change-requests/${c.id}`, { method: 'PATCH', body: { decision: 'approve' } })}>Approve (reassign)</button>
              <button className="btn btn-ghost btn-sm" onClick={() => act(`/change-requests/${c.id}`, { method: 'PATCH', body: { decision: 'decline', staff_note: prompt('Note for the student (optional)') || null } })}>Decline</button>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

function Student({ id, onBack }) {
  const [d, setD] = useState(null)
  const [reason, setReason] = useState('')
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const load = () => api(`/hostels/${id}`).then(setD).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [id])

  const send = async (e) => {
    e.preventDefault(); setErr('')
    try {
      await api(`/hostels/${id}/change-requests`, { method: 'POST', body: { reason } })
      setReason(''); setMsg('Request sent to the hostel staff.'); load()
    } catch (e2) { setErr(e2.message) }
  }
  const leave = async () => {
    if (!confirm('Withdraw from this hostel and delete the answers you shared with it?')) return
    try { await api(`/hostels/${id}/membership`, { method: 'DELETE' }); onBack() } catch (e) { setErr(e.message) }
  }

  if (!d) return <div className="page-muted">{err || 'Loading…'}</div>
  return (
    <div>
      <button className="btn btn-ghost btn-sm" onClick={onBack}>← All hostels</button>
      <h2 style={{ marginTop: 12 }}>{d.hostel.name}</h2>
      {err && <div className="alert">{err}</div>}
      {d.hostel.allocation_final && d.my.room_no ? (
        <div className="card">
          <strong>Your room: {d.my.room_no}</strong>
          <p>Roommates: {d.roommates.length ? d.roommates.join(', ') : 'none yet'}</p>
          {d.room_score != null && <p className="muted">Lifestyle compatibility {Math.round(d.room_score)}%</p>}
          {d.reasons.map((r, i) => <div className="reason" key={i}>{r}</div>)}
          <p className="muted" style={{ fontSize: '.8rem' }}>This is a recommendation, not a guarantee. Talk to your roommates about expectations early.</p>
        </div>
      ) : (
        <div className="card">Your preferences are with the hostel staff. You'll see your room and roommates here once they finalise the allocation.</div>
      )}

      <h3 className="mt-24">Need a change?</h3>
      <form onSubmit={send} style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <input className="input" style={{ flex: 1, minWidth: 220 }} required minLength={5} maxLength={1000} value={reason}
               onChange={(e) => setReason(e.target.value)} placeholder="Tell the staff what's not working" />
        <button className="btn btn-primary btn-sm">Request change</button>
      </form>
      {msg && <p className="muted">{msg}</p>}
      {d.change_requests.map((c) => (
        <div key={c.id} className="muted" style={{ marginTop: 6 }}>
          “{c.reason}” — <strong>{c.status}</strong>{c.staff_note ? ` · ${c.staff_note}` : ''}
        </div>
      ))}
      <p className="mt-24"><button className="btn btn-ghost btn-sm" onClick={leave}>Withdraw and delete my data</button></p>
    </div>
  )
}

export default function Hostels() {
  const [data, setData] = useState({ managed: [], joined: [] })
  const [open, setOpen] = useState(null) // {id, kind}
  const [create, setCreate] = useState({ name: '', institution: '', room_size: 2 })
  const [join, setJoin] = useState({ code: '', block: 'General', special_request: '', consent: false })
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')
  const load = () => api('/hostels').then(setData).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])

  if (open) {
    const back = () => { setOpen(null); load() }
    return open.kind === 'staff' ? <Staff id={open.id} onBack={back} /> : <Student id={open.id} onBack={back} />
  }

  const doCreate = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const h = await api('/hostels', { method: 'POST', body: { ...create, room_size: Number(create.room_size) } })
      setCreate({ name: '', institution: '', room_size: 2 }); setMsg(`Created. Share code ${h.join_code} with your students.`); load()
    } catch (e2) { setErr(e2.message) }
  }
  const doJoin = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const r = await api('/hostels/join', { method: 'POST', body: join })
      setJoin({ code: '', block: 'General', special_request: '', consent: false }); setMsg(`Joined ${r.name}.`); load()
    } catch (e2) { setErr(e2.message) }
  }

  return (
    <div>
      <h2>College &amp; hostel allocation</h2>
      <p className="muted">Students share lifestyle preferences, staff review suggested pairings and make the final allocation.</p>
      {err && <div className="alert">{err}</div>}
      {msg && <div className="alert" style={{ background: 'rgba(16,185,129,.1)' }}>{msg}</div>}

      <div className="grid grid-2">
        <form className="card" onSubmit={doJoin}>
          <h3>I'm a student</h3>
          <p className="muted" style={{ fontSize: '.85rem' }}>Enter the code from your hostel. Complete the lifestyle questionnaire first.</p>
          <input className="input" required placeholder="Join code" value={join.code} onChange={(e) => setJoin({ ...join, code: e.target.value.toUpperCase() })} />
          <input className="input mt-8" required placeholder="Hostel block (e.g. Boys Block A)" value={join.block} onChange={(e) => setJoin({ ...join, block: e.target.value })} />
          <input className="input mt-8" placeholder="Special request, e.g. accessibility (optional)" maxLength={500} value={join.special_request} onChange={(e) => setJoin({ ...join, special_request: e.target.value })} />
          <label style={{ display: 'flex', gap: 8, marginTop: 10, fontSize: '.85rem' }}>
            <input type="checkbox" checked={join.consent} onChange={(e) => setJoin({ ...join, consent: e.target.checked })} />
            I agree to share my lifestyle answers with this hostel's staff to help allocate rooms. I can withdraw any time.
          </label>
          <button className="btn btn-primary btn-sm mt-8">Join hostel</button>
        </form>

        <form className="card" onSubmit={doCreate}>
          <h3>I run a hostel / PG</h3>
          <input className="input" required minLength={2} placeholder="Hostel name" value={create.name} onChange={(e) => setCreate({ ...create, name: e.target.value })} />
          <input className="input mt-8" placeholder="College / institution (optional)" value={create.institution} onChange={(e) => setCreate({ ...create, institution: e.target.value })} />
          <label className="muted" style={{ display: 'block', marginTop: 8, fontSize: '.85rem' }}>Students per room</label>
          <select className="select" value={create.room_size} onChange={(e) => setCreate({ ...create, room_size: e.target.value })}>
            {[2, 3, 4, 5, 6].map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
          <button className="btn btn-primary btn-sm mt-8">Create hostel</button>
        </form>
      </div>

      {data.managed.length > 0 && <h3 className="mt-24">Hostels you manage</h3>}
      {data.managed.map((h) => (
        <div className="conn-item" key={h.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div><strong>{h.name}</strong><div className="muted" style={{ fontSize: '.82rem' }}>Code {h.join_code} · {h.students} students · {h.allocation_final ? 'final' : 'draft'}</div></div>
          <button className="btn btn-primary btn-sm" onClick={() => setOpen({ id: h.id, kind: 'staff' })}>Manage</button>
        </div>
      ))}
      {data.joined.length > 0 && <h3 className="mt-24">Your hostels</h3>}
      {data.joined.map((h) => (
        <div className="conn-item" key={h.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div><strong>{h.name}</strong><div className="muted" style={{ fontSize: '.82rem' }}>{h.block} · {h.allocation_final ? 'allocation final' : 'awaiting allocation'}</div></div>
          <button className="btn btn-ghost btn-sm" onClick={() => setOpen({ id: h.id, kind: 'student' })}>Open</button>
        </div>
      ))}
    </div>
  )
}
