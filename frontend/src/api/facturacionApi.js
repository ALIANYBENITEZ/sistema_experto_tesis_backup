import api from './axiosConfig'

// Planes
export const getPlanes              = ()              => api.get('/facturacion/planes')
export const createPlan             = (data)          => api.post('/facturacion/planes', data)
export const updatePlan             = (id, data)      => api.put(`/facturacion/planes/${id}`, data)

// Mi facturación (admin empresa)
export const getMiPlan              = ()              => api.get('/facturacion/mi-plan')
export const getMiHistorial         = ()              => api.get('/facturacion/mi-historial')

// Pagos
export const crearPago              = (data)          => api.post('/facturacion/pagos', data)
export const getPagos               = ()              => api.get('/facturacion/pagos')
export const testAprobarPago        = (id)            => api.post(`/facturacion/pagos/${id}/test-aprobar`)
export const testRechazarPago       = (id)            => api.post(`/facturacion/pagos/${id}/test-rechazar`)

// Pagopar (pasarela real)
export const getPagoparEstado       = ()              => api.get('/facturacion/pagopar/estado')
export const iniciarPagoPagopar     = (data)          => api.post('/facturacion/pagos/pagopar/iniciar', data)

// Admin (propietario)
export const getFacturacionEmpresas = ()              => api.get('/facturacion/admin/empresas')
export const asignarPlan            = (empresaId, data) => api.post(`/facturacion/admin/empresas/${empresaId}/asignar-plan`, data)
export const bloquearEmpresa        = (empresaId, data) => api.post(`/facturacion/admin/empresas/${empresaId}/bloquear`, data)
export const desbloquearEmpresa     = (empresaId)     => api.post(`/facturacion/admin/empresas/${empresaId}/desbloquear`)
