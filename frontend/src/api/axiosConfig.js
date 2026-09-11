import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Adjuntar el access token a cada request
api.interceptors.request.use((config) => {
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

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
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
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
