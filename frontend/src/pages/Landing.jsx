import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const FEATURES = [
  { title: 'Compatibility scoring', text: 'Transparent lifestyle, budget, and routine matching with clear reasons — not a mystery number.' },
  { title: 'Real-time chat', text: 'Connect with matched people and chat instantly after a mutual match.' },
  { title: 'Roommate groups', text: 'Form a group with compatible people, then hunt for a flat together.' },
  { title: 'Flat listings', text: 'Browse verified room and flat listings that fit your group’s budget and area.' },
  { title: 'Safety tools', text: 'Report, block, and moderation reviews keep the community safe.' },
  { title: 'ML-powered matches', text: 'A learning model refines recommendations as the community grows.' },
]

export default function Landing() {
  const { user } = useAuth()
  return (
    <div>
      <section className="hero">
        <h1>Find compatible roommates before you move</h1>
        <p>StaySync matches students and professionals by lifestyle, routine, budget, and housing preferences — so your next flatmate actually fits.</p>
        <div className="hero-actions">
          {user ? (
            <Link to="/discover" className="btn btn-primary">Browse matches</Link>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary">Get started free</Link>
              <Link to="/login" className="btn btn-ghost">Log in</Link>
            </>
          )}
        </div>
      </section>

      <h2 className="section-title">How it works</h2>
      <p className="section-sub">Four steps from sign-up to signed lease.</p>
      <div className="grid grid-3">
        {['Create your profile', 'Answer the lifestyle questionnaire', 'Match & chat with compatible people', 'Form a group and find a flat'].map((s, i) => (
          <div className="feature" key={s}>
            <h3>{i + 1}. {s}</h3>
          </div>
        ))}
      </div>

      <h2 className="section-title">Why StaySync</h2>
      <div className="features">
        {FEATURES.map((f) => (
          <div className="feature" key={f.title}>
            <h3>{f.title}</h3>
            <p>{f.text}</p>
          </div>
        ))}
      </div>

      <p className="center muted mt-24">
        StaySync never guarantees a match is safe — always meet in public, verify details, and trust your judgement.
      </p>
    </div>
  )
}
