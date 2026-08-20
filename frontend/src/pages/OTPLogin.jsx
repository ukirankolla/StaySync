import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function OTPLogin() {
  const { verifyOtp } = useAuth()
  const navigate = useNavigate()
  const [identifier, setIdentifier] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState('request')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [otpCode, setOtpCode] = useState('')

  const request = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    setOtpCode('')
    try {
      const res = await api('/auth/otp/request', { method: 'POST', body: { identifier, purpose: 'login' } })
      setStep('verify')
      if (res.otp_code) setOtpCode(res.otp_code)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const verify = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await verifyOtp({ identifier, code, purpose: 'login' })
      navigate('/profile')
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
          <h2 className="center">Log in with OTP</h2>
          {error && <div className="alert">{error}</div>}
          <div className="field">
            <label>Email or phone</label>
            <input className="input" value={identifier} onChange={(e) => setIdentifier(e.target.value)}
                   placeholder="you@example.com or +91..." required />
          </div>
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Sending…' : 'Send code'}</button>
          <div className="form-note"><Link to="/login">Back to password login</Link></div>
        </form>
      ) : (
        <form className="form card" onSubmit={verify}>
          <h2 className="center">Enter the code</h2>
          {error && <div className="alert">{error}</div>}
          {otpCode && (
            <div className="alert alert-info" style={{ textAlign: 'center' }}>
              <strong>Your OTP code</strong>
              <div style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '0.2em', margin: '12px 0', color: 'var(--accent)' }}>
                {otpCode}
              </div>
              <div style={{ fontSize: '.85rem', opacity: 0.8 }}>Enter this code below to verify your identity.</div>
            </div>
          )}
          <div className="field">
            <label>6-digit code</label>
            <input className="input" value={code} onChange={(e) => setCode(e.target.value)} placeholder="000000" required />
          </div>
          <button className="btn btn-primary btn-block" disabled={busy}>{busy ? 'Verifying…' : 'Verify & log in'}</button>
          <div className="form-note">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => { setStep('request'); setOtpCode(''); }}>← Send another code</button>
          </div>
        </form>
      )}
    </div>
  )
}
