import api from './axiosConfig'

// Parámetros disponibles
export const getParametros       = ()                => api.get('/scoring/parametros')

// Motores
export const getMotores          = ()                => api.get('/scoring/motores')
export const getMotor            = (id)              => api.get(`/scoring/motores/${id}`)
export const createMotor         = (data)            => api.post('/scoring/motores', data)
export const updateMotor         = (id, data)        => api.put(`/scoring/motores/${id}`, data)
export const toggleMotor         = (id)              => api.patch(`/scoring/motores/${id}/toggle`)

// Reglas
export const getReglas           = (motorId)         => api.get(`/scoring/motores/${motorId}/reglas`)
export const createRegla         = (motorId, data)   => api.post(`/scoring/motores/${motorId}/reglas`, data)
export const updateRegla         = (id, data)        => api.put(`/scoring/reglas/${id}`, data)
export const toggleRegla         = (id)              => api.patch(`/scoring/reglas/${id}/toggle`)
export const deleteRegla         = (id)              => api.delete(`/scoring/reglas/${id}`)

// Historial crediticio
export const getHistorial        = (clienteId)       => api.get(`/scoring/historial/${clienteId}`)
export const upsertHistorial     = (clienteId, data) => api.put(`/scoring/historial/${clienteId}`, data)

// Evaluación
export const evaluar             = (data)            => api.post('/scoring/evaluar', data)
export const getEvaluacionesRiesgo = (params)        => api.get('/scoring/evaluaciones', { params })
export const getEvaluacionRiesgo = (id)              => api.get(`/scoring/evaluaciones/${id}`)
