import api from './axiosConfig'

// Evaluación
export const coreEvaluar         = (data)      => api.post('/core/evaluar', data)
export const coreGetEvaluaciones = (params)    => api.get('/core/evaluaciones', { params })
export const coreGetEvaluacion   = (id)        => api.get(`/core/evaluaciones/${id}`)
export const coreGetPdf          = (id)        => api.get(`/core/evaluaciones/${id}/pdf`, { responseType: 'blob' })

// Lista negra
export const coreVerificarListaNegra = (clienteId) => api.get(`/core/verificar-lista-negra/${clienteId}`)

// Modelos
export const coreGetModelos      = ()          => api.get('/core/modelos')
export const coreGetModelo       = (id)        => api.get(`/core/modelos/${id}`)
export const coreCreateModelo    = (data)      => api.post('/core/modelos', data)
export const coreClonarModelo    = (data)      => api.post('/core/modelos/clonar', data)
export const coreDeleteModelo    = (id)        => api.delete(`/core/modelos/${id}`)
export const coreCreateFactor    = (modeloId, data) => api.post(`/core/modelos/${modeloId}/factores`, data)
export const coreCreateRegla     = (factorId, data) => api.post(`/core/factores/${factorId}/reglas`, data)
export const coreCreateUmbral    = (modeloId, data) => api.post(`/core/modelos/${modeloId}/umbrales`, data)
