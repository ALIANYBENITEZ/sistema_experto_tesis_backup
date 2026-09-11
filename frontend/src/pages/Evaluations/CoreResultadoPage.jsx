import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, CheckCircle, XCircle, AlertTriangle, MinusCircle } from 'lucide-react'
import { coreGetEvaluacion, coreGetPdf } from '../../api/coreApi'
import toast from 'react-hot-toast'

const NIVEL_CONFIG = {
  bajo:  { label: 'BAJO',  color: 'text-green-600', bg: 'bg-green-50 border-green-200', bar: '#16a34a' },
  medio: { label: 'MEDIO', color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200', bar: '#ca8a04' },
  alto:  { label: 'ALTO',  color: 'text-red-600', bg: 'bg-red-50 border-red-200', bar: '#dc2626' },
}

export default function CoreResultadoPage() {
  const { evalId } = useParams()
  const navigate = useNavigate()
  const [ev, setEv] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    coreGetEvaluacion(evalId)
      .then(r => setEv(r.data.data))
      .catch(() => { toast.error('Evaluación no encontrada'); navigate('/evaluations') })
      .finally(() => setLoading(false))
  }, [evalId])

  const handlePdf = async () => {
    try {
      toast.loading('Generando PDF…', { id: 'pdf' })
      const r = await coreGetPdf(evalId)
      const url = URL.createObjectURL(new Blob([r.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `evaluacion_riesgo_${evalId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('PDF descargado', { id: 'pdf' })
    } catch {
      toast.error('Error al generar PDF', { id: 'pdf' })
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
    </div>
  )
  if (!ev) return null

  const cfg = NIVEL_CONFIG[ev.clasificacion] || NIVEL_CONFIG.alto

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/evaluations')} className="btn-secondary btn-sm">
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Resultado de Evaluación #{ev.id}</h1>
            <p className="text-sm text-gray-500">{ev.fecha ? new Date(ev.fecha).toLocaleString('es-PY') : ''} · Modelo v{ev.modelo_version}</p>
          </div>
        </div>
        <button onClick={handlePdf} className="btn-primary">
          <Download className="h-4 w-4" /> Descargar PDF
        </button>
      </div>

      {/* Cliente */}
      {ev.cliente_nombre && (
        <div className="card flex items-center gap-4">
          <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-lg">
            {ev.cliente_nombre?.[0]}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{ev.cliente_nombre}</p>
            <p className="text-sm text-gray-500">{ev.cliente_num_doc} · {ev.tipo_persona === 'PF' ? 'Persona Física' : 'Persona Jurídica'}</p>
          </div>
        </div>
      )}

      {/* Score principal */}
      <div className={`card border-2 ${cfg.bg}`}>

        {/* Alerta lista negra */}
        {ev.lista_negra && ev.lista_negra.en_lista && (
          <div className="mb-4 bg-red-100 border border-red-400 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">🚨</span>
              <p className="font-bold text-red-800">ALERTA: Cliente encontrado en listas de sanciones internacionales</p>
            </div>
            {ev.lista_negra.coincidencias?.map((c, i) => (
              <p key={i} className="text-sm text-red-700 pl-6">
                • {c.nombre} {c.apellido} {c.cargo ? `(${c.cargo})` : ''} — Match: {c.tipo_match}
              </p>
            ))}
          </div>
        )}
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs text-gray-500">Clasificación de Riesgo</p>
            <p className={`text-3xl font-bold ${cfg.color}`}>RIESGO {cfg.label}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">Score Total</p>
            <p className="text-3xl font-bold text-gray-900">{ev.score_total.toFixed(1)}</p>
            <p className="text-xs text-gray-400">{ev.factores_evaluados} factores evaluados</p>
          </div>
        </div>
        {ev.estado === 'incompleta' && (
          <div className="flex items-center gap-2 bg-yellow-100 border border-yellow-300 rounded-lg p-3 text-sm text-yellow-800">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            <span>Evaluación incompleta: {ev.factores_sin_dato} factor(es) obligatorio(s) sin información.</span>
          </div>
        )}
      </div>

      {/* Explicación global */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-3">Análisis del Sistema</h2>
        <p className="text-sm text-gray-700 leading-relaxed">{ev.explicacion}</p>
      </div>

      {/* Factores de impacto */}
      {ev.impacto && (
        <div className="grid md:grid-cols-2 gap-4">
          {ev.impacto.desfavorables?.length > 0 && (
            <div className="card border-red-200 bg-red-50">
              <h3 className="text-sm font-semibold text-red-700 mb-2">⚠️ Factores Desfavorables</h3>
              {ev.impacto.desfavorables.map((d, i) => (
                <div key={i} className="flex justify-between text-sm py-1 border-b border-red-100 last:border-0">
                  <span className="text-gray-800">{d.factor_nombre}</span>
                  <span className="font-mono text-red-600 font-bold">+{d.peso.toFixed(1)}</span>
                </div>
              ))}
            </div>
          )}
          {ev.impacto.favorables?.length > 0 && (
            <div className="card border-green-200 bg-green-50">
              <h3 className="text-sm font-semibold text-green-700 mb-2">✅ Factores Favorables</h3>
              {ev.impacto.favorables.map((d, i) => (
                <div key={i} className="flex justify-between text-sm py-1 border-b border-green-100 last:border-0">
                  <span className="text-gray-800">{d.factor_nombre}</span>
                  <span className="font-mono text-green-600 font-bold">{d.peso.toFixed(1)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Detalle por factor */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-4">Detalle por Factor</h2>
        <div className="space-y-2">
          {ev.detalles?.map((d, i) => (
            <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border ${
              d.estado !== 'evaluado' ? 'bg-gray-50 border-gray-200' :
              d.nivel === 'bajo' ? 'bg-green-50 border-green-200' :
              d.nivel === 'medio' ? 'bg-yellow-50 border-yellow-200' :
              'bg-red-50 border-red-200'
            }`}>
              <div className="flex-shrink-0 mt-0.5">
                {d.estado !== 'evaluado' ? <MinusCircle className="h-5 w-5 text-gray-400" /> :
                 d.nivel === 'bajo' ? <CheckCircle className="h-5 w-5 text-green-600" /> :
                 d.nivel === 'medio' ? <AlertTriangle className="h-5 w-5 text-yellow-600" /> :
                 <XCircle className="h-5 w-5 text-red-600" />}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-gray-800">{d.factor_nombre}</p>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    d.categoria === 'principal' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}>{d.categoria}</span>
                </div>
                {d.valor_original && (
                  <p className="text-xs text-gray-500 mt-0.5">Valor: <span className="font-mono font-semibold">{d.valor_original}</span></p>
                )}
                {d.explicacion && <p className="text-xs text-gray-600 mt-1">{d.explicacion}</p>}
              </div>
              <div className="flex-shrink-0 text-right">
                {d.estado === 'evaluado' && (
                  <>
                    <p className={`text-sm font-bold ${d.peso >= 0 ? (d.peso > 0 ? 'text-red-600' : 'text-gray-400') : 'text-green-600'}`}>
                      {d.peso > 0 ? '+' : ''}{d.peso.toFixed(1)}
                    </p>
                    <p className="text-xs text-gray-400 capitalize">{d.nivel}</p>
                  </>
                )}
                {d.estado !== 'evaluado' && (
                  <span className="text-xs text-gray-400 capitalize">{d.estado.replace('_', ' ')}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Acciones */}
      <div className="flex gap-3">
        <button onClick={() => navigate('/evaluations')} className="btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Volver al historial
        </button>
        <button onClick={() => navigate('/evaluations/new')} className="btn-primary">
          Nueva evaluación
        </button>
        <button onClick={handlePdf} className="btn-secondary">
          <Download className="h-4 w-4" /> Descargar PDF
        </button>
      </div>
    </div>
  )
}
