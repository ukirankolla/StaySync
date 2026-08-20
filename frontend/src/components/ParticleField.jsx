import React, { useEffect, useRef } from 'react'

export default function ParticleField({ count = 30 }) {
  const containerRef = useRef(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const particles = []
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div')
      p.className = 'ai-particle'
      const size = Math.random() * 6 + 2
      const x = Math.random() * 100
      const dur = Math.random() * 15 + 10
      const delay = Math.random() * 10
      const hue = Math.random() > 0.5 ? '239, 102, 241' : '6, 182, 212'
      Object.assign(p.style, {
        width: `${size}px`,
        height: `${size}px`,
        left: `${x}%`,
        background: `radial-gradient(circle, rgba(${hue}, 0.6), transparent 70%)`,
        animationDuration: `${dur}s`,
        animationDelay: `${delay}s`,
      })
      container.appendChild(p)
      particles.push(p)
    }
    return () => particles.forEach((p) => p.remove())
  }, [count])

  return <div ref={containerRef} className="ai-particles" />
}
