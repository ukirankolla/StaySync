import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import MessageToasts from './components/MessageToasts'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import OTPLogin from './pages/OTPLogin'
import Profile from './pages/Profile'
import Questionnaire from './pages/Questionnaire'
import Discover from './pages/Discover'
import Connections from './pages/Connections'
import Chat from './pages/Chat'
import Groups from './pages/Groups'
import Listings from './pages/Listings'
import Admin from './pages/Admin'

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-muted">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AdminRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-muted">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'admin') return <Navigate to="/discover" replace />
  return children
}

export default function App() {
  const { user } = useAuth()
  return (
    <div className="app">
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={user ? <Navigate to="/discover" replace /> : <Login />} />
          <Route path="/register" element={user ? <Navigate to="/discover" replace /> : <Register />} />
          <Route path="/otp" element={user ? <Navigate to="/discover" replace /> : <OTPLogin />} />
          <Route path="/profile" element={<Protected><Profile /></Protected>} />
          <Route path="/questionnaire" element={<Protected><Questionnaire /></Protected>} />
          <Route path="/discover" element={<Protected><Discover /></Protected>} />
          <Route path="/connections" element={<Protected><Connections /></Protected>} />
          <Route path="/chat/:connectionId" element={<Protected><Chat /></Protected>} />
          <Route path="/groups" element={<Protected><Groups /></Protected>} />
          <Route path="/listings" element={<Protected><Listings /></Protected>} />
          <Route path="/admin" element={<AdminRoute><Admin /></AdminRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <MessageToasts />
    </div>
  )
}
