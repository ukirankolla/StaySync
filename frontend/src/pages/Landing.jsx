import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IMG, PORTRAITS } from '../lib/images'

const FEATURES = [
  { title: 'Compatibility scoring', text: 'Transparent lifestyle, budget, and routine matching with clear reasons — not a mystery number.', img: IMG.team },
  { title: 'Real-time chat', text: 'Connect with matched people and chat instantly after a mutual match.', img: IMG.chat },
  { title: 'Roommate groups', text: 'Form a group with compatible people, then hunt for a flat together.', img: IMG.friends },
  { title: 'Flat listings', text: 'Browse verified room and flat listings that fit your group’s budget and area.', img: IMG.home },
  { title: 'Safety tools', text: 'Report, block, and moderation reviews keep the community safe.', img: IMG.crowd },
  { title: 'Smarter matches', text: 'Ranking that learns and refines itself as the community grows.', img: IMG.office },
]

const STEPS = [
  { title: 'Create your profile', text: 'Tell us who you are, your city, and your budget.', img: PORTRAITS[1] },
  { title: 'Answer the lifestyle questionnaire', text: 'Sleep, cleanliness, routine — the things that actually matter.', img: IMG.plan },
  { title: 'Match & chat with compatible people', text: 'See transparent compatibility scores with reasons.', img: IMG.friends },
  { title: 'Form a group and find a flat', text: 'Hunt for a verified listing together.', img: IMG.home },
]

export default function Landing() {
  const { user } = useAuth()
  return (
    <div>
      <section className="hero">
        <img className="hero-bg" src={IMG.hero} alt="" />
        <div className="hero-inner">
          <span className="hero-eyebrow">Roommate + flat matching, done right</span>
          <h1>Find compatible roommates before you move</h1>
          <p>StaySync matches students and professionals by lifestyle, routine, budget, and housing preferences — so your next flatmate actually fits.</p>
          <div className="hero-actions">
            {user ? (
              <Link to="/discover" className="btn btn-primary btn-lg">Browse matches</Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">Get started free</Link>
                <Link to="/login" className="btn btn-ghost btn-lg btn-ghost-light">Log in</Link>
              </>
            )}
          </div>
        </div>
      </section>

      <div className="stats-bar">
        <div><strong>6</strong><span>cities live</span></div>
        <div><strong>100%</strong><span>score transparency</span></div>
        <div><strong>24/7</strong><span>moderation</span></div>
      </div>

      <h2 className="section-title">How it works</h2>
      <p className="section-sub">Four steps from sign-up to signed lease.</p>
      <div className="grid grid-3 steps-grid">
        {STEPS.map((s, i) => (
          <div className="card step-card" key={s.title}>
            <img className="card-img" src={s.img} alt="" loading="lazy" />
            <div className="step-num">{i + 1}</div>
            <h3>{s.title}</h3>
            <p>{s.text}</p>
          </div>
        ))}
      </div>

      <h2 className="section-title">Why StaySync</h2>
      <div className="features">
        {FEATURES.map((f) => (
          <div className="card feature" key={f.title}>
            <img className="card-img" src={f.img} alt="" loading="lazy" />
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
