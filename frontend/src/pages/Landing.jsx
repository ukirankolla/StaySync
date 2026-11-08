import React, { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IMG, HERO_IMAGES, STEP_IMAGES } from '../lib/images'
import ParticleField from '../components/ParticleField'

const STEPS = [
  { title: 'Create a profile', text: 'Share your budget, location, routines and living expectations through a short guided questionnaire.',
    img: STEP_IMAGES.profile, icon: '👤' },
  { title: 'Find compatible people', text: 'StaySync compares preferences and shows potential roommates, with clear reasons behind every recommendation.',
    img: STEP_IMAGES.questionnaire, icon: '🤝' },
  { title: 'Connect before committing', text: 'Review profiles, chat, discuss boundaries and decide together whether you want to live together.',
    img: STEP_IMAGES.match, icon: '💬' },
  { title: 'Choose a place together', text: 'Explore a PG, hostel or rental that fits both budgets and locations.',
    img: STEP_IMAGES.flat, icon: '🏠' },
]

const DIMENSIONS = [
  { title: 'Daily rhythm', text: 'Sleep and wake times, study or work hours.' },
  { title: 'Living standards', text: 'Cleanliness, chores and shared-space expectations.' },
  { title: 'Noise & guests', text: 'Quiet hours, music, visitors and social activity.' },
  { title: 'Lifestyle choices', text: 'Food, smoking and drinking preferences, and pets.' },
  { title: 'Practical fit', text: 'Budget, location, move-in date and room type.' },
]

const TRUST = [
  { title: 'You control what you share', text: 'Hide your profile any time, edit your answers, or delete your account and data.' },
  { title: 'Consent first', text: 'Chat opens only after both people accept a connection.' },
  { title: 'Report & block', text: 'Report profiles or listings and block anyone, in one tap.' },
  { title: 'Not a guarantee', text: 'Scores are recommendations, not guarantees. Talk it through and decide for yourself.' },
]

export default function Landing() {
  const { user } = useAuth()
  const [heroIdx, setHeroIdx] = useState(0)
  const [scrollY, setScrollY] = useState(0)
  const sectionsRef = useRef([])

  useEffect(() => {
    const t = setInterval(() => setHeroIdx((i) => (i + 1) % HERO_IMAGES.length), 6000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    )
    sectionsRef.current.forEach((el) => el && observer.observe(el))
    return () => observer.disconnect()
  }, [])

  const addRef = (el) => {
    if (el && !sectionsRef.current.includes(el)) sectionsRef.current.push(el)
  }

  return (
    <div>
      <section className="hero" style={{ transform: `translateY(${scrollY * 0.1}px)` }}>
        {HERO_IMAGES.map((url, i) => (
          <img key={i} src={url} alt="" className={`hero-bg ${i === heroIdx ? 'hero-fade' : ''}`}
               style={{ opacity: i === heroIdx ? 1 : 0, transition: 'opacity 1.5s ease', position: 'absolute' }} />
        ))}
        <ParticleField count={20} />
        <div className="hero-inner">
          <img src="/logo.png" alt="StaySync" className="page-logo" width="64" height="64" />
                    <span className="hero-eyebrow">
            <span className="pulse-dot" />
            The roommate compatibility platform
          </span>
          <h1>
            Find your people.
            <br />
            <span className="gradient-text">Build your future.</span>
          </h1>
          <p>SyncStay helps people find compatible roommates before they move in — and helps colleges create better-matched hostel rooms. Don't just find a place to stay. Find the right person to stay with.</p>
          <div className="hero-actions">
            {user ? (
              <Link to="/discover" className="btn btn-primary btn-lg">Find roommates</Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">Get started free</Link>
                <Link to="/login" className="btn btn-ghost btn-lg btn-ghost-light">Log in</Link>
              </>
            )}
          </div>
        </div>
      </section>

      <div ref={addRef} className="fade-in-up" style={{ marginTop: 56 }}>
        <h2 className="section-title">A room is more than four walls</h2>
        <p className="section-sub">The room may be affordable and well located, but the people sharing it may have very different routines, expectations and habits. People don't only need a place to stay — they need a living arrangement that fits how they live.</p>
      </div>

      <div ref={addRef} className="fade-in-up" style={{ marginTop: 48 }}>
        <h2 className="section-title">How it works</h2>
        <p className="section-sub">From moving city to finding your people.</p>
        <div className="grid grid-3 steps-grid">
          {STEPS.map((s, i) => (
            <div className="card step-card" key={s.title}>
              <img className="card-img" src={s.img} alt={s.title} loading="lazy" />
              <div className="step-num">{i + 1}</div>
              <div className="feature-icon">{s.icon}</div>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64 }}>
        <h2 className="section-title">Compatibility, explained</h2>
        <p className="section-sub">No mysterious score. StaySync compares practical living preferences and shows you why a match is recommended.</p>
        <div className="features">
          {DIMENSIONS.map((d) => (
            <div className="card feature" key={d.title}>
              <h3>{d.title}</h3>
              <p>{d.text}</p>
            </div>
          ))}
        </div>
        <p className="center muted" style={{ fontSize: '.85rem', marginTop: 12 }}>Scores are recommendations, not guarantees.</p>
      </div>

      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64 }}>
        <h2 className="section-title">For colleges &amp; hostels</h2>
        <p className="section-sub">Better-informed room allocation: students complete a short lifestyle form, StaySync suggests compatible pairings within your room capacity and hostel blocks, your staff review and decide, and students have a clear way to request a change. Staff keep the final say.</p>
        <p className="center">
          <Link to={user ? '/hostels' : '/register'} className="btn btn-primary btn-lg">{user ? 'Open hostel tools' : 'Get started'}</Link>
        </p>
      </div>

      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64 }}>
        <h2 className="section-title">Trust is part of the product</h2>
        <p className="section-sub">Roommate decisions affect people's homes, privacy and personal safety.</p>
        <div className="features">
          {TRUST.map((t) => (
            <div className="card feature" key={t.title}>
              <h3>{t.title}</h3>
              <p>{t.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64, textAlign: 'center' }}>
        <div className="card" style={{ padding: 48, background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.15)' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: 12 }}>Better roommates. Better routines. More room to grow.</h2>
          <p className="muted" style={{ fontSize: '1.05rem', marginBottom: 28 }}>A compatible living environment won't build your career for you, but it can make learning, work and personal goals easier to pursue.</p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            {user ? (
              <Link to="/discover" className="btn btn-primary btn-lg">Find roommates</Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">Get started — it's free</Link>
                <Link to="/login" className="btn btn-ghost btn-lg">Log in</Link>
              </>
            )}
          </div>
        </div>
      </div>

      <p className="center muted mt-24" style={{ fontSize: '.85rem' }}>
        StaySync never guarantees a match is safe — always meet in public, verify details, and trust your judgement.
      </p>
    </div>
  )
}
