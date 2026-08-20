import React, { useEffect, useState } from 'react'

export default function TypingEffect({ texts, speed = 50, pause = 2000 }) {
  const [textIdx, setTextIdx] = useState(0)
  const [charIdx, setCharIdx] = useState(0)
  const [deleting, setDeleting] = useState(false)
  const [display, setDisplay] = useState('')

  useEffect(() => {
    const current = texts[textIdx]
    if (!deleting) {
      if (charIdx < current.length) {
        const t = setTimeout(() => {
          setDisplay(current.slice(0, charIdx + 1))
          setCharIdx(charIdx + 1)
        }, speed)
        return () => clearTimeout(t)
      } else {
        const t = setTimeout(() => setDeleting(true), pause)
        return () => clearTimeout(t)
      }
    } else {
      if (charIdx > 0) {
        const t = setTimeout(() => {
          setDisplay(current.slice(0, charIdx - 1))
          setCharIdx(charIdx - 1)
        }, speed / 2)
        return () => clearTimeout(t)
      } else {
        setDeleting(false)
        setTextIdx((i) => (i + 1) % texts.length)
      }
    }
  }, [charIdx, deleting, textIdx, texts, speed, pause])

  return (
    <span>
      {display}
      <span style={{
        display: 'inline-block', width: '2px', height: '1em',
        background: 'var(--accent)', marginLeft: '2px',
        animation: 'blink 1s step-end infinite', verticalAlign: 'text-bottom'
      }} />
      <style>{`@keyframes blink { 50% { opacity: 0; } }`}</style>
    </span>
  )
}
