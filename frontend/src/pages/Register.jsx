import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IMG } from '../lib/images'
import AiImage from '../components/AiImage'

const REGISTER_QUOTES = [
  { text: "Found a roommate who matches my routine and my budget in a single evening.", author: "Rahul, Pune" },
  { text: "The AI suggested someone who became my best friend. StaySync just works.", author: "Kavya, Hyderabad" },
  { text: "Transparent scores made me trust the platform. No other app does this.", author: "Vikram, Chennai" },
]

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [quote] = useState(() => REGISTER_QUOTES[Math.floor(Math.random() * REGISTER_QUOTES.length)])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    const body = identifier.includes('@')
      ? { email: identifier, phone: null, password, full_name: fullName }
      : { email: null, phone: identifier, password, full_name: fullName }
    try {
      await register(body)
      navigate('/profile')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-panel">
        <form className="form card" onSubmit={submit}>
          <h2 className="center">Create your account</h2>
          <p className="center muted" style={{ fontSize: '.9rem', marginTop: -4 }}>Join StaySync and find your perfect match</p>
          {error && <div className="alert">{error}</div>}
          <div className="field">
            <label>Full name</label>
            <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)}
                   placeholder="Your name" required />
          </div>
          <div className="field">
            <label>Email or phone</label>
            <input className="input" value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                   placeholder="you@example.com or +91..." required />
          </div>
          <div className="field">
            <label>Password</label>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                   placeholder="At least 6 characters" minLength={6} required />
          </div>
          <button className="btn btn-primary btn-block" disabled={busy}>
            {busy ? 'Creating…' : 'Create account'}
          </button>
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14, textAlign: 'center' }}>
            <span className="muted" style={{ fontSize: '.88rem' }}>Already have an account? </span>
            <Link to="/login" style={{ fontWeight: 600 }}>Log in</Link>
          </div>
        </form>
      </div>
      <div className="auth-visual">
        <AiImage prompt="friends having chai on a balcony of an Indian apartment, city skyline sunset, warm candid photo, photorealistic" seed={77} fallback={IMG.city} alt="" w={900} h={800} />
        <div className="auth-quote">
          <p>"{quote.text}"</p>
          <span>— {quote.author}</span>
        </div>
      </div>
    </div>
  )
}
