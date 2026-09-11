import { useEffect, useState, useCallback } from 'react'
import { Plus, Pencil, Power } from 'lucide-react'
import { getUsers, toggleUser } from '../../api/userApi'
import { Table } from '../../components/Table'
import Modal from '../../components/Modal'
import UserForm from './UserForm'
import toast from 'react-hot-toast'

export default function UsersPage() {
  const [users,   setUsers]   = useState([])
  const [loading, setLoading] = useState(true)
  const [modal,   setModal]   = useState({ open: false, user: null })

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getUsers()
      setUsers(res.data.data)
    } catch {
      toast.error('Error al cargar usuarios')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  const handleToggle = async (user) => {
    try {
      await toggleUser(user.id)
      toast.success(`Usuario ${user.activo ? 'desactivado' : 'activado'}`)
      fetchUsers()
    } catch {
      toast.error('Error al cambiar estado')
    }
  }

  const columns = [
    { key: 'id',       label: '#' },
    { key: 'nombre',   label: 'Nombre', render: (r) => `${r.nombre} ${r.apellido}` },
    { key: 'email',    label: 'Email' },
    {
      key: 'rol', label: 'Rol',
      render: (r) => (
        <span className={r.rol === 'administrador' ? 'badge-blue' : 'badge-gray'}>
          {r.rol}
        </span>
      ),
    },
    {
      key: 'activo', label: 'Estado',
      render: (r) => (
        <span className={r.activo ? 'badge-green' : 'badge-red'}>
          {r.activo ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    {
      key: 'acciones', label: 'Acciones',
      render: (r) => (
        <div className="flex gap-2">
          <button onClick={() => setModal({ open: true, user: r })} className="btn-secondary btn-sm">
            <Pencil className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => handleToggle(r)}
            className={`btn btn-sm ${r.activo ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100' : 'bg-green-50 text-green-600 border border-green-200 hover:bg-green-100'}`}
            title={r.activo ? 'Desactivar' : 'Activar'}
          >
            <Power className="h-3.5 w-3.5" />
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Usuarios</h1>
          <p className="text-gray-500 text-sm">Gestión de accesos al sistema</p>
        </div>
        <button onClick={() => setModal({ open: true, user: null })} className="btn-primary">
          <Plus className="h-4 w-4" /> Nuevo usuario
        </button>
      </div>

      <Table columns={columns} data={users} loading={loading} emptyMessage="Sin usuarios registrados" />

      <Modal
        open={modal.open}
        onClose={() => setModal({ open: false, user: null })}
        title={modal.user ? 'Editar usuario' : 'Nuevo usuario'}
      >
        <UserForm
          user={modal.user}
          onSaved={() => { setModal({ open: false, user: null }); fetchUsers() }}
          onCancel={() => setModal({ open: false, user: null })}
        />
      </Modal>
    </div>
  )
}
