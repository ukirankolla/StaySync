import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [step, setStep] = useState('request')
  const [identifier, setIdentifier] = useState('')
  const [code, setCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [otpCode, setOtpCode] = useState('')

  const request = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    setOtpCode('')
    try {
      const res = await api('/auth/forgot', { method: 'POST', body: { identifier } })
      setStep('verify')
      if (res.otp_code) setOtpCode(res.otp_code)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const reset = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await api('/auth/reset', { method: 'POST', body: { identifier, code, new_password: newPassword } })
      navigate('/login', { state: { notice: 'Password updated. Log in with your new password.' } })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-24">
      {step === 'request' ? (
        <form className="form card" onSubmit={request}>
          <h2 className="center">Reset password</h2>
          <p className="muted center mb-16" style={{ fontSize: '.9rem' }}>We'll send a code to your email or phone.</p>
          {error && <div className="alert">{error}</div>}
          <div className="field">
            <label>Email or phone</label>
            <input className="input" value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                   placeholder="you@example.com or +91..." required />
          </div>
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Sending…' : 'Send code'}</button>
          <div className="form-note"><Link to="/login">Back to login</Link></div>
        </form>
      ) : (
        <form className="form card" onSubmit={reset}>
          <h2 className="center">Set a new password</h2>
          {error && <div className="alert">{error}</div>}
          {otpCode && (
            <div className="alert alert-info" style={{ textAlign: 'center' }}>
              <strong>Your reset code</strong>
              <div style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '0.2em', margin: '12px 0', color: 'var(--accent)' }}>
                {otpCode}
              </div>
              <div style={{ fontSize: '.85rem', opacity: 0.8 }}>Enter this code below to reset your password.</div>
            </div>
          )}
          <div className="field">
            <label>6-digit code</label>
            <input className="input" value={code} onChange={(e) => setCode(e.target.value)} placeholder="000000" required />
          </div>
          <div className="field">
            <label>New password</label>
            <input className="input" type="password" value={newPassword} minLength={6}
                   onChange={(e) => setNewPassword(e.target.value)} required />
          </div>
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Resetting…' : 'Reset password'}</button>
          <div className="form-note">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setStep('request'); setOtpCode(''); }}>← Send another code</button>
          </div>
        </form>
      )}
    </div>
  )
}
