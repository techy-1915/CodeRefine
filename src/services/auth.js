const API_URL = import.meta.env.VITE_API_URL

export async function login(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'Login failed')
  }
  const data = await response.json()
  localStorage.setItem('access_token', data.access_token)
  if (data.refresh_token) {
    localStorage.setItem('refresh_token', data.refresh_token)
  }
  return data
}

export async function signup(name, email, password) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new Error(data.detail || 'Registration failed')
  }
  const data = await response.json()
  localStorage.setItem('access_token', data.access_token)
  if (data.refresh_token) {
    localStorage.setItem('refresh_token', data.refresh_token)
  }
  return data
}

export async function logout() {
  const token = localStorage.getItem('access_token')
  if (token) {
    await fetch(`${API_URL}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => {})
  }
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function refreshToken() {
  const token = localStorage.getItem('refresh_token')
  if (!token) throw new Error('No refresh token')
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: token }),
  })
  if (!response.ok) throw new Error('Token refresh failed')
  const data = await response.json()
  localStorage.setItem('access_token', data.access_token)
  return data
}

export async function getCurrentUser() {
  const token = localStorage.getItem('access_token')
  if (!token) throw new Error('Not authenticated')
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) throw new Error('Not authenticated')
  return response.json()
}
