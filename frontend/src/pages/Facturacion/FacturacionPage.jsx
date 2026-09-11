import { useEffect, useState } from 'react'
import { CreditCard, FileText, AlertTriangle, CheckCircle } from 'lucide-react'
import { getMiPlan, getMiHistorial, crearPago, testAprobarPago, testRechazarPago, getPagos } from '../../api/facturacionApi'
import { useAuth } from '../../context/AuthContext'
import AdminFacturacionPage from './AdminFacturacionPage'
import toast from 'react-hot-toast'

export default function FacturacionPage() {
  const { isPropietario } = useAuth()

  // Propietario ve la vista de administración
  if (isPropietario) return <AdminFacturacionPage />

  // Admin empresa ve su facturación
  return <EmpresaFacturacionView />
}

function EmpresaFacturacionView() {
  const [planData, setPlanData] = useState(null)
  const [historial, setHistorial] = useState([])
  const [pagos, setPagos] = useState([])
  const [loading, setLoading] = useState(true)

  const fetch = async () => {
    setLoading(true)
    try {
      const [p, h, pg] = await Promise.all([getMiPlan(), getMiHistorial(), getPagos()])
      setPlanData(p.data.data)
      setHistorial(h.data.data)
      setPagos(pg.data.data)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])

  const handlePagar = async () => {
    if (!planData?.periodo) { toast.error('No hay período activo'); return }
    try {
      const r = await crearPago({ periodo_facturacion_id: planData.periodo.id })
      const pago = r.data.data
      // Simular pantalla de pago TEST
      const decision = confirm('SIMULACIÓN DE PAGO\n\n¿Aprobar el pago?\n\nAceptar = Aprobar\nCancelar = Rechazar')
      if (decision) {
        await testAprobarPago(pago.id)
        toast.success('Pago aprobado exitosamente')
      } else {
        await testRechazarPago(pago.id)
        toast.error('Pago rechazado')
      }
      fetch()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al procesar pago')
    }
  }

  if (loading) return <div className="flex justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" /></div>

  const plan = planData?.plan
  const periodo = planData?.periodo

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Facturación</h1>
        <p className="text-gray-500 text-sm">Información de plan, consumo y pagos</p>
      </div>

      {!plan ? (
        <div className="card text-center py-12">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-3" />
          <p className="text-gray-600">Su empresa no tiene un plan asignado.</p>
          <p className="text-sm text-gray-400">Contacte al administrador del sistema.</p>
        </div>
      ) : (
        <>
          {/* Plan actual */}
          <div className="grid md:grid-cols-4 gap-4">
            <div className="card text-center"><p className="text-xs text-gray-500">Plan</p><p className="text-xl font-bold text-primary-600">{plan.plan_nombre}</p></div>
            <div className="card text-center"><p className="text-xs text-gray-500">Reportes incluidos</p><p className="text-xl font-bold">{plan.cantidad_reportes_incluidos}</p></div>
            <div className="card text-center"><p className="text-xs text-gray-500">Consumidos</p><p className="text-xl font-bold">{periodo?.reportes_consumidos || 0}</p></div>
            <div className="card text-center"><p className="text-xs text-gray-500">Restantes</p><p className="text-xl font-bold text-green-600">{planData?.reportes_restantes || plan.cantidad_reportes_incluidos}</p></div>
          </div>

          {/* Estado de cuenta */}
          {periodo && (
            <div className="card">
              <h2 className="font-semibold text-gray-800 mb-4">Estado de Cuenta — {periodo.mes}/{periodo.anio}</h2>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div><p className="text-gray-500">Monto del plan</p><p className="font-bold">Gs. {periodo.monto_plan?.toLocaleString('es-PY')}</p></div>
                <div><p className="text-gray-500">Sobre facturado ({periodo.reportes_sobre_facturados} reportes)</p><p className="font-bold text-orange-600">Gs. {periodo.monto_sobre_facturado?.toLocaleString('es-PY')}</p></div>
                <div><p className="text-gray-500">Total</p><p className="font-bold text-lg">Gs. {periodo.monto_total?.toLocaleString('es-PY')}</p></div>
                <div><p className="text-gray-500">Pagado</p><p className="font-bold text-green-600">Gs. {periodo.monto_pagado?.toLocaleString('es-PY')}</p></div>
                <div><p className="text-gray-500">Saldo pendiente</p><p className="font-bold text-red-600 text-lg">Gs. {periodo.saldo_pendiente?.toLocaleString('es-PY')}</p></div>
                <div><p className="text-gray-500">Estado</p><p className={`font-bold ${periodo.estado === 'PAGADO' ? 'text-green-600' : 'text-yellow-600'}`}>{periodo.estado}</p></div>
              </div>
              {periodo.saldo_pendiente > 0 && (
                <button onClick={handlePagar} className="btn-primary mt-4">
                  <CreditCard className="h-4 w-4" /> Realizar pago
                </button>
              )}
            </div>
          )}

          {/* Historial */}
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-4">Historial de Períodos</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="text-left text-xs text-gray-500 uppercase border-b">
                  <th className="pb-2">Período</th><th className="pb-2">Consumidos</th><th className="pb-2">Sobre fact.</th><th className="pb-2">Total</th><th className="pb-2">Pagado</th><th className="pb-2">Saldo</th><th className="pb-2">Estado</th>
                </tr></thead>
                <tbody>
                  {historial.map(p => (
                    <tr key={p.id} className="border-b border-gray-100">
                      <td className="py-2">{p.mes}/{p.anio}</td>
                      <td className="py-2">{p.reportes_consumidos}</td>
                      <td className="py-2">{p.reportes_sobre_facturados}</td>
                      <td className="py-2">Gs. {p.monto_total?.toLocaleString('es-PY')}</td>
                      <td className="py-2 text-green-600">Gs. {p.monto_pagado?.toLocaleString('es-PY')}</td>
                      <td className="py-2 text-red-600">Gs. {p.saldo_pendiente?.toLocaleString('es-PY')}</td>
                      <td className="py-2"><span className={`text-xs font-medium ${p.estado === 'PAGADO' ? 'text-green-600' : 'text-yellow-600'}`}>{p.estado}</span></td>
                    </tr>
                  ))}
                  {historial.length === 0 && <tr><td colSpan={7} className="py-6 text-center text-gray-400">Sin historial</td></tr>}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
