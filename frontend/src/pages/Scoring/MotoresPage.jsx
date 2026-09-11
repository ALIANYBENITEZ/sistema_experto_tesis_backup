import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, Power, Pencil } from 'lucide-react'
import { getMotores, createMotor, updateMotor, toggleMotor } from '../../api/scoringApi'
import { getEmpresas } from '../../api/empresaApi'
import { useAuth } from '../../context/AuthContext'
import Modal from '../../components/Modal'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

function MotorForm({ motor, empresas, onSaved, onCancel }) {
  const isEdit = Boolean(motor)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    defaultValues: motor ?? { nombre: '', version: '1.0', descripcion: '', id_empresa_motor: '' },
  })
  const onSubmit = async (data) => {
    // Convertir id_empresa_motor a int o 0
    data.id_empresa_motor = data.id_empresa_motor ? parseInt(data.id_empresa_motor) : 0
    try {
      isEdit ? await updateMotor(motor.id, data) : await createMotor(data)
      toast.success(isEdit ? 'Motor actualizado' : 'Motor creado')
      onSaved()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al guardar')
    }
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="label">Nombre *</label>
        <input className={`input ${errors.nombre ? 'border-red-400' : ''}`}
          {...register('nombre', { required: 'Requerido' })} />
        {errors.nombre && <p className="text-xs text-red-600 mt-1">{errors.nombre.message}</p>}
      </div>
      <div>
        <label className="label">Empresa perteneciente *</label>
        <select className="input" {...register('id_empresa_motor', { required: 'Seleccione una empresa' })}>
          <option value="">— Seleccionar empresa —</option>
          {empresas.map(e => (
            <option key={e.id} value={e.id}>{e.nombre}</option>
          ))}
        </select>
        {errors.id_empresa_motor && <p className="text-xs text-red-600 mt-1">{errors.id_empresa_motor.message}</p>}
      </div>
      <div>
        <label className="label">Versión</label>
        <input className="input" {...register('version')} />
      </div>
      <div>
        <label className="label">Descripción</label>
        <textarea className="input resize-none h-20" {...register('descripcion')} />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        <button type="submit" className="btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando…' : isEdit ? 'Actualizar' : 'Crear'}
        </button>
      </div>
    </form>
  )
}

export default function MotoresPage() {
  const navigate = useNavigate()
  const { isPropietario } = useAuth()
  const [motores, setMotores] = useState([])
  const [empresas, setEmpresas] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState({ open: false, motor: null })

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const r = await getMotores()
      setMotores(r.data.data)
      if (isPropietario) {
        const e = await getEmpresas()
        setEmpresas(e.data.data)
      }
    } catch { toast.error('Error al cargar motores') }
    finally { setLoading(false) }
  }, [isPropietario])

  useEffect(() => { fetch() }, [fetch])

  const handleToggle = async (motor) => {
    try {
      await toggleMotor(motor.id)
      toast.success(`Motor ${motor.activo ? 'desactivado' : 'activado'}`)
      fetch()
    } catch { toast.error('Error') }
  }

  // Encontrar nombre de empresa por id
  const getEmpresaNombre = (id) => {
    if (!id || id === 0) return 'Global'
    const e = empresas.find(emp => emp.id === id)
    return e ? e.nombre : `Empresa #${id}`
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Motores de Reglas</h1>
          <p className="text-gray-500 text-sm">Plantillas de evaluación de riesgo</p>
        </div>
        {isPropietario && (
          <button onClick={() => setModal({ open: true, motor: null })} className="btn-primary">
            <Plus className="h-4 w-4" /> Nuevo motor
          </button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {motores.map(motor => (
            <div key={motor.id} className="card flex flex-col gap-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{motor.nombre}</p>
                  <p className="text-xs text-gray-500">v{motor.version} · {getEmpresaNombre(motor.id_empresa_motor)}</p>
                </div>
                <span className={motor.activo ? 'badge-green' : 'badge-gray'}>
                  {motor.activo ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              {motor.descripcion && (
                <p className="text-sm text-gray-600 line-clamp-2">{motor.descripcion}</p>
              )}
              <div className="flex items-center justify-between text-sm text-gray-500 border-t border-gray-100 pt-3">
                <span>{motor.total_reglas} reglas configuradas</span>
                <div className="flex gap-2">
                  <button onClick={() => navigate(`/scoring/motores/${motor.id}`)}
                    className="btn-secondary btn-sm" title="Ver reglas">
                    <Eye className="h-3.5 w-3.5" />
                  </button>
                  {isPropietario && (
                    <>
                      <button onClick={() => setModal({ open: true, motor })}
                        className="btn-secondary btn-sm" title="Editar">
                        <Pencil className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => handleToggle(motor)}
                        className={`btn btn-sm ${motor.activo
                          ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100'
                          : 'bg-green-50 text-green-600 border border-green-200 hover:bg-green-100'}`}
                        title={motor.activo ? 'Desactivar' : 'Activar'}>
                        <Power className="h-3.5 w-3.5" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
          {motores.length === 0 && (
            <div className="col-span-full text-center py-16 text-gray-400">
              {isPropietario ? 'No hay motores configurados. Crea el primero.' : 'No hay motores asignados a tu empresa.'}
            </div>
          )}
        </div>
      )}

      {isPropietario && (
        <Modal open={modal.open} onClose={() => setModal({ open: false, motor: null })}
          title={modal.motor ? 'Editar motor' : 'Nuevo motor'}>
          <MotorForm motor={modal.motor} empresas={empresas}
            onSaved={() => { setModal({ open: false, motor: null }); fetch() }}
            onCancel={() => setModal({ open: false, motor: null })} />
        </Modal>
      )}
    </div>
  )
}
