import { useEffect, useState } from 'react'
import { CreditCard, Lock, Unlock, RefreshCw } from 'lucide-react'
import { getFacturacionEmpresas, getPlanes, asignarPlan, bloquearEmpresa, desbloquearEmpresa } from '../../api/facturacionApi'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function AdminFacturacionPage() {
  const { isPropietario } = useAuth()
  const [empresas, setEmpresas] = useState([])
  const [planes, setPlanes] = useState([])
  const [loading, setLoading] = useState(true)
  const [asignando, setAsignando] = useState(null) // empresa_id

  const fetch = async () => {
    setLoading(true)
    try {
      const [e, p] = await Promise.all([getFacturacionEmpresas(), getPlanes()])
      setEmpresas(e.data.data)
      setPlanes(p.data.data)
    } catch { toast.error('Error al cargar datos') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])

  const handleAsignarPlan = async (empresaId, planId) => {
    try {
      await asignarPlan(empresaId, { plan_id: planId })
      toast.success('Plan asignado')
      setAsignando(null)
      fetch()
    } catch (err) { toast.error(err.response?.data?.message || 'Error') }
  }

  const handleBloquear = async (empresaId) => {
    if (!confirm('¿Bloquear consultas de esta empresa?')) return
    try {
      await bloquearEmpresa(empresaId, { motivo: 'BLOQUEADO_DEUDA' })
      toast.success('Empresa bloqueada')
      fetch()
    } catch { toast.error('Error') }
  }

  const handleDesbloquear = async (empresaId) => {
    try {
      await desbloquearEmpresa(empresaId)
      toast.success('Empresa desbloqueada')
      fetch()
    } catch { toast.error('Error') }
  }

  if (!isPropietario) return <p className="text-gray-400 text-center py-12">Acceso no autorizado</p>

  if (loading) return <div className="flex justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" /></div>

  // Stats
  const totalEmpresas = empresas.length
  const conDeuda = empresas.filter(e => e.saldo_pendiente > 0).length
  const bloqueadas = empresas.filter(e => !e.consultas_habilitadas).length
  const facturacionMes = empresas.reduce((s, e) => s + e.monto_total, 0)
  const cobrado = empresas.reduce((s, e) => s + e.monto_pagado, 0)
  const pendiente = empresas.reduce((s, e) => s + e.saldo_pendiente, 0)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Facturación — Administración</h1>
        <p className="text-gray-500 text-sm">Gestión de planes, consumo y pagos de todas las empresas</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <div className="card text-center p-4"><p className="text-xs text-gray-500">Empresas</p><p className="text-2xl font-bold">{totalEmpresas}</p></div>
        <div className="card text-center p-4"><p className="text-xs text-gray-500">Con deuda</p><p className="text-2xl font-bold text-yellow-600">{conDeuda}</p></div>
        <div className="card text-center p-4"><p className="text-xs text-gray-500">Bloqueadas</p><p className="text-2xl font-bold text-red-600">{bloqueadas}</p></div>
        <div className="card text-center p-4"><p className="text-xs text-gray-500">Facturado mes</p><p className="text-lg font-bold">Gs. {facturacionMes.toLocaleString('es-PY')}</p></div>
        <div className="card text-center p-4"><p className="text-xs text-gray-500">Cobrado</p><p className="text-lg font-bold text-green-600">Gs. {cobrado.toLocaleString('es-PY')}</p></div>
        <div className="card text-center p-4"><p className="text-xs text-gray-500">Pendiente</p><p className="text-lg font-bold text-red-600">Gs. {pendiente.toLocaleString('es-PY')}</p></div>
      </div>

      {/* Tabla de empresas */}
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-500 uppercase border-b">
              <th className="pb-2 pr-3">Empresa</th>
              <th className="pb-2 pr-3">Plan</th>
              <th className="pb-2 pr-3">Incluidos</th>
              <th className="pb-2 pr-3">Consumidos</th>
              <th className="pb-2 pr-3">Sobre fact.</th>
              <th className="pb-2 pr-3">Total</th>
              <th className="pb-2 pr-3">Pagado</th>
              <th className="pb-2 pr-3">Saldo</th>
              <th className="pb-2 pr-3">Estado</th>
              <th className="pb-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empresas.map(e => (
              <tr key={e.empresa_id} className="border-b border-gray-100">
                <td className="py-3 pr-3 font-medium text-gray-900">{e.empresa_nombre}</td>
                <td className="py-3 pr-3">
                  {asignando === e.empresa_id ? (
                    <select className="input text-xs py-1" autoFocus
                      onChange={ev => { if (ev.target.value) handleAsignarPlan(e.empresa_id, parseInt(ev.target.value)) }}
                      onBlur={() => setAsignando(null)}>
                      <option value="">Seleccionar...</option>
                      {planes.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                    </select>
                  ) : (
                    <span className="cursor-pointer hover:text-primary-600" onClick={() => setAsignando(e.empresa_id)}>
                      {e.plan_nombre} <RefreshCw className="h-3 w-3 inline text-gray-400" />
                    </span>
                  )}
                </td>
                <td className="py-3 pr-3">{e.reportes_incluidos}</td>
                <td className="py-3 pr-3 font-bold">{e.reportes_consumidos}</td>
                <td className="py-3 pr-3 text-orange-600">{e.sobre_facturados}</td>
                <td className="py-3 pr-3">Gs. {e.monto_total.toLocaleString('es-PY')}</td>
                <td className="py-3 pr-3 text-green-600">Gs. {e.monto_pagado.toLocaleString('es-PY')}</td>
                <td className="py-3 pr-3 font-bold text-red-600">Gs. {e.saldo_pendiente.toLocaleString('es-PY')}</td>
                <td className="py-3 pr-3">
                  <span className={`text-xs font-medium ${e.estado_pago === 'PAGADO' ? 'text-green-600' : e.estado_pago === 'PENDIENTE' ? 'text-yellow-600' : 'text-gray-400'}`}>
                    {e.estado_pago}
                  </span>
                </td>
                <td className="py-3">
                  {e.consultas_habilitadas ? (
                    <button onClick={() => handleBloquear(e.empresa_id)} className="btn btn-sm bg-red-50 text-red-600 border border-red-200 hover:bg-red-100" title="Bloquear">
                      <Lock className="h-3.5 w-3.5" />
                    </button>
                  ) : (
                    <button onClick={() => handleDesbloquear(e.empresa_id)} className="btn btn-sm bg-green-50 text-green-600 border border-green-200 hover:bg-green-100" title="Desbloquear">
                      <Unlock className="h-3.5 w-3.5" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {empresas.length === 0 && <tr><td colSpan={10} className="py-8 text-center text-gray-400">Sin empresas</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
