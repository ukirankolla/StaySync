import React, { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api, wsUrl } from '../api/client'

export default function Chat() {
  const { connectionId } = useParams()
  const navigate = useNavigate()
  const [conns, setConns] = useState([])
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')
  const [online, setOnline] = useState(new Set())
  const [err, setErr] = useState('')
  const wsRef = useRef(null)
  const bottomRef = useRef(null)
  const userRef = useRef(null)

  useEffect(() => {
    api('/matching/connections').then(setConns).catch(() => {})
    api('/auth/me').then((u) => (userRef.current = u.id)).catch(() => {})
  }, [])

  useEffect(() => {
    const ws = new WebSocket(wsUrl())
    wsRef.current = ws
    ws.onopen = () => ws.send(JSON.stringify({ type: 'ping' }))
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'presence') setOnline(new Set(msg.data.online))
      if (msg.type === 'message' && String(msg.data.connection_id) === String(connectionId)) {
        setMessages((m) => {
          if (m.some((x) => x.id === msg.data.id)) return m
          return [...m, msg.data]
        })
      }
    }
    return () => ws.close()
  }, [connectionId])

  useEffect(() => {
    if (connectionId && connectionId !== 'new') {
      api(`/chat/connections/${connectionId}/messages`).then(setMessages).catch(() => {})
    }
  }, [connectionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (e) => {
    e.preventDefault()
    if (!text.trim() || !connectionId || connectionId === 'new') return
    try {
      const msg = await api(`/chat/connections/${connectionId}/messages`, { method: 'POST', body: { content: text.trim() } })
      setMessages((m) => (m.some((x) => x.id === msg.id) ? m : [...m, msg]))
      setText('')
    } catch (e2) {
      setErr(e2.message)
    }
  }

  const active = conns.find((c) => String(c.id) === String(connectionId))

  return (
    <div className="chat-layout">
      <div className="chat-sidebar">
        <h3 className="mb-16">Conversations</h3>
        {conns.filter((c) => c.status === 'accepted').map((c) => (
          <div key={c.id}
               className={`conn-item ${String(c.id) === String(connectionId) ? 'active' : ''}`}
               onClick={() => navigate(`/chat/${c.id}`)}>
            <strong>{c.peer_name}</strong>
            <div className="muted" style={{ fontSize: '.82rem' }}>{c.last_message || 'Start chatting'}</div>
          </div>
        ))}
        {conns.filter((c) => c.status === 'accepted').length === 0 && (
          <p className="muted">Accept a connection request to start chatting.</p>
        )}
      </div>

      <div className="chat-box">
        {!connectionId || connectionId === 'new' ? (
          <div className="empty">Select a conversation from the left.</div>
        ) : (
          <>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong>{active?.peer_name || 'Chat'}</strong>
              {online.has(active?.peer_id) && <span className="badge">online</span>}
            </div>
            <div className="messages">
              {messages.length === 0 && <p className="muted center">No messages yet — say hi!</p>}
              {messages.map((m) => (
                <div key={m.id} className={`msg ${m.sender_id === userRef.current ? 'me' : 'other'}`}>
                  {m.content}
                  <div className="msg-time">{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
            {err && <div className="alert" style={{ margin: 8 }}>{err}</div>}
            <form className="chat-input-row" onSubmit={send}>
              <input className="input" value={text} onChange={(e) => setText(e.target.value)}
                     placeholder="Type a message…" disabled={!active || active.status !== 'accepted'} />
              <button className="btn btn-primary" disabled={!text.trim() || !active}>Send</button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
