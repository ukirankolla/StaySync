import React from 'react'
import { avatarGradient, initials } from '../lib/images'

export default function Avatar({ name, photo, size = 48, style }) {
  if (photo) {
    return <img src={photo} alt={name} className="avatar-img" style={{ width: size, height: size, ...style }} />
  }
  return (
    <div className="avatar" style={{ width: size, height: size, fontSize: size * 0.36, background: avatarGradient(name), ...style }}>
      {initials(name)}
    </div>
  )
}
