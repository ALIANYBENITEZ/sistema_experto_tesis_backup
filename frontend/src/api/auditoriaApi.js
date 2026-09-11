import api from './axiosConfig'

export const getAuditoria = (params) =>
  api.get('/auditoria/', { params }).then((r) => r.data.data)

export const getAuditoriaFiltros = () =>
  api.get('/auditoria/filtros').then((r) => r.data.data)
