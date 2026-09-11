import api from './axiosConfig'

export const login = (email, password) =>
  api.post('/auth/login', { email, password })

export const setup2FA = (codigo, token) =>
  api.post('/auth/2fa/setup', { codigo }, { headers: { Authorization: `Bearer ${token}` } })

export const verify2FA = (codigo, token) =>
  api.post('/auth/2fa/verify', { codigo }, { headers: { Authorization: `Bearer ${token}` } })

export const reset2FA = (userId) =>
  api.post(`/auth/2fa/reset/${userId}`)

export const changePassword = (data) =>
  api.post('/auth/change-password', data)

export const forgotPassword = (data) =>
  api.post('/auth/forgot-password', data)

export const getSecurityUsers = () =>
  api.get('/auth/security/users')

export const logout = () =>
  api.post('/auth/logout')

export const getMe = () =>
  api.get('/auth/me')

export const refreshToken = (token) =>
  api.post('/auth/refresh', {}, {
    headers: { Authorization: `Bearer ${token}` },
  })
