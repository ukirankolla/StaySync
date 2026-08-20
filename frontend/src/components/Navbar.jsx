import React from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <Link to={user ? '/discover' : '/'} className="brand">
        <span className="brand-icon">🏠</span>
        StaySync
      </Link>
      <div className="nav-links">
        {user ? (
          <>
            <NavLink to="/discover" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Discover</NavLink>
            <NavLink to="/connections" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Connections</NavLink>
            <NavLink to="/groups" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Groups</NavLink>
            <NavLink to="/listings" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Flats</NavLink>
            {user.role === 'admin' && (
              <NavLink to="/admin" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Admin</NavLink>
            )}
            <NavLink to="/profile" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Profile</NavLink>
            <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="btn btn-primary btn-sm">Get Started</Link>
          </>
        )}
      </div>
    </nav>
  )
}
