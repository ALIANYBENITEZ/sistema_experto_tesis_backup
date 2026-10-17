import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { login as apiLogin, logout as apiLogout, getMe, setup2FA, verify2FA } from '../api/authApi'
import { guardarExpiracion, sesionExpirada } from '../utils/session'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)
  // 2FA states
  const [authState, setAuthState] = useState(null) // null, '2fa_setup_required', '2fa_required', 'authenticated'
  const [partialToken, setPartialToken] = useState(null)
  const [qrCode, setQrCode] = useState(null)
  const timerRef = useRef(null)

  // Limpia toda la sesión local (tokens + marca de expiración) y el estado.
  const limpiarSesion = useCallback(() => {
    if (timerRef.current) { clearTimeout(timerRef.current); timerRef.current = null }
    localStorage.clear()
    setUser(null)
    setAuthState(null)
    setPartialToken(null)
    setQrCode(null)
  }, [])

  // Programa el cierre automático de sesión al cumplirse el tiempo configurado.
  const programarExpiracion = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    const exp = Number(localStorage.getItem('session_expires_at') || 0)
    if (exp <= 0) return
    const restante = exp - Date.now()
    if (restante <= 0) {
      limpiarSesion()
      return
    }
    timerRef.current = setTimeout(() => { limpiarSesion() }, restante)
  }, [limpiarSesion])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token && !sesionExpirada()) {
      getMe()
        .then(({ data }) => {
          setUser(data.data)
          setAuthState('authenticated')
          programarExpiracion()
        })
        .catch(() => { limpiarSesion() })
        .finally(() => setLoading(false))
    } else {
      // Sin token o sesión ya expirada → asegurarse de dejar todo limpio.
      if (token) limpiarSesion()
      setLoading(false)
    }
  }, [programarExpiracion, limpiarSesion])

  // Revalida la sesión cuando la pestaña vuelve a estar visible o recupera el
  // foco (incluye el caso de volver con el botón "atrás" del navegador, que
  // restaura la página desde la caché sin recargar la app).
  useEffect(() => {
    const revalidar = () => {
      if (sesionExpirada() || !localStorage.getItem('access_token')) {
        limpiarSesion()
      }
    }
    // pageshow con event.persisted === true indica que la página se restauró
    // desde la caché del navegador (típico al pulsar "atrás"): revalidar y, si
    // la sesión ya no es válida, recargar para no mostrar contenido cacheado.
    const onPageShow = (event) => {
      if (event.persisted) {
        if (sesionExpirada() || !localStorage.getItem('access_token')) {
          limpiarSesion()
          window.location.replace('/login')
          return
        }
      }
      revalidar()
    }
    document.addEventListener('visibilitychange', revalidar)
    window.addEventListener('focus', revalidar)
    window.addEventListener('pageshow', onPageShow)
    return () => {
      document.removeEventListener('visibilitychange', revalidar)
      window.removeEventListener('focus', revalidar)
      window.removeEventListener('pageshow', onPageShow)
    }
  }, [limpiarSesion])

  const login = useCallback(async (email, password) => {
    // Limpiar tokens previos para evitar conflictos entre usuarios
    localStorage.clear()

    const { data } = await apiLogin(email, password)
    const result = data.data

    if (result.auth_state === 'authenticated') {
      // Acceso directo (sin 2FA o fallback)
      localStorage.setItem('access_token', result.access_token)
      localStorage.setItem('refresh_token', result.refresh_token)
      guardarExpiracion(result.session_timeout)
      setUser(result.user)
      setAuthState('authenticated')
      programarExpiracion()
      return result
    }

    // 2FA requerido
    setPartialToken(result.partial_token)
    setAuthState(result.auth_state)
    if (result.qr_code) setQrCode(result.qr_code)
    return result
  }, [programarExpiracion])

  const complete2FASetup = useCallback(async (codigo) => {
    const { data } = await setup2FA(codigo, partialToken)
    const result = data.data
    localStorage.setItem('access_token', result.access_token)
    localStorage.setItem('refresh_token', result.refresh_token)
    guardarExpiracion(result.session_timeout)
    setUser(result.user)
    setAuthState('authenticated')
    setPartialToken(null)
    setQrCode(null)
    programarExpiracion()
    return result
  }, [partialToken, programarExpiracion])

  const complete2FAVerify = useCallback(async (codigo) => {
    const { data } = await verify2FA(codigo, partialToken)
    const result = data.data
    localStorage.setItem('access_token', result.access_token)
    localStorage.setItem('refresh_token', result.refresh_token)
    guardarExpiracion(result.session_timeout)
    setUser(result.user)
    setAuthState('authenticated')
    setPartialToken(null)
    programarExpiracion()
    return result
  }, [partialToken, programarExpiracion])

  const logoutUser = useCallback(async () => {
    try { await apiLogout() } catch {}
    limpiarSesion()
  }, [limpiarSesion])

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
