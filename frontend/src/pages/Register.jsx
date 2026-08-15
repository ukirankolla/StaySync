import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IMG } from '../lib/images'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

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
          <h2 className="center">Create your StaySync account</h2>
          {error && <div className="alert">{error}</div>}
          <div className="field">
            <label>Full name</label>
            <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Your name" required />
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
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Creating…' : 'Create account'}</button>
          <div className="form-note">
            Already have an account? <Link to="/login">Log in</Link>
          </div>
        </form>
      </div>
      <div className="auth-visual">
        <img src={IMG.city} alt="" />
        <div className="auth-quote">
          <p>“Found a roommate who matches my routine and my budget in a single evening.”</p>
          <span>— StaySync member</span>
        </div>
      </div>
    </div>
  )
}
