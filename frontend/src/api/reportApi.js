import api from './axiosConfig'

export const getSummary      = ()       => api.get('/reports/summary')
export const getReportList   = (params) => api.get('/reports/evaluations', { params })
export const exportPdf       = (params) =>
  api.get('/reports/evaluations/pdf', {
    params,
    responseType: 'blob',
  })
