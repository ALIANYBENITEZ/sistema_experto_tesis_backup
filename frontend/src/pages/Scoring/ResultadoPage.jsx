import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, CheckCircle, XCircle, AlertTriangle, FileText } from 'lucide-react'
import { getEvaluacionRiesgo } from '../../api/scoringApi'
import toast from 'react-hot-toast'

const CATEGORIA_CONFIG = {
  bajo:      { label: 'Riesgo Bajo',     color: 'text-green-600',  bg: 'bg-green-50  border-green-200', bar: '#16a34a' },
  medio:     { label: 'Riesgo Medio',    color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200', bar: '#ca8a04' },
  alto:      { label: 'Riesgo Alto',     color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200', bar: '#ea580c' },
  rechazado: { label: 'RECHAZADO',       color: 'text-red-600',    bg: 'bg-red-50    border-red-200',    bar: '#dc2626' },
}

const PARAM_LABELS = {
  ingresos_mensuales:    'Ingresos Mensuales',
  edad:                  'Edad',
  nivel_endeudamiento:   'Nivel Endeudamiento %',
  meses_empleo_actual:   'Antigüedad Laboral',
  cantidad_atrasos:      'Atrasos',
  deuda_total_sistema:   'Deuda Total Sistema',
  score_externo:         'Score Crediticio',
  historial_pagos:       'Historial Pagos',
  en_lista_negra:        'En Lista Negra',
  tipo_empleo:           'Tipo Empleo',
  referencias_personales:'Referencias',
}

export default function ResultadoPage() {
  const { evalId } = useParams()
  const navigate   = useNavigate()
  const [ev, setEv]           = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getEvaluacionRiesgo(evalId)
      .then(r => setEv(r.data.data))
      .catch(() => { toast.error('Evaluación no encontrada'); navigate('/evaluations') })
      .finally(() => setLoading(false))
  }, [evalId, navigate])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
    </div>
  )
  if (!ev) return null

  const cfg        = CATEGORIA_CONFIG[ev.categoria_riesgo] ?? CATEGORIA_CONFIG.alto
  const porcentaje = ev.score_maximo > 0
    ? Math.round((ev.score_final / ev.score_maximo) * 100)
    : 0

  const determinante = ev.detalles?.find(d => d.es_determinante && !d.cumplido)
  const reglasCumplidas  = ev.detalles?.filter(d => d.cumplido).length ?? 0
  const reglasTotal      = ev.detalles?.length ?? 0

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/evaluations')} className="btn-secondary btn-sm">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Resultado de Evaluación #{ev.id}</h1>
          <p className="text-sm text-gray-500">
            {new Date(ev.fecha_analisis).toLocaleString('es-PY')}
          </p>
        </div>
      </div>

      {/* Cliente */}
      {ev.cliente && (
        <div className="card flex items-center gap-4">
          <div className="h-12 w-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-lg">
            {ev.cliente.nombre?.[0]}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{ev.cliente.nombre} {ev.cliente.apellido}</p>
            <p className="text-sm text-gray-500">{ev.cliente.num_doc} · Motor: {ev.motor_nombre}</p>
          </div>
        </div>
      )}

      {/* Detalle de la Operación Inmobiliaria */}
      {ev.operacion && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-3">Operación Inmobiliaria</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
            <div>
              <p className="text-gray-500 text-xs">Tipo de propiedad</p>
              <p className="font-medium text-gray-900 capitalize">{ev.operacion.tipo_propiedad?.replace('_', ' ')}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Valor de la propiedad</p>
              <p className="font-medium text-gray-900">Gs. {ev.operacion.valor_propiedad?.toLocaleString('es-PY')}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Monto solicitado</p>
              <p className="font-medium text-gray-900">Gs. {ev.operacion.monto_solicitado?.toLocaleString('es-PY')}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Plazo</p>
              <p className="font-medium text-gray-900">{ev.operacion.plazo_meses} meses</p>
            </div>
            {ev.operacion.ubicacion && (
              <div>
                <p className="text-gray-500 text-xs">Ubicación</p>
                <p className="font-medium text-gray-900">{ev.operacion.ubicacion}</p>
              </div>
            )}
            {ev.operacion.destino && (
              <div>
                <p className="text-gray-500 text-xs">Destino</p>
                <p className="font-medium text-gray-900 capitalize">{ev.operacion.destino}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Resultado principal */}
      <div className={`card border-2 ${cfg.bg}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-800">Resultado del Scoring</h2>
          <span className={`text-lg font-bold ${cfg.color}`}>{cfg.label}</span>
        </div>

        {ev.categoria_riesgo === 'rechazado' && determinante && (
          <div className="flex items-start gap-2 bg-red-100 border border-red-300 rounded-lg p-3 mb-4 text-sm text-red-800">
            <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold">Rechazo automático</p>
              <p>La regla determinante <strong>"{determinante.regla_nombre}"</strong> no fue cumplida.</p>
            </div>
          </div>
        )}

        {/* Barra de puntaje */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Puntaje obtenido</span>
            <span className="font-bold text-gray-900">
              {ev.score_final.toFixed(1)} / {ev.score_maximo.toFixed(1)} pts ({porcentaje}%)
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div className="h-full rounded-full transition-all"
              style={{ width: `${Math.min(100, porcentaje)}%`, backgroundColor: cfg.bar }} />
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>{reglasCumplidas} de {reglasTotal} reglas cumplidas</span>
            <span className="flex gap-4">
              <span className="text-green-600">≥75% Riesgo Bajo</span>
              <span className="text-yellow-600">≥50% Riesgo Medio</span>
              <span className="text-red-600">&lt;50% Riesgo Alto</span>
            </span>
          </div>
        </div>

        {ev.observaciones && (
          <p className="mt-4 text-sm text-gray-600 bg-white rounded-lg p-3 border border-gray-200">
            {ev.observaciones}
          </p>
        )}
      </div>

      {/* Recomendación automatizada */}
      {ev.recomendacion && (
        <div className="card border-l-4 border-l-primary-600">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="h-5 w-5 text-primary-600" />
            <h2 className="font-semibold text-gray-800">Recomendación del Sistema</h2>
            <span className={`ml-auto text-xs font-bold px-2 py-1 rounded ${
              ev.recomendacion.decision === 'FAVORABLE' ? 'bg-green-100 text-green-700' :
              ev.recomendacion.decision === 'CON OBSERVACIONES' ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              {ev.recomendacion.decision}
            </span>
          </div>
          <p className="text-sm text-gray-700 mb-3">{ev.recomendacion.descripcion}</p>
          {ev.recomendacion.detalle_adicional && (
            <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 border border-gray-200 mb-3">
              {ev.recomendacion.detalle_adicional}
            </p>
          )}
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Acciones sugeridas:</p>
            <ul className="space-y-1.5">
              {ev.recomendacion.acciones.map((a, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-primary-500 mt-0.5">•</span>
                  {a}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Desglose por regla */}
      {ev.detalles && ev.detalles.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Desglose por Regla</h2>
          <div className="space-y-2">
            {ev.detalles.map((d, i) => (
              <div key={i}
                className={`flex items-start gap-3 p-3 rounded-lg border
                  ${d.cumplido
                    ? 'bg-green-50 border-green-200'
                    : d.es_determinante
                      ? 'bg-red-50 border-red-300'
                      : 'bg-gray-50 border-gray-200'}`}>
                <div className="flex-shrink-0 mt-0.5">
                  {d.cumplido
                    ? <CheckCircle className="h-5 w-5 text-green-600" />
                    : <XCircle className={`h-5 w-5 ${d.es_determinante ? 'text-red-600' : 'text-gray-400'}`} />
                  }
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-medium text-gray-800">{d.regla_nombre}</p>
                    {d.es_determinante && (
                      <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                        Determinante
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                    <span className="font-mono bg-white px-1.5 py-0.5 rounded border">
                      {PARAM_LABELS[d.parametro] || d.parametro}
                    </span>
                    <span className="font-mono font-bold text-primary-600">{d.operador}</span>
                    <span className="font-mono bg-white px-1.5 py-0.5 rounded border">{d.valor_referencia}</span>
                    <span className="text-gray-400 mx-1">→ valor:</span>
                    <span className="font-mono bg-white px-1.5 py-0.5 rounded border font-semibold">
                      {d.valor_evaluado}
                    </span>
                  </div>
                </div>
                <div className="flex-shrink-0 text-right">
                  <p className={`text-sm font-bold ${d.cumplido ? 'text-green-600' : 'text-gray-400'}`}>
                    +{d.puntos_obtenidos.toFixed(1)} pts
                  </p>
                  <p className="text-xs text-gray-400">de {d.peso_puntos}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Acciones */}
      <div className="flex gap-3">
        <button onClick={() => navigate('/evaluations')} className="btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Volver
        </button>
        <button onClick={() => navigate(`/evaluations/new`)}
          className="btn-primary">
          <FileText className="h-4 w-4" /> Nueva evaluación
        </button>
      </div>
    </div>
  )
}

