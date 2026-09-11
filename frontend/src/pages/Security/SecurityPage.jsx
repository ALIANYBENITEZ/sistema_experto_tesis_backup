import { useEffect, useState } from 'react'
import { ShieldCheck, ShieldX, RefreshCw } from 'lucide-react'
import { getSecurityUsers, reset2FA } from '../../api/authApi'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function SecurityPage() {
  const { isPropietario } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  const fetch = async () => {
    setLoading(true)
    try {
      const r = await getSecurityUsers()
      setUsers(r.data.data)
    } catch { toast.error('Error al cargar datos de seguridad') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])

  const handleReset2FA = async (user) => {
    if (!confirm(`¿Restablecer el 2FA de ${user.nombre} ${user.apellido}? Deberá configurar nuevamente su autenticador.`)) return
    try {
      await reset2FA(user.id)
      toast.success(`2FA restablecido para ${user.nombre}`)
      fetch()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al restablecer')
    }
  }

  // Agrupar por empresa si es propietario
  const empresasMap = {}
  users.forEach(u => {
    const key = u.empresa_nombre || 'Sin empresa'
    if (!empresasMap[key]) empresasMap[key] = []
    empresasMap[key].push(u)
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Seguridad</h1>
        <p className="text-gray-500 text-sm">Gestión de autenticación de dos factores (2FA)</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(empresasMap).map(([empresa, usuarios]) => (
            <div key={empresa} className="card">
              {isPropietario && (
                <h2 className="font-semibold text-gray-800 mb-4 border-b border-gray-200 pb-2">{empresa}</h2>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-200">
                      <th className="pb-2 pr-4">Usuario</th>
                      <th className="pb-2 pr-4">Rol</th>
                      <th className="pb-2 pr-4">Estado 2FA</th>
                      <th className="pb-2 pr-4">Configurado</th>
                      <th className="pb-2 pr-4">Cuenta</th>
                      <th className="pb-2">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {usuarios.map(u => (
                      <tr key={u.id} className="border-b border-gray-100 last:border-0">
                        <td className="py-3 pr-4">
                          <p className="font-medium text-gray-900">{u.nombre} {u.apellido}</p>
                          <p className="text-xs text-gray-400">{u.email}</p>
                        </td>
                        <td className="py-3 pr-4 capitalize text-gray-600">{u.rol}</td>
                        <td className="py-3 pr-4">
                          {u.tiene_2fa ? (
                            <span className="flex items-center gap-1 text-green-600 text-xs font-medium">
                              <ShieldCheck className="h-4 w-4" /> Activado
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-gray-400 text-xs">
                              <ShieldX className="h-4 w-4" /> {u.totp_estado === 'restablecido' ? 'Restablecido' : 'No configurado'}
                            </span>
                          )}
                        </td>
                        <td className="py-3 pr-4 text-xs text-gray-500">
                          {u.totp_fecha_config ? new Date(u.totp_fecha_config).toLocaleDateString('es-PY') : '—'}
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`text-xs ${u.activo ? 'text-green-600' : 'text-red-600'}`}>
                            {u.activo ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                        <td className="py-3">
                          {u.tiene_2fa && (
                            <button onClick={() => handleReset2FA(u)}
                              className="btn-secondary btn-sm text-xs"
                              title="Restablecer 2FA">
                              <RefreshCw className="h-3.5 w-3.5" /> Reset 2FA
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
