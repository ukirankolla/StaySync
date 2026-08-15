import React, { useState } from 'react'
import { aiImage } from '../lib/images'

export default function AiImage({ prompt, seed = 1, fallback, alt = '', className, w = 900, h = 600, ...rest }) {
  const [src, setSrc] = useState(() => aiImage(prompt, { w, h, seed }))
  const onError = () => {
    if (fallback) setSrc(fallback)
    else if (src) setSrc(null)
  }
  if (!src) return null
  return <img src={src} alt={alt} loading="lazy" className={className} onError={onError} {...rest} />
}
