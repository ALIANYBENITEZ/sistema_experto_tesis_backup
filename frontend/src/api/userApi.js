import api from './axiosConfig'

export const getUsers      = ()           => api.get('/users/')
export const getUser       = (id)         => api.get(`/users/${id}`)
export const createUser    = (data)       => api.post('/users/', data)
export const updateUser    = (id, data)   => api.put(`/users/${id}`, data)
export const toggleUser    = (id)         => api.patch(`/users/${id}/toggle`)
