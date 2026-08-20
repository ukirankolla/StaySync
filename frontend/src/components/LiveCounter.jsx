import React, { useEffect, useState } from 'react'

export default function LiveCounter({ end, duration = 2000, prefix = '', suffix = '' }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    let start = 0
    const startTime = Date.now()
    const timer = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.round(eased * end))
      if (progress < 1) requestAnimationFrame(timer)
    }
    requestAnimationFrame(timer)
  }, [end, duration])

  return <span>{prefix}{count.toLocaleString('en-IN')}{suffix}</span>
}
