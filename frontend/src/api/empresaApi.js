import api from './axiosConfig'

export const getEmpresas       = ()              => api.get('/empresas/')
export const getEmpresa        = (id)            => api.get(`/empresas/${id}`)
export const createEmpresa     = (data)          => api.post('/empresas/', data)
export const updateEmpresa     = (id, data)      => api.put(`/empresas/${id}`, data)
export const toggleEmpresa     = (id)            => api.patch(`/empresas/${id}/toggle`)

// Usuarios de empresa
export const getUsuariosEmpresa  = (empresaId)         => api.get(`/empresas/${empresaId}/usuarios`)
export const createUsuarioEmpresa = (empresaId, data)  => api.post(`/empresas/${empresaId}/usuarios`, data)
export const updateUsuarioEmpresa = (userId, data)     => api.put(`/empresas/usuarios/${userId}`, data)
export const toggleUsuario        = (userId)           => api.patch(`/empresas/usuarios/${userId}/toggle`)
