import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, ShieldCheck } from 'lucide-react'
import { coreCreateModelo } from '../../api/coreApi'
import { getEmpresas } from '../../api/empresaApi'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function NuevoModeloPage() {
  const navigate = useNavigate()
  const { isPropietario } = useAuth()

  const [empresas, setEmpresas] = useState([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    nombre: '',
    version: '1.0',
    descripcion: '',
    id_empresa: '',
  })

  useEffect(() => {
    // Solo el propietario puede crear modelos y elegir empresa
    if (!isPropietario) {
      navigate('/scoring', { replace: true })
      return
    }
    getEmpresas()
      .then((r) => setEmpresas(r.data.data))
      .catch(() => toast.error('No se pudieron cargar las empresas'))
  }, [isPropietario, navigate])

  const setF = (k, v) => setForm((prev) => ({ ...prev, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.nombre.trim()) {
      toast.error('El nombre del modelo es requerido')
      return
    }
    if (!form.id_empresa) {
      toast.error('Debe seleccionar la empresa a la que pertenece el modelo')
      return
    }

    setLoading(true)
    try {
      const payload = {
        nombre: form.nombre.trim(),
        version: form.version.trim() || '1.0',
        descripcion: form.descripcion.trim(),
        id_empresa: parseInt(form.id_empresa, 10),
      }
      const r = await coreCreateModelo(payload)
      const nuevo = r.data.data
      toast.success('Modelo creado correctamente')
      // Ir directo a la configuración del modelo para cargar factores/reglas
      navigate(`/scoring/modelo/${nuevo.id}`)
    } catch (err) {
      const msg = err?.response?.data?.message || 'Error al crear el modelo'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/scoring')}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary-100 rounded-lg">
            <ShieldCheck className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Nuevo modelo de scoring</h1>
            <p className="text-gray-500 text-sm">Crea un modelo de evaluación para una empresa</p>
          </div>
        </div>
      </div>

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="card space-y-5">
        <div>
          <label className="label">Nombre del modelo *</label>
          <input
            type="text" className="input"
            placeholder="Ej: Riesgo Comercial Inmobiliario"
            value={form.nombre}
            onChange={(e) => setF('nombre', e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="label">Versión</label>
            <input
              type="text" className="input"
              placeholder="1.0"
              value={form.version}
              onChange={(e) => setF('version', e.target.value)}
            />
          </div>
          <div>
            <label className="label">Empresa perteneciente *</label>
            <select
              className="input"
              value={form.id_empresa}
              onChange={(e) => setF('id_empresa', e.target.value)}
            >
              <option value="">Seleccione una empresa…</option>
              {empresas.map((e) => (
                <option key={e.id} value={e.id}>{e.nombre}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="label">Descripción</label>
          <textarea
            className="input" rows={3}
            placeholder="Descripción del modelo y su propósito"
            value={form.descripcion}
            onChange={(e) => setF('descripcion', e.target.value)}
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button type="submit" className="btn-primary" disabled={loading}>
            <Save className="h-4 w-4" />
            {loading ? 'Guardando…' : 'Crear modelo'}
          </button>
          <button type="button" onClick={() => navigate('/scoring')} className="btn-secondary">
            Cancelar
          </button>
        </div>

        <p className="text-xs text-gray-400">
          Tras crear el modelo podrás configurar sus factores, reglas IF-THEN y umbrales de clasificación.
        </p>
      </form>
    </div>
  )
}
