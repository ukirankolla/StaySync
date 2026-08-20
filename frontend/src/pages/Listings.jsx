import React, { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'
import ProfileModal from '../components/ProfileModal'
import AiImage from '../components/AiImage'
import { listingPrompt, roomImage, hashSeed } from '../lib/images'

export default function Listings() {
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

  const load = () => {
    api(`/listings${filters.city ? `?city=${encodeURIComponent(filters.city)}` : ''}${filters.maxRent ? `${filters.city ? '&' : '?'}max_rent=${filters.maxRent}` : ''}`)
      .then(setListings)
      .catch((e) => setErr(e.message))
  }
  useEffect(load, [filters])

  const loadMine = () => api('/listings/mine').then(setMine).catch(() => {})
  useEffect(() => { loadMine() }, [])

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
      if (res.status === 'accepted') { window.location.href = `/chat/${res.connection_id}` }
      else { setNotice('Request sent to the owner. Once they accept, you can chat.'); setTimeout(() => setNotice(''), 5000) }
    } catch (e) { setErr(e.message) } finally { setContacting(null) }
  }

  const report = async (l) => {
    const reason = prompt('Reason for reporting this listing?', 'Fake listing')
    if (!reason) return
    try { await api('/moderation/report', { method: 'POST', body: { target_type: 'listing', listing_id: l.id, reason } }); alert('Report submitted.') }
    catch (e) { alert(e.message) }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ marginBottom: 4 }}>Flats & rooms</h2>
          <div className="live-indicator"><span className="live-dot" /> AI-generated previews</div>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Close' : '+ Post a listing'}
        </button>
      </div>

      {notice && <div className="alert alert-success mt-16">{notice}</div>}
      {err && <div className="alert mt-16">{err}</div>}

      <div className="card mt-16 mb-16" style={{ display: 'flex', gap: 14, flexWrap: 'wrap', alignItems: 'end' }}>
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
              {l.photos?.[0] ? (
                <img className="match-photo" src={l.photos[0]} alt={l.title} loading="lazy" />
              ) : (
                <AiImage className="match-photo" prompt={listingPrompt(l)} seed={l.id % 100000} fallback={roomImage(l.city)} alt={l.title} />
              )}
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
                {l.amenities.map((a) => <span key={a} className="chip chip-gray">{a}</span>)}
              </div>
              {l.available_from && <p className="muted mt-8" style={{ fontSize: '.82rem' }}>Available from {l.available_from}</p>}
              <div className="mt-8" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
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
