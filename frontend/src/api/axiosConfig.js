import axios from 'axios'
import { sesionExpirada as sesionVencida } from '../utils/session'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Adjuntar el access token a cada request. Si la sesión ya venció por tiempo,
// se corta el request y se redirige al login (evita usar un token caduco).
api.interceptors.request.use((config) => {
  const esAuth = config.url?.includes('/auth/login') || config.url?.includes('/auth/2fa')
  if (!esAuth && sesionVencida()) {
    localStorage.clear()
    if (window.location.pathname !== '/login') window.location.href = '/login'
    return Promise.reject(new axios.Cancel('Sesión expirada'))
  }
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Si el token expiró (401) intentar refresh automático
// Excluir el endpoint de login para que sus errores lleguen al catch del componente
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config

    // Si el error viene del login o 2FA, no intentar refresh
    if (original.url?.includes('/auth/login') || original.url?.includes('/auth/2fa')) {
      return Promise.reject(error)
    }

    // Sesión cerrada por inicio en otro dispositivo: no reintentar, cerrar ya.
    if (error.response?.status === 401 && error.response?.data?.code === 'SESION_DUPLICADA') {
      localStorage.clear()
      localStorage.setItem('session_kickout', '1')
      if (window.location.pathname !== '/login') window.location.href = '/login'
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        // Si la sesión ya venció por tiempo, no intentar refrescar: cerrar.
        if (sesionVencida()) throw new Error('sesión expirada')
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('no refresh token')
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL || '/api'}/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${refresh}` } }
        )
        localStorage.setItem('access_token', data.data.access_token)
        original.headers.Authorization = `Bearer ${data.data.access_token}`
        return api(original)
      } catch {
        localStorage.clear()
        if (window.location.pathname !== '/login') window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
