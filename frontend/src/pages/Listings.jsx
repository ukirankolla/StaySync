import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import ProfileModal from '../components/ProfileModal'
import Avatar from '../components/Avatar'
import { listingImage, roomImage } from '../lib/images'

export default function Listings() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [listings, setListings] = useState([])
  const [mine, setMine] = useState([])
  const [filters, setFilters] = useState({ city: '', maxRent: '' })
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', city: '', area: '', rent: '', deposit: '',
    room_type: 'private', bhk: '', amenities: '', available_from: '', looking_for: '',
    photos: [],
  })
  const [uploading, setUploading] = useState(false)
  const [contacting, setContacting] = useState(null)
  const [err, setErr] = useState('')
  const [notice, setNotice] = useState('')
  const [editId, setEditId] = useState(null)
  const [viewOwner, setViewOwner] = useState(null)
  const [invites, setInvites] = useState([])
  const [residentInput, setResidentInput] = useState({})
  const [contactingResident, setContactingResident] = useState(null)
  const [importing, setImporting] = useState(false)

  const load = () => {
    api(`/listings${filters.city ? `?city=${encodeURIComponent(filters.city)}` : ''}${filters.maxRent ? `${filters.city ? '&' : '?'}max_rent=${filters.maxRent}` : ''}`)
      .then(setListings)
      .catch((e) => setErr(e.message))
  }
  useEffect(load, [filters])

  const loadMine = () => api('/listings/mine').then(setMine).catch(() => {})
  useEffect(() => { loadMine() }, [])

  const loadInvites = () => api('/listings/residents/invitations').then(setInvites).catch(() => {})
  useEffect(() => { loadInvites() }, [])

  const flash = (msg) => { setNotice(msg); setTimeout(() => setNotice(''), 5000) }
  const refreshAll = () => { load(); loadMine(); loadInvites() }

  const respondInvite = async (inv, action) => {
    setErr('')
    try {
      await api(`/listings/residents/${inv.id}/respond?action=${action}`, { method: 'POST' })
      flash(action === 'accept' ? 'You are now listed as a resident. Seekers can chat with you.' : 'Invitation declined.')
      refreshAll()
    } catch (e) { setErr(e.message) }
  }

  const addResident = async (l) => {
    const identifier = (residentInput[l.id] || '').trim()
    if (!identifier) return
    setErr('')
    try {
      await api(`/listings/${l.id}/residents`, { method: 'POST', body: { identifier } })
      setResidentInput((r) => ({ ...r, [l.id]: '' }))
      flash('Invitation sent. They will show on the listing once they confirm.')
      loadMine()
    } catch (e) { setErr(e.message) }
  }

  const removeResident = async (l, userId, isSelf) => {
    if (!confirm(isSelf ? 'Remove yourself from this listing?' : 'Remove this resident from the listing?')) return
    setErr('')
    try {
      await api(`/listings/${l.id}/residents/${userId}`, { method: 'DELETE' })
      refreshAll()
    } catch (e) { setErr(e.message) }
  }

  const TEMPLATE = 'title,city,area,address,rent,deposit,room_type,bhk,amenities,photos,description,available_from,looking_for\n' +
    '"Sunny room near metro",Ongole,Church Center,"12-3 Main Road",4500,9000,private,2BHK,WiFi;Geyser;Parking,,"Furnished room, veg preferred",2026-12-01,1\n'
  const downloadTemplate = () => {
    const url = URL.createObjectURL(new Blob([TEMPLATE], { type: 'text/csv' }))
    const a = document.createElement('a'); a.href = url; a.download = 'staysync-listings-template.csv'; a.click()
    URL.revokeObjectURL(url)
  }
  const importCsv = async (e) => {
    const file = e.target.files?.[0]; e.target.value = ''
    if (!file) return
    setImporting(true); setErr(''); setNotice('')
    try {
      const res = await api('/listings/import', { method: 'POST', body: { csv: await file.text() } })
      const bad = res.errors?.length ? ` ${res.errors.length} row(s) skipped: ` + res.errors.slice(0, 3).map((x) => `line ${x.row} (${x.error})`).join('; ') : ''
      flash(`Imported ${res.created} listing(s)${res.status === 'pending' ? ' - they will appear once approved' : ''}.${bad}`)
      load(); loadMine()
    } catch (e2) { setErr(e2.message) } finally { setImporting(false) }
  }

  const contactResident = async (l, r) => {
    setContactingResident(r.user_id); setErr('')
    try {
      const res = await api(`/listings/${l.id}/residents/${r.user_id}/contact`, { method: 'POST' })
      if (res.status === 'accepted') { navigate(`/chat/${res.connection_id}`) }
      else flash(`Request sent to ${r.full_name}. Once they accept, you can chat.`)
    } catch (e) { setErr(e.message) } finally { setContactingResident(null) }
  }

  const emptyForm = { title: '', description: '', city: '', area: '', rent: '', deposit: '', room_type: 'private', bhk: '', amenities: '', available_from: '', looking_for: '', photos: [] }

  const startEdit = (l) => {
    setForm({
      title: l.title, description: l.description || '', city: l.city, area: l.area || '',
      rent: l.rent, deposit: l.deposit || '', room_type: l.room_type, bhk: l.bhk || '',
      amenities: (l.amenities || []).join(', '), available_from: l.available_from || '',
      looking_for: l.looking_for || '', photos: l.photos || [],
    })
    setEditId(l.id); setShowForm(true)
  }

  const cancelEdit = () => { setEditId(null); setForm(emptyForm); setShowForm(false) }

  const create = async (e) => {
    e.preventDefault(); setErr('')
    try {
      const payload = {
        title: form.title, description: form.description, city: form.city, area: form.area,
        rent: Number(form.rent), deposit: form.deposit === '' ? null : Number(form.deposit),
        room_type: form.room_type, bhk: form.bhk || null,
        amenities: form.amenities.split(',').map((a) => a.trim()).filter(Boolean),
        available_from: form.available_from || null, looking_for: form.looking_for === '' ? null : Number(form.looking_for),
        photos: form.photos,
      }
      if (editId) {
        await api(`/listings/${editId}`, { method: 'PUT', body: payload }); setNotice('Listing updated.')
      } else {
        await api('/listings', { method: 'POST', body: payload }); setNotice('Listing submitted for review.')
      }
      cancelEdit(); setTimeout(() => setNotice(''), 4000); loadMine(); load()
    } catch (e2) { setErr(e2.message) }
  }

  const toggleActive = async (l) => {
    try { await api(`/listings/${l.id}`, { method: 'PUT', body: { is_active: !l.is_active } }); loadMine() }
    catch (e2) { setErr(e2.message) }
  }

  const uploadPhoto = async (e) => {
    const file = e.target.files?.[0]; if (!file) return
    setUploading(true); setErr('')
    try {
      const fd = new FormData(); fd.append('file', file)
      const res = await fetch('/api/upload/image', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('staysync_token')}` },
        body: fd,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Upload failed')
      setForm((f) => ({ ...f, photos: [...f.photos, data.url] }))
    } catch (e2) { setErr(e2.message) } finally { setUploading(false); e.target.value = '' }
  }

  const removePhoto = (url) => setForm((f) => ({ ...f, photos: f.photos.filter((p) => p !== url) }))

  const contact = async (l) => {
    setContacting(l.id); setErr('')
    try {
      const res = await api(`/listings/${l.id}/contact`, { method: 'POST' })
      if (res.status === 'accepted') { navigate(`/chat/${res.connection_id}`) }
      else { setNotice('Request sent to the owner. Once they accept, you can chat.'); setTimeout(() => setNotice(''), 5000) }
    } catch (e) { setErr(e.message) } finally { setContacting(null) }
  }

  const report = async (l) => {
    const reason = prompt('Reason for reporting this listing?', 'Fake listing')
    if (!reason) return
    try { await api('/moderation/report', { method: 'POST', body: { target_type: 'listing', listing_id: l.id, reason } }); alert('Report submitted.') }
    catch (e) { alert(e.message) }
  }

  const renderResidents = (l, canManage) => {
    const list = l.residents || []
    if (list.length === 0 && !canManage) return null
    return (
      <div className="mt-8">
        <div className="section-label">
          {list.length > 0 ? 'People living here' : 'No residents listed yet'}
        </div>
        {list.map((r) => (
          <div key={r.id} className="resident-row">
            <Avatar name={r.full_name} photo={r.photos?.[0]} size={40} style={{ flexShrink: 0 }} />
            <div className="resident-info">
              <div className="resident-name">
                {r.full_name}{r.is_you ? ' (you)' : ''}
                {r.is_verified && <span className="chip chip-green">verified</span>}
                {r.status === 'pending' && <span className="status-pill status-pending">awaiting confirmation</span>}
              </div>
              <div className="muted" style={{ fontSize: '.8rem' }}>
                {[r.age && `${r.age} yrs`, r.occupation_detail || r.occupation].filter(Boolean).join(' · ')}
              </div>
              {r.reasons?.length > 0 && <div className="muted" style={{ fontSize: '.78rem' }}>{r.reasons[0]}</div>}
            </div>
            {r.score != null && <span className="chip chip-green" style={{ flexShrink: 0 }}>{Math.round(r.score)}% match</span>}
            <div className="resident-actions">
              <button className="btn btn-ghost btn-sm" onClick={() => setViewOwner(r.user_id)}>Profile</button>
              {!r.is_you && r.status === 'accepted' && l.owner_id !== user.id && (
                <button className="btn btn-primary btn-sm" disabled={contactingResident === r.user_id} onClick={() => contactResident(l, r)}>
                  {contactingResident === r.user_id ? 'Sending…' : '💬 Chat'}
                </button>
              )}
              {(canManage || r.is_you) && (
                <button className="btn btn-ghost btn-sm" onClick={() => removeResident(l, r.user_id, r.is_you)}>
                  {r.is_you ? 'Leave' : 'Remove'}
                </button>
              )}
            </div>
          </div>
        ))}
        {canManage && (
          <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
            <input className="input" style={{ flex: 1, minWidth: 180 }} placeholder="Flatmate's email or phone (must have a StaySync account)"
                   value={residentInput[l.id] || ''} onChange={(e) => setResidentInput((r) => ({ ...r, [l.id]: e.target.value }))}
                   onKeyDown={(e) => { if (e.key === 'Enter') addResident(l) }} />
            <button className="btn btn-sm" onClick={() => addResident(l)}>+ Add resident</button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ marginBottom: 4 }}>Flats & rooms</h2>
          <div className="live-indicator"><span className="live-dot" /> Chat with owners &amp; residents</div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="btn btn-ghost btn-sm" onClick={downloadTemplate}>CSV template</button>
          <label className="btn btn-ghost btn-sm" style={{ cursor: 'pointer' }}>
            {importing ? 'Importing...' : 'Import CSV'}
            <input type="file" accept=".csv,text/csv" onChange={importCsv} hidden disabled={importing} />
          </label>
          <button className="btn btn-primary btn-sm" onClick={() => setShowForm((s) => !s)}>
            {showForm ? 'Close' : '+ Post a listing'}
          </button>
        </div>
      </div>

      {notice && <div className="alert alert-success mt-16">{notice}</div>}
      {err && <div className="alert mt-16">{err}</div>}

      {invites.length > 0 && (
        <div className="card mt-16">
          <strong>🏠 Do you live here?</strong>
          {invites.map((inv) => (
            <div key={inv.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginTop: 10 }}>
              <span>
                {inv.invited_by || 'A poster'} listed you as living at <strong>{inv.listing_title}</strong>
                {' '}({[inv.area, inv.city].filter(Boolean).join(', ')}). Confirm so people looking for a room can chat with you.
              </span>
              <span style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-primary btn-sm" onClick={() => respondInvite(inv, 'accept')}>Yes, I live here</button>
                <button className="btn btn-ghost btn-sm" onClick={() => respondInvite(inv, 'decline')}>No</button>
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="card mt-16 mb-16 filter-bar">
        <div className="field">
          <label>City</label>
          <input className="input" value={filters.city} onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                 placeholder="e.g. Delhi, Bengaluru" />
        </div>
        <div className="field">
          <label>Max rent (₹/mo)</label>
          <input className="input" type="number" value={filters.maxRent} onChange={(e) => setFilters({ ...filters, maxRent: e.target.value })} placeholder="20000" />
        </div>
        <button className="btn btn-primary btn-sm" onClick={load}><span>🔍</span> Filter</button>
      </div>

      {showForm && (
        <form className="card mb-16" onSubmit={create}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>{editId ? 'Edit listing' : 'Post a room / flat listing'}</h3>
            <button type="button" className="btn btn-ghost btn-sm" onClick={cancelEdit}>× Cancel</button>
          </div>
          <div className="form-row mt-8">
            <div className="field"><label>Title</label><input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></div>
            <div className="field"><label>Rent (₹/mo)</label><input className="input" type="number" value={form.rent} onChange={(e) => setForm({ ...form, rent: e.target.value })} required /></div>
          </div>
          <div className="form-row mt-8">
            <div className="field"><label>City</label><input className="input" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} required /></div>
            <div className="field"><label>Area</label><input className="input" value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })} /></div>
          </div>
          <div className="form-row mt-8">
            <div className="field">
              <label>Room type</label>
              <select className="select" value={form.room_type} onChange={(e) => setForm({ ...form, room_type: e.target.value })}>
                <option value="private">Private room</option>
                <option value="shared">Shared room</option>
                <option value="whole">Whole flat</option>
              </select>
            </div>
            <div className="field"><label>BHK</label><input className="input" value={form.bhk} onChange={(e) => setForm({ ...form, bhk: e.target.value })} placeholder="2BHK" /></div>
          </div>
          <div className="form-row mt-8">
            <div className="field"><label>Deposit (₹)</label><input className="input" type="number" value={form.deposit} onChange={(e) => setForm({ ...form, deposit: e.target.value })} /></div>
            <div className="field"><label>Flatmates wanted</label><input className="input" type="number" value={form.looking_for} onChange={(e) => setForm({ ...form, looking_for: e.target.value })} /></div>
          </div>
          <div className="field mt-8"><label>Amenities (comma separated)</label><input className="input" value={form.amenities} onChange={(e) => setForm({ ...form, amenities: e.target.value })} placeholder="WiFi, Parking, Gym" /></div>
          <div className="field mt-8"><label>Available from</label><input className="input" type="date" value={form.available_from} onChange={(e) => setForm({ ...form, available_from: e.target.value })} /></div>
          <div className="field mt-8">
            <label>Photos</label>
            {form.photos.length > 0 && (
              <div className="photo-strip mb-8">
                {form.photos.map((p) => (
                  <div key={p} style={{ position: 'relative' }}>
                    <img src={p} alt="" className="photo-thumb photo-thumb-lg" />
                    <button type="button" onClick={() => removePhoto(p)}
                            style={{ position: 'absolute', top: -6, right: -6, borderRadius: '50%', background: 'var(--danger)', color: '#fff', border: 'none', width: 22, height: 22, cursor: 'pointer', fontSize: '.7rem' }}>×</button>
                  </div>
                ))}
              </div>
            )}
            <div className="photo-upload">
              <input type="file" accept="image/jpeg,image/png,image/webp" onChange={uploadPhoto}
                     disabled={uploading} className="input" style={{ width: 'auto' }} />
              {uploading && <span className="muted">Uploading…</span>}
            </div>
          </div>
          <div className="field mt-8"><label>Description</label><textarea className="input" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <button className="btn btn-primary btn-block mt-16">{editId ? 'Save changes' : 'Submit for review'}</button>
        </form>
      )}

      {listings.length === 0 ? (
        <div className="empty">
          <div style={{ fontSize: '3rem', marginBottom: 12 }}>🏢</div>
          <div style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: 8 }}>No listings match your filters</div>
          <p>Try adjusting your search criteria.</p>
        </div>
      ) : (
        <div className="grid grid-2">
          {listings.map((l) => (
            <div className="card listing-card" key={l.id}>
              <img className="match-photo" src={listingImage(l)} alt={l.title} loading="lazy" />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '1.05rem' }}>{l.title}</h3>
                <span className="chip">₹{l.rent.toLocaleString('en-IN')}/mo</span>
              </div>
              <div className="match-meta mt-8">
                <span className="chip">{l.city}</span>
                {l.area && <span className="chip chip-gray">{l.area}</span>}
                <span className="chip chip-gray">{l.room_type.replace('_', ' ')}</span>
                {l.bhk && <span className="chip chip-gray">{l.bhk}</span>}
                {l.is_verified && <span className="chip chip-green">verified</span>}
              </div>
              {l.description && <p className="muted mt-8" style={{ fontSize: '.88rem', lineHeight: 1.5 }}>{l.description}</p>}
              {l.photos?.length > 0 && (
                <div className="photo-strip mt-8">
                  {l.photos.slice(0, 4).map((p) => <img key={p} src={p} alt="" className="photo-thumb" />)}
                </div>
              )}
              <div className="mt-8" style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
                {l.amenities.map((a) => <span key={a} className="chip chip-gray">{String(a).replace(/_/g, ' ')}</span>)}
              </div>
              {l.available_from && <p className="muted mt-8" style={{ fontSize: '.82rem' }}>Available from {l.available_from}</p>}
              {l.owner_name && <p className="muted mt-8" style={{ fontSize: '.82rem' }}>Posted by {l.owner_name}</p>}
              {renderResidents(l, false)}
              <div className="mt-8 listing-actions">
                {l.owner_id !== user.id && (
                  <>
                    <button className="btn btn-primary btn-sm" disabled={contacting === l.id} onClick={() => contact(l)}>
                      {contacting === l.id ? 'Sending…' : '🔗 Contact owner'}
                    </button>
                    <button className="btn btn-ghost btn-sm" onClick={() => setViewOwner(l.owner_id)}>View owner</button>
                    <button className="btn btn-ghost btn-sm" onClick={() => report(l)}>Report</button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {mine.length > 0 && (
        <>
          <h3 className="mt-24" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>📋</span> Your listings
          </h3>
          <div className="grid grid-2">
            {mine.map((l) => (
              <div className="card" key={l.id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                  <strong>{l.title}</strong>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <span className={`status-pill status-${l.status === 'approved' ? 'accepted' : 'pending'}`}>{l.status}</span>
                    {l.status === 'approved' && <span className={`status-pill ${l.is_active ? 'status-accepted' : 'status-declined'}`}>{l.is_active ? 'active' : 'hidden'}</span>}
                  </div>
                </div>
                <p className="muted mt-8 mb-8">₹{l.rent.toLocaleString('en-IN')}/mo · {l.city}</p>
                {renderResidents(l, true)}
                <div className="mb-8" />
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  <button className="btn btn-sm" onClick={() => startEdit(l)}>Edit</button>
                  {l.status === 'approved' && (
                    <button className="btn btn-ghost btn-sm" onClick={() => toggleActive(l)}>
                      {l.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {viewOwner && <ProfileModal userId={viewOwner} onClose={() => setViewOwner(null)} />}
    </div>
  )
}
