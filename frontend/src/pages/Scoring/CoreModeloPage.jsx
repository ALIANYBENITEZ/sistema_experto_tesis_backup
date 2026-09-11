import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, ChevronDown, ChevronRight } from 'lucide-react'
import { coreGetModelo, coreCreateFactor, coreCreateRegla } from '../../api/coreApi'
import { useAuth } from '../../context/AuthContext'
import Modal from '../../components/Modal'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

const NIVEL_COLORS = { bajo: 'bg-green-100 text-green-700', medio: 'bg-yellow-100 text-yellow-700', alto: 'bg-red-100 text-red-700' }

export default function CoreModeloPage() {
  const { modeloId } = useParams()
  const navigate = useNavigate()
  const { isPropietario } = useAuth()
  const [modelo, setModelo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedFactor, setExpandedFactor] = useState(null)
  const [modalFactor, setModalFactor] = useState(false)
  const [modalRegla, setModalRegla] = useState(null) // factorId

  const fetch = useCallback(async () => {
    try {
      const r = await coreGetModelo(modeloId)
      setModelo(r.data.data)
    } catch { toast.error('Modelo no encontrado'); navigate('/scoring') }
    finally { setLoading(false) }
  }, [modeloId])

  useEffect(() => { fetch() }, [fetch])

  if (loading) return <div className="flex justify-center py-16"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" /></div>
  if (!modelo) return null

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/scoring')} className="btn-secondary btn-sm">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-900">{modelo.nombre}</h1>
          <p className="text-sm text-gray-500">v{modelo.version} · {modelo.factores?.length || 0} factores</p>
        </div>
        {isPropietario && (
          <button onClick={() => setModalFactor(true)} className="btn-primary">
            <Plus className="h-4 w-4" /> Agregar factor
          </button>
        )}
      </div>

      {/* Umbrales */}
      {modelo.umbrales?.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-3">Umbrales de Clasificación</h2>
          <div className="grid grid-cols-3 gap-3">
            {modelo.umbrales.map(u => (
              <div key={u.id} className={`rounded-lg p-3 text-center ${NIVEL_COLORS[u.nivel]}`}>
                <p className="text-xs font-semibold uppercase">{u.nivel}</p>
                <p className="text-lg font-bold">{u.score_min} — {u.score_max}</p>
                {u.descripcion && <p className="text-xs mt-1 opacity-75">{u.descripcion}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Factores */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-4">Factores de Evaluación</h2>
        {(!modelo.factores || modelo.factores.length === 0) ? (
          <p className="text-sm text-gray-400 text-center py-8">No hay factores configurados</p>
        ) : (
          <div className="space-y-2">
            {modelo.factores.map(f => (
              <div key={f.id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Factor header */}
                <div
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => setExpandedFactor(expandedFactor === f.id ? null : f.id)}
                >
                  <div className="flex items-center gap-3">
                    {expandedFactor === f.id ? <ChevronDown className="h-4 w-4 text-gray-400" /> : <ChevronRight className="h-4 w-4 text-gray-400" />}
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900">{f.nombre}</p>
                        <span className={`text-xs px-1.5 py-0.5 rounded ${f.categoria === 'principal' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
                          {f.categoria}
                        </span>
                        <span className="text-xs text-gray-400">{f.tipo_dato}</span>
                        <span className="text-xs text-gray-400">· {f.tipo_persona}</span>
                        {f.obligatorio && <span className="text-xs text-red-500">*</span>}
                      </div>
                      {f.descripcion && <p className="text-xs text-gray-500 mt-0.5">{f.descripcion}</p>}
                    </div>
                  </div>
                  <span className="text-xs text-gray-400">{f.reglas?.length || 0} reglas</span>
                </div>

                {/* Reglas expandidas */}
                {expandedFactor === f.id && (
                  <div className="border-t border-gray-200 bg-gray-50 p-4">
                    {isPropietario && (
                      <button onClick={() => setModalRegla(f.id)} className="btn-secondary btn-sm mb-3">
                        <Plus className="h-3.5 w-3.5" /> Agregar regla
                      </button>
                    )}
                    {f.reglas?.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-200">
                              <th className="pb-2 pr-3">Nombre</th>
                              <th className="pb-2 pr-3">Condición</th>
                              <th className="pb-2 pr-3">Nivel</th>
                              <th className="pb-2 pr-3">Peso</th>
                              <th className="pb-2">Explicación</th>
                            </tr>
                          </thead>
                          <tbody>
                            {f.reglas.map(r => (
                              <tr key={r.id} className="border-b border-gray-100 last:border-0">
                                <td className="py-2 pr-3 font-medium text-gray-800">{r.nombre}</td>
                                <td className="py-2 pr-3 font-mono text-xs">
                                  {r.operador} {r.valor_min}{r.valor_max ? ` — ${r.valor_max}` : ''}
                                </td>
                                <td className="py-2 pr-3">
                                  <span className={`text-xs px-1.5 py-0.5 rounded ${NIVEL_COLORS[r.nivel]}`}>
                                    {r.nivel}
                                  </span>
                                </td>
                                <td className={`py-2 pr-3 font-bold ${r.peso >= 0 ? (r.peso > 0 ? 'text-red-600' : 'text-gray-400') : 'text-green-600'}`}>
                                  {r.peso > 0 ? '+' : ''}{r.peso}
                                </td>
                                <td className="py-2 text-xs text-gray-500 max-w-xs truncate">{r.explicacion || '—'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-xs text-gray-400">Sin reglas configuradas</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal: Nuevo Factor */}
      {isPropietario && (
        <Modal open={modalFactor} onClose={() => setModalFactor(false)} title="Nuevo Factor">
          <FactorForm modeloId={modeloId} onSaved={() => { setModalFactor(false); fetch() }} onCancel={() => setModalFactor(false)} />
        </Modal>
      )}

      {/* Modal: Nueva Regla */}
      {isPropietario && modalRegla && (
        <Modal open={!!modalRegla} onClose={() => setModalRegla(null)} title="Nueva Regla">
          <ReglaForm factorId={modalRegla} onSaved={() => { setModalRegla(null); fetch() }} onCancel={() => setModalRegla(null)} />
        </Modal>
      )}
    </div>
  )
}

// ── Formulario de Factor ──
function FactorForm({ modeloId, onSaved, onCancel }) {
  const { register, handleSubmit, formState: { isSubmitting } } = useForm({
    defaultValues: { codigo: '', nombre: '', descripcion: '', tipo_dato: 'numerico', tipo_persona: 'AMBOS', categoria: 'principal', obligatorio: true, orden: 0 }
  })

  const onSubmit = async (data) => {
    data.obligatorio = data.obligatorio === 'true' || data.obligatorio === true
    data.orden = parseInt(data.orden) || 0
    try {
      await coreCreateFactor(modeloId, data)
      toast.success('Factor creado')
      onSaved()
    } catch (err) { toast.error(err.response?.data?.message || 'Error') }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div><label className="label text-xs">Código *</label><input className="input text-sm" placeholder="ej: ingresos_mensuales" {...register('codigo', { required: true })} /></div>
        <div><label className="label text-xs">Nombre *</label><input className="input text-sm" placeholder="ej: Ingresos Mensuales" {...register('nombre', { required: true })} /></div>
      </div>
      <div><label className="label text-xs">Descripción</label><input className="input text-sm" {...register('descripcion')} /></div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="label text-xs">Tipo dato *</label>
          <select className="input text-sm" {...register('tipo_dato')}>
            <option value="numerico">Numérico</option>
            <option value="porcentaje">Porcentaje</option>
            <option value="catalogo">Catálogo</option>
            <option value="booleano">Booleano</option>
            <option value="texto">Texto</option>
          </select>
        </div>
        <div>
          <label className="label text-xs">Tipo persona</label>
          <select className="input text-sm" {...register('tipo_persona')}>
            <option value="AMBOS">Ambos</option>
            <option value="PF">Persona Física</option>
            <option value="PJ">Persona Jurídica</option>
          </select>
        </div>
        <div>
          <label className="label text-xs">Categoría</label>
          <select className="input text-sm" {...register('categoria')}>
            <option value="principal">Principal</option>
            <option value="complementario">Complementario</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label text-xs">Obligatorio</label>
          <select className="input text-sm" {...register('obligatorio')}>
            <option value="true">Sí</option>
            <option value="false">No</option>
          </select>
        </div>
        <div><label className="label text-xs">Orden</label><input type="number" className="input text-sm" {...register('orden')} /></div>
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary btn-sm">Cancelar</button>
        <button type="submit" className="btn-primary btn-sm" disabled={isSubmitting}>{isSubmitting ? 'Creando...' : 'Crear Factor'}</button>
      </div>
    </form>
  )
}

// ── Formulario de Regla ──
function ReglaForm({ factorId, onSaved, onCancel }) {
  const { register, handleSubmit, formState: { isSubmitting } } = useForm({
    defaultValues: { nombre: '', operador: '>=', valor_min: '', valor_max: '', nivel: 'bajo', peso: 0, explicacion: '', orden: 0 }
  })

  const onSubmit = async (data) => {
    data.peso = parseFloat(data.peso)
    data.orden = parseInt(data.orden) || 0
    try {
      await coreCreateRegla(factorId, data)
      toast.success('Regla creada')
      onSaved()
    } catch (err) { toast.error(err.response?.data?.message || 'Error') }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div><label className="label text-xs">Nombre *</label><input className="input text-sm" placeholder="ej: Ingresos altos" {...register('nombre', { required: true })} /></div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="label text-xs">Operador *</label>
          <select className="input text-sm" {...register('operador')}>
            <option value=">=">Mayor o igual (≥)</option>
            <option value="<=">Menor o igual (≤)</option>
            <option value="==">Igual (=)</option>
            <option value=">">Mayor (&gt;)</option>
            <option value="<">Menor (&lt;)</option>
            <option value="!=">Diferente (≠)</option>
            <option value="entre">Entre (rango)</option>
            <option value="en">En (lista)</option>
          </select>
        </div>
        <div><label className="label text-xs">Valor mín / referencia</label><input className="input text-sm" placeholder="ej: 8000000" {...register('valor_min')} /></div>
        <div><label className="label text-xs">Valor máx (para "entre")</label><input className="input text-sm" placeholder="ej: 10000000" {...register('valor_max')} /></div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="label text-xs">Nivel resultado *</label>
          <select className="input text-sm" {...register('nivel')}>
            <option value="bajo">Bajo</option>
            <option value="medio">Medio</option>
            <option value="alto">Alto</option>
          </select>
        </div>
        <div><label className="label text-xs">Peso * (- favorable, + riesgo)</label><input type="number" step="0.1" className="input text-sm" placeholder="ej: -3 o +15" {...register('peso', { required: true })} /></div>
        <div><label className="label text-xs">Orden</label><input type="number" className="input text-sm" {...register('orden')} /></div>
      </div>
      <div><label className="label text-xs">Explicación</label><input className="input text-sm" placeholder="Texto que se mostrará en el reporte" {...register('explicacion')} /></div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary btn-sm">Cancelar</button>
        <button type="submit" className="btn-primary btn-sm" disabled={isSubmitting}>{isSubmitting ? 'Creando...' : 'Crear Regla'}</button>
      </div>
    </form>
  )
}
