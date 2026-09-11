import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { login as apiLogin, logout as apiLogout, getMe, setup2FA, verify2FA } from '../api/authApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)
  // 2FA states
  const [authState, setAuthState] = useState(null) // null, '2fa_setup_required', '2fa_required', 'authenticated'
  const [partialToken, setPartialToken] = useState(null)
  const [qrCode, setQrCode] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      getMe()
        .then(({ data }) => { setUser(data.data); setAuthState('authenticated') })
        .catch(() => { localStorage.clear(); setAuthState(null) })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    // Limpiar tokens previos para evitar conflictos entre usuarios
    localStorage.clear()

    const { data } = await apiLogin(email, password)
    const result = data.data

    if (result.auth_state === 'authenticated') {
      // Acceso directo (sin 2FA o fallback)
      localStorage.setItem('access_token', result.access_token)
      localStorage.setItem('refresh_token', result.refresh_token)
      setUser(result.user)
      setAuthState('authenticated')
      return result
    }

    // 2FA requerido
    setPartialToken(result.partial_token)
    setAuthState(result.auth_state)
    if (result.qr_code) setQrCode(result.qr_code)
    return result
  }, [])

  const complete2FASetup = useCallback(async (codigo) => {
    const { data } = await setup2FA(codigo, partialToken)
    const result = data.data
    localStorage.setItem('access_token', result.access_token)
    localStorage.setItem('refresh_token', result.refresh_token)
    setUser(result.user)
    setAuthState('authenticated')
    setPartialToken(null)
    setQrCode(null)
    return result
  }, [partialToken])

  const complete2FAVerify = useCallback(async (codigo) => {
    const { data } = await verify2FA(codigo, partialToken)
    const result = data.data
    localStorage.setItem('access_token', result.access_token)
    localStorage.setItem('refresh_token', result.refresh_token)
    setUser(result.user)
    setAuthState('authenticated')
    setPartialToken(null)
    return result
  }, [partialToken])

  const logoutUser = useCallback(async () => {
    try { await apiLogout() } catch {}
    localStorage.clear()
    setUser(null)
    setAuthState(null)
    setPartialToken(null)
    setQrCode(null)
  }, [])

  const isPropietario = user?.rol === 'propietario' && user?.id_empresa === 0
  const isAdmin       = user?.rol === 'propietario' || user?.rol === 'administrador'
  const isComercial   = user?.rol === 'comercial'

  return (
    <AuthContext.Provider value={{
      user, loading, authState, qrCode, partialToken,
      login, complete2FASetup, complete2FAVerify, logout: logoutUser,
      isPropietario, isAdmin, isComercial,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de AuthProvider')
  return ctx
}
