import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, User } from 'lucide-react'
import { getEvaluation } from '../../api/evaluationApi'
import ResultadoBadge from '../../components/ResultadoBadge'
import { fmtFechaHora } from '../../utils/fecha'
import toast from 'react-hot-toast'

export default function EvaluationDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [ev, setEv]           = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getEvaluation(id)
      .then(r => setEv(r.data.data))
      .catch(() => toast.error('No se encontró la evaluación'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
    </div>
  )
  if (!ev) return null

  const puntaje = parseFloat(ev.puntaje_total ?? 0)
  const pct     = Math.min(100, puntaje)
  const color   = puntaje >= 70 ? '#16a34a' : puntaje >= 50 ? '#ca8a04' : '#dc2626'

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/evaluations')} className="btn-secondary btn-sm">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Evaluación #{ev.id}</h1>
          <p className="text-sm text-gray-500">{fmtFechaHora(ev.fecha)}</p>
        </div>
      </div>

      {/* Cliente */}
      {ev.cliente && (
        <div className="card flex items-center gap-4">
          <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center">
            <User className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">{ev.cliente.nombre} {ev.cliente.apellido}</p>
            <p className="text-sm text-gray-500">{ev.cliente.num_doc}</p>
          </div>
        </div>
      )}

      {/* Resultado */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-800">Resultado</h2>
          <ResultadoBadge resultado={ev.resultado} />
        </div>
        {/* Barra de puntaje */}
        <div className="flex items-center gap-4">
          <div className="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="h-full rounded-full transition-all"
              style={{ width: `${pct}%`, backgroundColor: color }}
            />
          </div>
          <span className="text-2xl font-bold" style={{ color }}>{puntaje.toFixed(1)}</span>
          <span className="text-sm text-gray-400">/ 100</span>
        </div>
        {ev.observaciones && (
          <p className="mt-4 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{ev.observaciones}</p>
        )}
      </div>

      {/* Detalle por criterio */}
      {ev.detalles && ev.detalles.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Desglose por Criterio</h2>
          <div className="space-y-3">
            {ev.detalles.map((d) => (
              <div key={d.criterio_id} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-gray-700">{d.criterio_nombre}</span>
                    <span className="font-bold text-gray-900">{parseFloat(d.valor).toFixed(1)}</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="h-full rounded-full bg-primary-500"
                      style={{ width: `${d.valor}%` }}
                    />
                  </div>
                  {d.comentario && <p className="text-xs text-gray-400 mt-0.5">{d.comentario}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
