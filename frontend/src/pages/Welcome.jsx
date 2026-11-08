import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const SLIDES = [
  { icon: '🏠', title: 'Find the right roommate', text: 'Answer a short lifestyle profile and see people whose habits actually fit yours.' },
  { icon: '🤝', title: 'Compatibility you can understand', text: 'Every match comes with plain-language reasons, so you know why, not just a number.' },
  { icon: '🔑', title: 'Then find the flat together', text: 'Chat, form a group, agree house rules and browse flats for your shared budget.' },
]

export const WELCOME_KEY = 'staysync_welcome_seen'

export default function Welcome() {
  const navigate = useNavigate()
  const [i, setI] = useState(0)
  const last = i === SLIDES.length - 1
  const done = (to) => {
    try { localStorage.setItem(WELCOME_KEY, '1') } catch { /* private mode */ }
    navigate(to, { replace: true })
  }
  const s = SLIDES[i]
  return (
    <div className="q-card" style={{ textAlign: 'center', paddingTop: 40 }}>
      <div style={{ fontSize: '4rem' }} aria-hidden="true">{s.icon}</div>
      <h2 style={{ marginTop: 16 }}>{s.title}</h2>
      <p className="muted" style={{ maxWidth: 360, margin: '8px auto 24px' }}>{s.text}</p>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 24 }}>
        {SLIDES.map((_, n) => (
          <span key={n} style={{ width: n === i ? 22 : 8, height: 8, borderRadius: 8, background: n === i ? 'var(--primary, #6366f1)' : 'rgba(148,163,184,.5)', transition: 'width .2s' }} />
        ))}
      </div>
      {last ? (
        <>
          <button className="btn btn-primary btn-block" onClick={() => done('/register')}>Get started</button>
          <button className="btn btn-ghost btn-block mt-8" onClick={() => done('/login')}>I already have an account</button>
        </>
      ) : (
        <>
          <button className="btn btn-primary btn-block" onClick={() => setI(i + 1)}>Next</button>
          <button className="btn btn-ghost btn-block mt-8" onClick={() => done('/login')}>Skip</button>
        </>
      )}
    </div>
  )
}
