import api from './axiosConfig'

// Criterios
export const getCriteria      = ()           => api.get('/evaluations/criteria')
export const createCriterion  = (data)       => api.post('/evaluations/criteria', data)
export const updateCriterion  = (id, data)   => api.put(`/evaluations/criteria/${id}`, data)

// Evaluaciones
export const getEvaluations   = (params)     => api.get('/evaluations/', { params })
export const getEvaluation    = (id)         => api.get(`/evaluations/${id}`)
export const createEvaluation = (data)       => api.post('/evaluations/', data)
export const updateEvaluation = (id, data)   => api.put(`/evaluations/${id}`, data)
