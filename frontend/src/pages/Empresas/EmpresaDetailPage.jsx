import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Power, UserPlus } from 'lucide-react'
import { getEmpresa, updateEmpresa, getUsuariosEmpresa, createUsuarioEmpresa, toggleUsuario } from '../../api/empresaApi'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'

export default function EmpresaDetailPage() {
  const { empresaId } = useParams()
  const navigate = useNavigate()
  const [empresa, setEmpresa] = useState(null)
  const [usuarios, setUsuarios] = useState([])
  const [showUserForm, setShowUserForm] = useState(false)
  const [loading, setLoading] = useState(true)

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm()

  const fetch = async () => {
    try {
      const [e, u] = await Promise.all([
        getEmpresa(empresaId),
        getUsuariosEmpresa(empresaId),
      ])
      setEmpresa(e.data.data)
      setUsuarios(u.data.data)
    } catch { toast.error('Error al cargar empresa') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [empresaId])

  const handleToggleUser = async (userId) => {
    try {
      await toggleUsuario(userId)
      toast.success('Estado actualizado')
      fetch()
    } catch { toast.error('Error') }
  }

  const onCreateUser = async (data) => {
    try {
      await createUsuarioEmpresa(empresaId, data)
      toast.success('Usuario creado')
      setShowUserForm(false)
      reset()
      fetch()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al crear usuario')
    }
  }

  if (loading) return (
    <div className="flex justify-center py-12">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/empresas')} className="btn-secondary btn-sm">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">{empresa?.nombre}</h1>
          <p className="text-sm text-gray-500">RUC: {empresa?.ruc || '—'} · {empresa?.email || ''}</p>
        </div>
      </div>

      {/* Info empresa */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-3">Datos de la empresa</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          <div><p className="text-gray-500 text-xs">Dirección</p><p className="font-medium">{empresa?.direccion || '—'}</p></div>
          <div><p className="text-gray-500 text-xs">Teléfono</p><p className="font-medium">{empresa?.telefono || '—'}</p></div>
          <div><p className="text-gray-500 text-xs">Estado</p><p className={`font-medium ${empresa?.activo ? 'text-green-600' : 'text-red-600'}`}>{empresa?.activo ? 'Activa' : 'Inactiva'}</p></div>
        </div>
      </div>

      {/* Usuarios */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-800">Usuarios ({usuarios.length})</h2>
          <button onClick={() => setShowUserForm(!showUserForm)} className="btn-primary btn-sm">
            <UserPlus className="h-3.5 w-3.5" /> Nuevo usuario
          </button>
        </div>

        {showUserForm && (
          <form onSubmit={handleSubmit(onCreateUser)} className="bg-gray-50 rounded-lg p-4 mb-4 space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <input className="input text-sm" placeholder="Nombre *" {...register('nombre', { required: true })} />
              <input className="input text-sm" placeholder="Apellido *" {...register('apellido', { required: true })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input className="input text-sm" type="email" placeholder="Email *" {...register('email', { required: true })} />
              <input className="input text-sm" type="password" placeholder="Contraseña *" {...register('password', { required: true })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <select className="input text-sm" {...register('rol')}>
                <option value="administrador">Administrador</option>
                <option value="comercial">Comercial</option>
              </select>
              <div className="flex gap-2">
                <button type="submit" className="btn-primary btn-sm flex-1" disabled={isSubmitting}>
                  {isSubmitting ? 'Creando...' : 'Crear'}
                </button>
                <button type="button" onClick={() => setShowUserForm(false)} className="btn-secondary btn-sm">
                  Cancelar
                </button>
              </div>
            </div>
          </form>
        )}

        {usuarios.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-6">Sin usuarios registrados</p>
        ) : (
          <div className="space-y-2">
            {usuarios.map(u => (
              <div key={u.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold text-xs">
                    {u.nombre?.[0]}{u.apellido?.[0]}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{u.nombre} {u.apellido}</p>
                    <p className="text-xs text-gray-500">{u.email} · <span className="capitalize">{u.rol}</span></p>
                  </div>
                </div>
                <button onClick={() => handleToggleUser(u.id)}
                  className={`p-1.5 rounded-full ${u.activo ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}
                  title={u.activo ? 'Desactivar' : 'Activar'}>
                  <Power className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
