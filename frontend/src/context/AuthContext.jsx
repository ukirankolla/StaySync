import { createContext, useContext, useEffect, useState } from 'react'
import { api, getToken, setToken, clearToken } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (getToken()) {
      api('/auth/me')
        .then(setUser)
        .catch(() => clearToken())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (payload) => {
    const res = await api('/auth/login', { method: 'POST', body: payload })
    setToken(res.access_token)
    setUser(res.user)
    return res.user
  }

  const register = async (payload) => {
    const res = await api('/auth/register', { method: 'POST', body: payload })
    setToken(res.access_token)
    setUser(res.user)
    return res.user
  }

  const verifyOtp = async (payload) => {
    const res = await api('/auth/otp/verify', { method: 'POST', body: payload })
    setToken(res.access_token)
    setUser(res.user)
    return res.user
  }

  const logout = () => {
    clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, verifyOtp, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
