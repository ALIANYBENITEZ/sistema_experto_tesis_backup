import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Power, ChevronRight, Eye, Settings, Trash2 } from 'lucide-react'
import { coreGetModelos, coreDeleteModelo } from '../../api/coreApi'
import { getEmpresas } from '../../api/empresaApi'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function ScoringPage() {
  const navigate = useNavigate()
  const [modelos, setModelos] = useState([])
  const [empresas, setEmpresas] = useState([])
  const [loading, setLoading] = useState(true)
  const [eliminando, setEliminando] = useState(null)
  const { isPropietario } = useAuth()

  const cargarModelos = async () => {
    try {
      const r = await coreGetModelos()
      setModelos(r.data.data)
      if (isPropietario) {
        const e = await getEmpresas()
        setEmpresas(e.data.data)
      }
    } catch { toast.error('Error al cargar modelos') }
    finally { setLoading(false) }
  }

  useEffect(() => {
    cargarModelos()
  }, [isPropietario])

  const handleEliminar = async (modelo) => {
    const ok = window.confirm(
      `¿Eliminar el modelo "${modelo.nombre}"?\n\n` +
      `Si tiene evaluaciones asociadas se desactivará en lugar de eliminarse.`
    )
    if (!ok) return
    setEliminando(modelo.id)
    try {
      const r = await coreDeleteModelo(modelo.id)
      toast.success(r.data.message || 'Modelo eliminado')
      await cargarModelos()
    } catch (err) {
      toast.error(err?.response?.data?.message || 'Error al eliminar el modelo')
    } finally {
      setEliminando(null)
    }
  }

  const getEmpresaNombre = (id) => {
    if (!id || id === 0) return 'Global'
    const e = empresas.find(emp => emp.id === id)
    return e ? e.nombre : `Empresa #${id}`
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Scoring de Riesgo</h1>
          <p className="text-gray-500 text-sm">Configuración de modelos de scoring del sistema experto</p>
        </div>
        {isPropietario && (
          <button onClick={() => navigate('/scoring/nuevo-modelo')} className="btn-primary">
            <Plus className="h-4 w-4" /> Nuevo modelo
          </button>
        )}
      </div>

      {/* Info */}
      <div className="card bg-blue-50 border-blue-200">
        <h2 className="font-semibold text-blue-800 mb-2">Sistema Experto de Evaluación</h2>
        <p className="text-sm text-blue-700">
          Cada modelo contiene factores de evaluación con reglas IF-THEN configurables.
          Los factores se clasifican en principales y complementarios, con pesos positivos (riesgo) y negativos (favorables).
          La clasificación final se determina por umbrales configurables.
        </p>
      </div>

      {/* Modelos */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : modelos.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">
          No hay modelos de scoring configurados.
        </div>
      ) : (
        <div className="space-y-4">
          {modelos.map(m => (
            <div key={m.id} className={`card border-l-4 ${m.activo ? 'border-l-green-500' : 'border-l-gray-300'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-gray-900">{m.nombre}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${m.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                      {m.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    v{m.version} · {m.total_factores} factores
                    {isPropietario && <span className="ml-2">· {getEmpresaNombre(m.id_empresa)}</span>}
                  </p>
                  {m.descripcion && <p className="text-xs text-gray-400 mt-1">{m.descripcion}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => navigate(`/scoring/modelo/${m.id}`)}
                    className="btn-secondary">
                    <Settings className="h-4 w-4" />
                    {isPropietario ? 'Configurar' : 'Ver factores'}
                    <ChevronRight className="h-4 w-4" />
                  </button>
                  {isPropietario && (
                    <button
                      onClick={() => handleEliminar(m)}
                      disabled={eliminando === m.id}
                      title="Eliminar modelo"
                      className="p-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
