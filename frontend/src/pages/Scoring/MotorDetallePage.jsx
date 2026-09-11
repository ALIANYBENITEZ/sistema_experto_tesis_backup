import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Pencil, Trash2, Power, AlertTriangle } from 'lucide-react'
import { getMotor, createRegla, updateRegla, toggleRegla, deleteRegla } from '../../api/scoringApi'
import Modal from '../../components/Modal'
import ReglaForm from './ReglaForm'
import toast from 'react-hot-toast'

const PARAM_LABELS = {
  ingresos_mensuales:    'Ingresos Mensuales',
  edad:                  'Edad',
  nivel_endeudamiento:   'Nivel Endeudamiento %',
  meses_empleo_actual:   'Antigüedad Laboral',
  cantidad_atrasos:      'Cantidad Atrasos',
  deuda_total_sistema:   'Deuda Total Sistema',
  score_externo:         'Score Crediticio',
  historial_pagos:       'Historial Pagos',
  en_lista_negra:        'En Lista Negra',
  tipo_empleo:           'Tipo de Empleo',
  referencias_personales:'Referencias Personales',
}

export default function MotorDetallePage() {
  const { motorId } = useParams()
  const navigate    = useNavigate()
  const [motor,   setMotor]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [modal,   setModal]   = useState({ open: false, regla: null })

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const r = await getMotor(motorId)
      setMotor(r.data.data)
    } catch { toast.error('Motor no encontrado'); navigate('/scoring') }
    finally { setLoading(false) }
  }, [motorId, navigate])

  useEffect(() => { fetch() }, [fetch])

  const handleToggleRegla = async (regla) => {
    try {
      await toggleRegla(regla.id)
      toast.success(`Regla ${regla.activo ? 'desactivada' : 'activada'}`)
      fetch()
    } catch { toast.error('Error') }
  }

  const handleDeleteRegla = async (regla) => {
    if (!confirm(`¿Eliminar la regla "${regla.nombre}"?`)) return
    try {
      await deleteRegla(regla.id)
      toast.success('Regla eliminada')
      fetch()
    } catch { toast.error('Error al eliminar') }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
    </div>
  )

  const reglas       = motor?.reglas ?? []
  const scoreMaximo  = reglas.filter(r => r.activo).reduce((s, r) => s + r.peso_puntos, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/scoring')} className="btn-secondary btn-sm">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-900">{motor.nombre}</h1>
          <p className="text-sm text-gray-500">v{motor.version} · {reglas.length} reglas · Puntaje máximo: {scoreMaximo.toFixed(0)} pts</p>
        </div>
        <button onClick={() => setModal({ open: true, regla: null })} className="btn-primary">
          <Plus className="h-4 w-4" /> Nueva regla
        </button>
      </div>

      {/* Info del motor */}
      {motor.descripcion && (
        <div className="card bg-blue-50 border-blue-200 py-3 px-4">
          <p className="text-sm text-blue-700">{motor.descripcion}</p>
        </div>
      )}

      {/* Leyenda */}
      <div className="flex gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded-full bg-red-500 inline-block" />
          Regla determinante (rechazo si falla)
        </span>
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded-full bg-green-500 inline-block" />
          Regla normal
        </span>
      </div>

      {/* Lista de reglas */}
      <div className="space-y-3">
        {reglas.length === 0 && (
          <div className="card text-center py-12 text-gray-400">
            No hay reglas configuradas. Agrega la primera regla.
          </div>
        )}
        {reglas.map((regla, idx) => (
          <div key={regla.id}
            className={`card border-l-4 ${regla.es_determinante ? 'border-l-red-500' : 'border-l-green-500'}
              ${!regla.activo ? 'opacity-50' : ''}`}>
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3 flex-1">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-500">
                  {regla.orden || idx + 1}
                </span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-medium text-gray-900 text-sm">{regla.nombre}</p>
                    {regla.es_determinante && (
                      <span className="flex items-center gap-1 text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="h-3 w-3" /> Determinante
                      </span>
                    )}
                    {!regla.activo && <span className="badge-gray">Inactiva</span>}
                  </div>
                  {regla.descripcion && (
                    <p className="text-xs text-gray-500 mt-0.5">{regla.descripcion}</p>
                  )}
                  {/* Condición IF-THEN visual */}
                  <div className="mt-2 flex items-center gap-2 text-sm">
                    <span className="font-mono bg-gray-100 px-2 py-0.5 rounded text-xs text-gray-700">
                      IF
                    </span>
                    <span className="text-gray-700 font-medium">
                      {PARAM_LABELS[regla.parametro] || regla.parametro}
                    </span>
                    <span className="font-mono bg-primary-100 text-primary-700 px-2 py-0.5 rounded text-xs font-bold">
                      {regla.operador}
                    </span>
                    <span className="font-mono bg-gray-100 px-2 py-0.5 rounded text-xs text-gray-700">
                      {regla.valor_referencia}
                    </span>
                    <span className="font-mono bg-gray-100 px-2 py-0.5 rounded text-xs text-gray-700">
                      THEN
                    </span>
                    <span className="text-green-700 font-bold text-sm">
                      +{regla.peso_puntos} pts
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <button onClick={() => setModal({ open: true, regla })}
                  className="btn-secondary btn-sm" title="Editar">
                  <Pencil className="h-3.5 w-3.5" />
                </button>
                <button onClick={() => handleToggleRegla(regla)}
                  className={`btn btn-sm ${regla.activo
                    ? 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                    : 'bg-green-50 text-green-700 border border-green-200'}`}
                  title={regla.activo ? 'Desactivar' : 'Activar'}>
                  <Power className="h-3.5 w-3.5" />
                </button>
                <button onClick={() => handleDeleteRegla(regla)}
                  className="btn btn-sm bg-red-50 text-red-600 border border-red-200 hover:bg-red-100"
                  title="Eliminar">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Modal open={modal.open} onClose={() => setModal({ open: false, regla: null })}
        title={modal.regla ? 'Editar regla' : 'Nueva regla'} size="lg">
        <ReglaForm
          regla={modal.regla}
          motorId={motorId}
          onSubmitFn={modal.regla
            ? (data) => updateRegla(modal.regla.id, data)
            : (data) => createRegla(motorId, data)}
          onSaved={() => { setModal({ open: false, regla: null }); fetch() }}
          onCancel={() => setModal({ open: false, regla: null })}
        />
      </Modal>
    </div>
  )
}

