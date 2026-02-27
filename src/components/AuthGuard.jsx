import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { getCurrentUser } from '../services/auth'

function AuthGuard({ children }) {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    getCurrentUser()
      .then(() => setStatus('authenticated'))
      .catch(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setStatus('unauthenticated')
      })
  }, [])

  if (status === 'checking') return (
    <div className="bg-[#0a0a0f] min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" role="status" aria-label="Loading" />
    </div>
  )

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }

  return children
}

export default AuthGuard
