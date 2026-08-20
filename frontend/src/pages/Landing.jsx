import React, { useEffect, useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { IMG, HERO_IMAGES, STEP_IMAGES } from '../lib/images'
import ParticleField from '../components/ParticleField'
import TypingEffect from '../components/TypingEffect'
import LiveCounter from '../components/LiveCounter'

const TYPING_TEXTS = [
  'Find compatible roommates',
  'Match by lifestyle & budget',
  'AI-powered flat hunting',
  'Transparent compatibility scores',
  'Real-time chat with matches',
]

const STEPS = [
  { title: 'Create your profile', text: 'Tell us who you are, your city, and your budget. Our AI learns your preferences.',
    img: STEP_IMAGES.profile, icon: '👤' },
  { title: 'Answer the lifestyle questionnaire', text: 'Sleep, cleanliness, routine — the things that actually matter for compatibility.',
    img: STEP_IMAGES.questionnaire, icon: '📋' },
  { title: 'Match & chat instantly', text: 'See transparent compatibility scores with clear reasons. Start chatting immediately.',
    img: STEP_IMAGES.match, icon: '💬' },
  { title: 'Form a group & find a flat', text: 'Hunt for a verified listing together with your compatible roommates.',
    img: STEP_IMAGES.flat, icon: '🏠' },
]

const FEATURES = [
  { title: 'AI Compatibility Scoring', text: 'Transparent lifestyle, budget, and routine matching with clear reasons — not a mystery number.', icon: '🎯', gradient: 'var(--gradient)' },
  { title: 'Real-time Chat', text: 'Connect with matched people and chat instantly after a mutual match. No waiting.', icon: '⚡', gradient: 'var(--gradient-cool)' },
  { title: 'Roommate Groups', text: 'Form a group with compatible people, then hunt for a flat together as a team.', icon: '👥', gradient: 'var(--gradient-purple)' },
  { title: 'Smart Flat Listings', text: 'Browse verified room and flat listings that fit your group\'s budget and area preferences.', icon: '🏢', gradient: 'linear-gradient(135deg, #f59e0b, #ef4444)' },
  { title: 'Safety First', text: 'Report, block, and AI-powered moderation keep the community safe.', icon: '🛡️', gradient: 'var(--gradient-cool)' },
  { title: 'Machine Learning', text: 'Our matching algorithm learns from the community and refines itself for smarter recommendations.', icon: '🧠', gradient: 'var(--gradient-purple)' },
]

const TESTIMONIALS = [
  { name: 'Priya S.', role: 'Software Engineer, Bengaluru', text: 'StaySync matched me with a roommate who had the exact same sleep schedule. It\'s been 6 months and we\'re still going strong!' },
  { name: 'Arjun M.', role: 'MBA Student, Delhi', text: 'The compatibility score transparency is what sold me. I could see exactly why we matched — no black box.' },
  { name: 'Neha K.', role: 'Designer, Mumbai', text: 'Formed a group on StaySync and found our dream 3BHK in Koramangala within a week. The AI suggestions were spot on.' },
  { name: 'Rahul T.', role: 'Data Analyst, Pune', text: 'I was skeptical about finding roommates online, but the moderation and transparent scoring made me feel safe. Best decision.' },
]

export default function Landing() {
  const { user } = useAuth()
  const [heroIdx, setHeroIdx] = useState(0)
  const [testimonialIdx, setTestimonialIdx] = useState(0)
  const [scrollY, setScrollY] = useState(0)
  const sectionsRef = useRef([])

  useEffect(() => {
    const t = setInterval(() => setHeroIdx((i) => (i + 1) % HERO_IMAGES.length), 6000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    const t = setInterval(() => setTestimonialIdx((i) => (i + 1) % TESTIMONIALS.length), 5000)
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

  const currentTestimonial = TESTIMONIALS[testimonialIdx]

  return (
    <div>
      {/* Hero Section */}
      <section className="hero" style={{ transform: `translateY(${scrollY * 0.1}px)` }}>
        {HERO_IMAGES.map((url, i) => (
          <img key={i} src={url} alt="" className={`hero-bg ${i === heroIdx ? 'hero-fade' : ''}`}
               style={{ opacity: i === heroIdx ? 1 : 0, transition: 'opacity 1.5s ease', position: 'absolute' }} />
        ))}
        <ParticleField count={20} />
        <div className="hero-inner">
          <span className="hero-eyebrow">
            <span className="pulse-dot" />
            AI-Powered Roommate Matching
          </span>
          <h1>
            <TypingEffect texts={TYPING_TEXTS} speed={60} pause={2500} />
            <br />
            <span className="gradient-text">before you move</span>
          </h1>
          <p>StaySync uses machine learning to match students and professionals by lifestyle, routine, budget, and housing preferences — so your next flatmate actually fits.</p>
          <div className="hero-actions">
            {user ? (
              <Link to="/discover" className="btn btn-primary btn-lg">
                <span style={{ fontSize: '1.1rem' }}>🔍</span> Browse AI Matches
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">
                  <span style={{ fontSize: '1.1rem' }}>🚀</span> Get started free
                </Link>
                <Link to="/login" className="btn btn-ghost btn-lg btn-ghost-light">Log in</Link>
              </>
            )}
          </div>
          <div style={{ marginTop: 28, display: 'flex', gap: 20, justifyContent: 'center', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'rgba(255,255,255,0.7)', fontSize: '.85rem' }}>
              <span style={{ color: '#10b981', fontSize: '1rem' }}>✓</span> No credit card required
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'rgba(255,255,255,0.7)', fontSize: '.85rem' }}>
              <span style={{ color: '#10b981', fontSize: '1rem' }}>✓</span> AI-powered matching
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'rgba(255,255,255,0.7)', fontSize: '.85rem' }}>
              <span style={{ color: '#10b981', fontSize: '1rem' }}>✓</span> 100% score transparency
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <div className="stats-bar">
        <div>
          <strong><LiveCounter end={6} /></strong>
          <span>Cities live</span>
        </div>
        <div>
          <strong><LiveCounter end={100} suffix="%" /></strong>
          <span>Score transparency</span>
        </div>
        <div>
          <strong><LiveCounter end={24} suffix="/7" /></strong>
          <span>AI moderation</span>
        </div>
      </div>

      {/* How it works */}
      <div ref={addRef} className="fade-in-up">
        <h2 className="section-title">How it works</h2>
        <p className="section-sub">Four steps from sign-up to signed lease — powered by AI at every step.</p>
        <div className="grid grid-3 steps-grid">
          {STEPS.map((s, i) => (
            <div className="card step-card" key={s.title} style={{ animationDelay: `${i * 0.1}s` }}>
              <img className="card-img" src={s.img} alt={s.title} loading="lazy" />
              <div className="step-num">{i + 1}</div>
              <div className="feature-icon">{s.icon}</div>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Match Preview */}
      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64 }}>
        <h2 className="section-title">See AI matching in action</h2>
        <p className="section-sub">Our machine learning model analyzes 12 lifestyle factors to find your best matches.</p>
        <div className="card" style={{ maxWidth: 500, margin: '0 auto', padding: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
            <div className="feature-icon" style={{ background: 'var(--gradient)', color: '#fff', width: 44, height: 44, fontSize: '1.2rem' }}>🧠</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1rem' }}>AI Match Analysis</div>
              <div className="muted" style={{ fontSize: '.82rem' }}>Powered by RandomForest ML model</div>
            </div>
            <div className="live-indicator" style={{ marginLeft: 'auto' }}>
              <span className="live-dot" /> Live
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[
              { label: 'Sleep schedule', score: 92, color: 'var(--gradient)' },
              { label: 'Cleanliness', score: 88, color: 'var(--gradient-cool)' },
              { label: 'Budget overlap', score: 95, color: 'var(--gradient)' },
              { label: 'Social preference', score: 78, color: 'var(--gradient-purple)' },
              { label: 'Noise tolerance', score: 85, color: 'var(--gradient-cool)' },
            ].map((item) => (
              <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ width: 130, fontSize: '.85rem', color: 'var(--text-muted)' }}>{item.label}</span>
                <div className="breakdown-bar" style={{ flex: 1 }}>
                  <div style={{ width: `${item.score}%`, background: item.color, transition: 'width 1.5s ease' }} />
                </div>
                <span style={{ width: 40, textAlign: 'right', fontWeight: 700, fontSize: '.9rem' }}>{item.score}%</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 18, padding: '12px 16px', background: 'rgba(99, 102, 241, 0.08)', borderRadius: 12, fontSize: '.85rem', color: 'var(--text-muted)' }}>
            <span style={{ color: '#10b981', marginRight: 6 }}>✓</span>
            <strong style={{ color: 'var(--text)' }}>87% overall compatibility</strong> — Both prefer quiet after 10 PM, similar budget range, and same area preference.
          </div>
        </div>
      </div>

      {/* Features */}
      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64 }}>
        <h2 className="section-title">Why StaySync</h2>
        <p className="section-sub">Built for India's rental market, powered by modern AI.</p>
        <div className="features">
          {FEATURES.map((f, i) => (
            <div className="card feature" key={f.title} style={{ animationDelay: `${i * 0.08}s` }}>
              <div className="feature-icon" style={{ background: f.gradient, color: '#fff', fontSize: '1.3rem' }}>{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Testimonials */}
      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64 }}>
        <h2 className="section-title">Loved by roommates</h2>
        <p className="section-sub">Real stories from real StaySync users.</p>
        <div className="card" style={{ maxWidth: 560, margin: '0 auto', padding: 32, textAlign: 'center', minHeight: 200 }}>
          <div style={{ fontSize: '2.5rem', marginBottom: 16, opacity: 0.3 }}>"</div>
          <p style={{ fontSize: '1.1rem', lineHeight: 1.7, margin: '0 0 20px', color: 'var(--text)', fontWeight: 500 }}>
            {currentTestimonial.text}
          </p>
          <div>
            <div style={{ fontWeight: 700, color: 'var(--text)' }}>{currentTestimonial.name}</div>
            <div className="muted" style={{ fontSize: '.85rem' }}>{currentTestimonial.role}</div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 20 }}>
            {TESTIMONIALS.map((_, i) => (
              <button key={i} onClick={() => setTestimonialIdx(i)}
                style={{
                  width: i === testimonialIdx ? 24 : 8, height: 8, borderRadius: 4,
                  background: i === testimonialIdx ? 'var(--gradient)' : 'var(--glass)',
                  border: 'none', cursor: 'pointer', transition: 'all 0.3s ease',
                }} />
            ))}
          </div>
        </div>
      </div>

      {/* CTA */}
      <div ref={addRef} className="fade-in-up" style={{ marginTop: 64, textAlign: 'center' }}>
        <div className="card" style={{ padding: 48, background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.15)' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: 12 }}>Ready to find your perfect flatmate?</h2>
          <p className="muted" style={{ fontSize: '1.1rem', marginBottom: 28 }}>Join thousands of students and professionals who found their match on StaySync.</p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            {user ? (
              <Link to="/discover" className="btn btn-primary btn-lg">
                <span>🔍</span> Browse AI Matches
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">
                  <span>🚀</span> Get started — it's free
                </Link>
                <Link to="/login" className="btn btn-ghost btn-lg">Log in</Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="center muted mt-24" style={{ fontSize: '.85rem' }}>
        StaySync never guarantees a match is safe — always meet in public, verify details, and trust your judgement.
      </p>
    </div>
  )
}
