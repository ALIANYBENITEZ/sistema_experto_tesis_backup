import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye, Power } from 'lucide-react'
import { getEmpresas, toggleEmpresa } from '../../api/empresaApi'
import toast from 'react-hot-toast'

export default function EmpresasPage() {
  const navigate = useNavigate()
  const [empresas, setEmpresas] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  const fetch = async () => {
    setLoading(true)
    try {
      const r = await getEmpresas()
      setEmpresas(r.data.data)
    } catch { toast.error('Error al cargar empresas') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetch() }, [])

  const handleToggle = async (id) => {
    try {
      await toggleEmpresa(id)
      toast.success('Estado actualizado')
      fetch()
    } catch { toast.error('Error') }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Empresas Clientes</h1>
          <p className="text-gray-500 text-sm">Inmobiliarias que utilizan el sistema</p>
        </div>
        <button onClick={() => navigate('/empresas/new')} className="btn-primary">
          <Plus className="h-4 w-4" /> Nueva Empresa
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : empresas.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-400">No hay empresas registradas</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {empresas.map(e => (
            <div key={e.id} className={`card flex items-center justify-between ${!e.activo ? 'opacity-60' : ''}`}>
              <div className="flex items-center gap-4">
                <button onClick={() => handleToggle(e.id)}
                  className={`p-2 rounded-full ${e.activo ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                  <Power className="h-4 w-4" />
                </button>
                <div>
                  <p className="font-semibold text-gray-900">{e.nombre}</p>
                  <p className="text-xs text-gray-500">
                    RUC: {e.ruc || '—'} · {e.total_usuarios} usuarios · {e.activo ? 'Activa' : 'Inactiva'}
                  </p>
                  {e.email && <p className="text-xs text-gray-400">{e.email}</p>}
                </div>
              </div>
              <button onClick={() => navigate(`/empresas/${e.id}`)} className="btn-secondary btn-sm">
                <Eye className="h-3.5 w-3.5" /> Ver / Usuarios
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
