import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'

const Icon = ({ children }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
       strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{children}</svg>
)

const TABS = [
  { to: '/discover', label: 'Discover', match: ['/discover', '/questionnaire'],
    icon: <Icon><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></Icon> },
  { to: '/listings', label: 'Flats', match: ['/listings'],
    icon: <Icon><path d="M3 11.5 12 4l9 7.5" /><path d="M5 10v10h14V10" /><path d="M10 20v-6h4v6" /></Icon> },
  { to: '/connections', label: 'Chats', match: ['/connections', '/chat'],
    icon: <Icon><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.5-4.8A8 8 0 1 1 21 12Z" /></Icon> },
  { to: '/groups', label: 'Groups', match: ['/groups'],
    icon: <Icon><circle cx="9" cy="8" r="3.2" /><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" /><path d="M16 5.2a3.2 3.2 0 0 1 0 5.6" /><path d="M18 14.3c2 .7 3.5 2.6 3.5 5.7" /></Icon> },
  { to: '/profile', label: 'Profile', match: ['/profile', '/admin', '/hostels'],
    icon: <Icon><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" /></Icon> },
]

/** App-style tab bar. Shown on phones only (see .bottom-nav in styles.css). */
export default function BottomNav() {
  const { pathname } = useLocation()
  return (
    <nav className="bottom-nav" aria-label="Main">
      {TABS.map((t) => {
        const active = t.match.some((m) => pathname === m || pathname.startsWith(m + '/'))
        return (
          <NavLink key={t.to} to={t.to} className={`bottom-tab${active ? ' active' : ''}`} aria-current={active ? 'page' : undefined}>
            <span className="bottom-tab-icon">{t.icon}</span>
            <span className="bottom-tab-label">{t.label}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}
