const TOKEN_KEY = 'staysync_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export async function api(path, { method = 'GET', body, headers = {} } = {}) {
  const token = getToken()
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...headers },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)

  const res = await fetch(`/api${path}`, opts)
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const err = new Error(data?.detail || `Request failed (${res.status})`)
    err.status = res.status
    err.detail = data?.detail
    throw err
  }
  return data
}

export function wsUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const token = getToken()
  return `${proto}://${window.location.host}/api/chat/ws?token=${encodeURIComponent(token || '')}`
}
