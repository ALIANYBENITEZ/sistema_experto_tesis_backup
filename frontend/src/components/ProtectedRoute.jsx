import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ adminOnly = false }) {
  const { user, loading, authState } = useAuth()

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    )
  }

  // No autenticado o en proceso de 2FA → ir al login
  if (!user || authState !== 'authenticated') return <Navigate to="/login" replace />
  if (adminOnly && user.rol !== 'administrador' && user.rol !== 'propietario') return <Navigate to="/dashboard" replace />

  return <Outlet />
}
