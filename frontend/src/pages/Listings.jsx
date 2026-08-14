import React, { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const CITIES = ['Bengaluru', 'Mumbai', 'Delhi', 'Pune', 'Hyderabad', 'Chennai', 'Kolkata']

export default function Listings() {
  const { user } = useAuth()
  const [listings, setListings] = useState([])
  const [mine, setMine] = useState([])
  const [filters, setFilters] = useState({ city: '', maxRent: '' })
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', city: 'Bengaluru', area: '', rent: '', deposit: '',
    room_type: 'private', bhk: '', amenities: '', available_from: '', looking_for: '',
  })
  const [err, setErr] = useState('')
  const [notice, setNotice] = useState('')

  const load = () => {
    api(`/listings${filters.city ? `?city=${encodeURIComponent(filters.city)}` : ''}${filters.maxRent ? `${filters.city ? '&' : '?'}max_rent=${filters.maxRent}` : ''}`)
      .then(setListings)
      .catch((e) => setErr(e.message))
  }
  useEffect(load, [filters])

  useEffect(() => {
    api('/listings/mine').then(setMine).catch(() => {})
  }, [])

  const create = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      const payload = {
        title: form.title, description: form.description, city: form.city, area: form.area,
        rent: Number(form.rent), deposit: form.deposit === '' ? null : Number(form.deposit),
        room_type: form.room_type, bhk: form.bhk || null,
        amenities: form.amenities.split(',').map((a) => a.trim()).filter(Boolean),
        available_from: form.available_from || null, looking_for: form.looking_for === '' ? null : Number(form.looking_for),
      }
      await api('/listings', { method: 'POST', body: payload })
      setShowForm(false)
      setNotice('Listing submitted for review.')
      setTimeout(() => setNotice(''), 4000)
      api('/listings/mine').then(setMine).catch(() => {})
    } catch (e2) { setErr(e2.message) }
  }

  const report = async (l) => {
    const reason = prompt('Reason for reporting this listing?', 'Fake listing')
    if (!reason) return
    try {
      await api('/moderation/report', { method: 'POST', body: { target_type: 'listing', listing_id: l.id, reason } })
      alert('Report submitted.')
    } catch (e) { alert(e.message) }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <h2>Flats & rooms</h2>
        <button className="btn btn-primary btn-sm" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Close' : '+ Post a listing'}
        </button>
      </div>

      {notice && <div className="alert alert-success mt-16">{notice}</div>}
      {err && <div className="alert mt-16">{err}</div>}

      <div className="card mt-16 mb-16" style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'end' }}>
        <div className="field">
          <label>City</label>
          <select className="select" value={filters.city} onChange={(e) => setFilters({ ...filters, city: e.target.value })}>
            <option value="">All cities</option>
            {CITIES.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Max rent (₹/mo)</label>
          <input className="input" type="number" value={filters.maxRent} onChange={(e) => setFilters({ ...filters, maxRent: e.target.value })} placeholder="20000" />
        </div>
        <button className="btn btn-ghost" onClick={load}>Filter</button>
      </div>

      {showForm && (
        <form className="card mb-16" onSubmit={create}>
          <h3>Post a room / flat listing</h3>
          <div className="form-row mt-8">
            <div className="field">
              <label>Title</label>
              <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            </div>
            <div className="field">
              <label>Rent (₹/mo)</label>
              <input className="input" type="number" value={form.rent} onChange={(e) => setForm({ ...form, rent: e.target.value })} required />
            </div>
          </div>
          <div className="form-row mt-8">
            <div className="field">
              <label>City</label>
              <select className="select" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })}>
                {CITIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Area</label>
              <input className="input" value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })} />
            </div>
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
            <div className="field">
              <label>BHK</label>
              <input className="input" value={form.bhk} onChange={(e) => setForm({ ...form, bhk: e.target.value })} placeholder="2BHK" />
            </div>
          </div>
          <div className="form-row mt-8">
            <div className="field">
              <label>Deposit (₹)</label>
              <input className="input" type="number" value={form.deposit} onChange={(e) => setForm({ ...form, deposit: e.target.value })} />
            </div>
            <div className="field">
              <label>Flatmates wanted</label>
              <input className="input" type="number" value={form.looking_for} onChange={(e) => setForm({ ...form, looking_for: e.target.value })} />
            </div>
          </div>
          <div className="field mt-8">
            <label>Amenities (comma separated)</label>
            <input className="input" value={form.amenities} onChange={(e) => setForm({ ...form, amenities: e.target.value })} placeholder="WiFi, Parking, Gym" />
          </div>
          <div className="field mt-8">
            <label>Available from</label>
            <input className="input" type="date" value={form.available_from} onChange={(e) => setForm({ ...form, available_from: e.target.value })} />
          </div>
          <div className="field mt-8">
            <label>Description</label>
            <textarea className="input" rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <button className="btn btn-primary btn-block mt-16">Submit for review</button>
        </form>
      )}

      {listings.length === 0 ? (
        <div className="empty">No listings match your filters.</div>
      ) : (
        <div className="grid grid-2">
          {listings.map((l) => (
            <div className="card" key={l.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0 }}>{l.title}</h3>
                <span className="chip">₹{l.rent.toLocaleString('en-IN')}/mo</span>
              </div>
              <div className="match-meta mt-8">
                <span className="chip">{l.city}</span>
                {l.area && <span className="chip chip-gray">{l.area}</span>}
                <span className="chip chip-gray">{l.room_type.replace('_', ' ')}</span>
                {l.bhk && <span className="chip chip-gray">{l.bhk}</span>}
                {l.is_verified && <span className="chip chip-green">verified</span>}
              </div>
              {l.description && <p className="muted mt-8" style={{ fontSize: '.9rem' }}>{l.description}</p>}
              <div className="mt-8" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {l.amenities.map((a) => <span key={a} className="chip chip-gray">{a}</span>)}
              </div>
              {l.available_from && <p className="muted mt-8" style={{ fontSize: '.82rem' }}>Available from {l.available_from}</p>}
              <div className="mt-8">
                {l.owner_id !== user.id && (
                  <button className="btn btn-ghost btn-sm" onClick={() => report(l)}>Report</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {mine.length > 0 && (
        <>
          <h3 className="mt-24">Your listings</h3>
          <div className="grid grid-2">
            {mine.map((l) => (
              <div className="card" key={l.id}>
                <strong>{l.title}</strong>
                <span className={`status-pill status-${l.status === 'approved' ? 'accepted' : 'pending'}`} style={{ marginLeft: 8 }}>{l.status}</span>
                <p className="muted mt-8 mb-8">₹{l.rent.toLocaleString('en-IN')}/mo · {l.city}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
