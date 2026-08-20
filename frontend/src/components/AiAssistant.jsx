import React, { useState, useRef, useEffect } from 'react'

const SUGGESTIONS = [
  "How does compatibility scoring work?",
  "What makes a good roommate match?",
  "How do I verify my profile?",
  "Tell me about StaySync's safety features",
  "How do roommate groups work?",
  "What cities is StaySync available in?",
]

const RESPONSES = {
  compatibility: "Our AI analyzes 12 lifestyle factors — sleep schedule, cleanliness, noise tolerance, budget, and more. Each match comes with transparent reasons so you know exactly why you're compatible.",
  verify: "You can verify your profile in two ways: email OTP verification for a basic badge, or government ID verification for a trusted identity badge. Both boost your trust score with potential roommates.",
  safety: "StaySync has 24/7 moderation, report/block tools, and government ID verification. We review all reports with our AI moderation agent and take swift action against fake profiles.",
  groups: "Create a group, invite compatible roommates, set a shared budget and city preference, then browse flat listings together. It's the smart way to find a flat with people you actually get along with.",
  cities: "StaySync is currently live in 6 Indian cities with more coming soon. We're expanding based on demand — join up and let us know where you'd like us next!",
  default: "Great question! StaySync uses AI-powered matching to connect you with compatible roommates based on lifestyle, budget, and preferences. Try browsing your matches to see it in action!"
}

function getResponse(input) {
  const lower = input.toLowerCase()
  if (lower.includes('compat') || lower.includes('match') || lower.includes('score') || lower.includes('work'))
    return RESPONSES.compatibility
  if (lower.includes('verif') || lower.includes('badge') || lower.includes('id'))
    return RESPONSES.verify
  if (lower.includes('safe') || lower.includes('report') || lower.includes('block') || lower.includes('moder'))
    return RESPONSES.safety
  if (lower.includes('group') || lower.includes('team') || lower.includes('flat'))
    return RESPONSES.groups
  if (lower.includes('cit') || lower.includes('where') || lower.includes('live') || lower.includes('avail'))
    return RESPONSES.cities
  return RESPONSES.default
}

export default function AiAssistant() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hi! I'm StaySync AI. Ask me anything about finding roommates, compatibility scoring, or how the platform works." }
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = (text) => {
    const msg = text || input
    if (!msg.trim()) return
    setMessages((m) => [...m, { role: 'user', text: msg }])
    setInput('')
    setTyping(true)
    setTimeout(() => {
      setMessages((m) => [...m, { role: 'bot', text: getResponse(msg) }])
      setTyping(false)
    }, 800 + Math.random() * 700)
  }

  return (
    <div className="ai-assistant">
      {open && (
        <div className="ai-chat-popup">
          <div className="ai-chat-header">
            <span style={{ fontSize: '1.2rem' }}>🤖</span>
            <h4>StaySync AI Assistant</h4>
            <div className="live-indicator" style={{ marginLeft: 'auto' }}>
              <span className="live-dot" /> Live
            </div>
          </div>
          <div className="ai-chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`ai-msg ${m.role}`}>{m.text}</div>
            ))}
            {typing && (
              <div className="typing-indicator" style={{ alignSelf: 'flex-start' }}>
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <div style={{ padding: '8px 12px', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {SUGGESTIONS.slice(0, 3).map((s) => (
              <button key={s} className="btn btn-ghost btn-sm"
                style={{ fontSize: '.75rem', padding: '4px 10px' }}
                onClick={() => send(s)}>
                {s.length > 30 ? s.slice(0, 30) + '…' : s}
              </button>
            ))}
          </div>
          <form className="ai-chat-input" onSubmit={(e) => { e.preventDefault(); send() }}>
            <input className="input" value={input} onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about StaySync..." style={{ fontSize: '.88rem' }} />
            <button className="btn btn-primary btn-sm" type="submit" disabled={!input.trim()}>Send</button>
          </form>
        </div>
      )}
      <button className="ai-assistant-btn" onClick={() => setOpen(!open)}
        title="AI Assistant">
        {open ? '✕' : '🤖'}
      </button>
    </div>
  )
}
