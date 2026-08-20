import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { AUTH_IMAGES } from '../lib/images'

const LOGIN_QUOTES = [
  { text: "The compatibility score made choosing a flatmate feel safe and easy.", author: "Priya, Bengaluru" },
  { text: "Found someone who matches my sleep schedule and budget perfectly.", author: "Arjun, Delhi" },
  { text: "The AI matching is genuinely smart — it got my lifestyle right.", author: "Neha, Mumbai" },
]

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [showOtpSuggestion, setShowOtpSuggestion] = useState(false)
  const [quote] = useState(() => LOGIN_QUOTES[Math.floor(Math.random() * LOGIN_QUOTES.length)])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    setShowOtpSuggestion(false)
    const body = identifier.includes('@')
      ? { email: identifier, password }
      : { phone: identifier, password }
    try {
      await login(body)
      navigate('/discover')
    } catch (err) {
      setError(err.message)
      if (err.message.includes('OTP') || err.message.includes('no password')) {
        setShowOtpSuggestion(true)
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-panel">
        <form className="form card" onSubmit={submit}>
          <h2 className="center">Welcome back</h2>
          <p className="center muted" style={{ fontSize: '.9rem', marginTop: -4 }}>Log in to find your perfect flatmate</p>
          {location.state?.notice && <div className="alert alert-success">{location.state.notice}</div>}
          {error && <div className="alert">{error}</div>}
          {showOtpSuggestion && (
            <div className="alert alert-info">
              <strong>Try OTP login instead?</strong>
              <div style={{ marginTop: 6 }}>
                <Link to="/otp" style={{ fontWeight: 600 }}>Log in with OTP →</Link>
              </div>
            </div>
          )}
          <div className="field">
            <label>Email or phone</label>
            <input className="input" value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                   placeholder="you@example.com or +91..." required />
          </div>
          <div className="field">
            <label>Password</label>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                   placeholder="••••••••" required />
          </div>
          <button className="btn btn-primary btn-block" disabled={busy}>
            {busy ? 'Logging in…' : 'Log in'}
          </button>
          <div className="form-note">
            Prefer a code? <Link to="/otp">Log in with OTP</Link>
          </div>
          <div className="form-note">
            <Link to="/forgot-password">Forgot password?</Link>
          </div>
          <div style={{ borderTop: '1px solid var(--border)', paddingTop: 14, textAlign: 'center' }}>
            <span className="muted" style={{ fontSize: '.88rem' }}>New here? </span>
            <Link to="/register" style={{ fontWeight: 600 }}>Create an account</Link>
          </div>
        </form>
      </div>
      <div className="auth-visual">
        <img src={AUTH_IMAGES.login} alt="" />
        <div className="auth-quote">
          <p>"{quote.text}"</p>
          <span>— {quote.author}</span>
        </div>
      </div>
    </div>
  )
}
