import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, wsUrl } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function MessageToasts() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [toasts, setToasts] = useState([])
  const namesRef = useRef({})
  const idRef = useRef(0)

  useEffect(() => {
    if (!user) return
    api('/matching/connections')
      .then((conns) => {
        const map = {}
        conns.forEach((c) => { map[c.peer_id] = c.peer_name })
        namesRef.current = map
      })
      .catch(() => {})
  }, [user])

  useEffect(() => {
    if (!user) return
    const ws = new WebSocket(wsUrl())
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type !== 'message') return
      const senderName = namesRef.current[msg.data.sender_id] || 'Someone'
      const id = ++idRef.current
      setToasts((t) => [...t, { id, sender: senderName, content: msg.data.content, connectionId: msg.data.connection_id }])
      setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 5000)
    }
    return () => ws.close()
  }, [user])

  if (toasts.length === 0) return null

  return (
    <div className="toast-stack">
      {toasts.map((t) => (
        <div key={t.id} className="toast" onClick={() => { navigate(`/chat/${t.connectionId}`); setToasts((x) => x.filter((y) => y.id !== t.id)) }}>
          <div>
            <b>{t.sender}</b>
            <div style={{ opacity: .85, fontSize: '.85rem' }}>{t.content.length > 60 ? `${t.content.slice(0, 60)}…` : t.content}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
