import api from './axiosConfig'

export const getClients  = (params)     => api.get('/clients/', { params })
export const getClient   = (id)         => api.get(`/clients/${id}`)
export const createClient = (data)      => api.post('/clients/', data)
export const updateClient = (id, data)  => api.put(`/clients/${id}`, data)
export const deleteClient = (id)        => api.delete(`/clients/${id}`)

// Ubicación
export const getPaises         = ()         => api.get('/clients/paises')
export const getDepartamentos  = ()         => api.get('/clients/departamentos')
export const getCiudades       = (deptoId)  => api.get(`/clients/departamentos/${deptoId}/ciudades`)
