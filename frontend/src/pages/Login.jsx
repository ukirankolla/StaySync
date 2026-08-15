import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IMG } from '../lib/images'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    const body = identifier.includes('@')
      ? { email: identifier, password }
      : { phone: identifier, password }
    try {
      await login(body)
      navigate('/discover')
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
          <h2 className="center">Log in to StaySync</h2>
          {location.state?.notice && <div className="alert alert-success">{location.state.notice}</div>}
          {error && <div className="alert">{error}</div>}
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
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
          <div className="form-note">
            Prefer a code? <Link to="/otp">Log in with OTP</Link>
          </div>
          <div className="form-note">
            <Link to="/forgot-password">Forgot password?</Link>
          </div>
          <div className="form-note">
            New here? <Link to="/register">Create an account</Link>
          </div>
        </form>
      </div>
      <div className="auth-visual">
        <img src={IMG.heroAlt} alt="" />
        <div className="auth-quote">
          <p>“The compatibility score made choosing a flatmate feel safe and easy.”</p>
          <span>— StaySync member</span>
        </div>
      </div>
    </div>
  )
}
