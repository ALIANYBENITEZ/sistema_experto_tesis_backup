import { useEffect, useState, useCallback } from 'react'
import { Plus, Search, Eye, Pencil } from 'lucide-react'
import { getClients } from '../../api/clientApi'
import { Table, Pagination } from '../../components/Table'
import Modal from '../../components/Modal'
import ClientForm from './ClientForm'
import ClientDetail from './ClientDetail'
import toast from 'react-hot-toast'

export default function ClientsPage() {
  const [data,    setData]    = useState({ items: [], total: 0, pages: 1 })
  const [loading, setLoading] = useState(true)
  const [page,    setPage]    = useState(1)
  const [search,  setSearch]  = useState('')
  const [modal,   setModal]   = useState({ open: false, client: null })
  const [detail,  setDetail]  = useState({ open: false, client: null })

  const fetchClients = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getClients({ page, per_page: 15, search })
      setData(res.data.data)
    } catch {
      toast.error('Error al cargar clientes')
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => { fetchClients() }, [fetchClients])

  // Reset página al buscar
  useEffect(() => { setPage(1) }, [search])

  const openCreate = () => setModal({ open: true, client: null })
  const openEdit   = (client) => setModal({ open: true, client })
  const closeModal = () => setModal({ open: false, client: null })

  const openDetail  = (client) => setDetail({ open: true, client })
  const closeDetail = () => setDetail({ open: false, client: null })

  const onSaved = () => { closeModal(); fetchClients(); }

  const columns = [
    { key: 'num_doc',  label: 'N° Documento' },
    { key: 'tipo_doc', label: 'Tipo' },
    { key: 'nombre',   label: 'Nombre', render: (r) => `${r.nombre} ${r.apellido ?? ''}` },
    { key: 'email',    label: 'Email',  render: (r) => r.email || '—' },
    { key: 'telefono', label: 'Teléfono', render: (r) => r.telefono || '—' },
    {
      key: 'estado', label: 'Estado',
      render: (r) => (
        <span className={r.estado === 'activo' ? 'badge-green' : 'badge-gray'}>
          {r.estado}
        </span>
      ),
    },
    {
      key: 'acciones', label: 'Acciones',
      render: (r) => (
        <div className="flex gap-2">
          <button onClick={() => openDetail(r)} className="btn-secondary btn-sm" title="Ver detalle">
            <Eye className="h-3.5 w-3.5" />
          </button>
          <button onClick={() => openEdit(r)} className="btn-secondary btn-sm" title="Editar">
            <Pencil className="h-3.5 w-3.5" />
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
          <p className="text-gray-500 text-sm">Gestión de clientes registrados</p>
        </div>
        <button onClick={openCreate} className="btn-primary">
          <Plus className="h-4 w-4" /> Nuevo cliente
        </button>
      </div>

      {/* Búsqueda */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          className="input pl-9"
          placeholder="Buscar por nombre, doc, email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Table columns={columns} data={data.items} loading={loading} emptyMessage="No se encontraron clientes" />
      <Pagination
        page={page} pages={data.pages} total={data.total} perPage={15}
        onPageChange={setPage}
      />

      <Modal
        open={modal.open}
        onClose={closeModal}
        title={modal.client ? 'Editar cliente' : 'Nuevo cliente'}
        size="lg"
      >
        <ClientForm client={modal.client} onSaved={onSaved} onCancel={closeModal} />
      </Modal>

      <Modal
        open={detail.open}
        onClose={closeDetail}
        title="Detalle del cliente"
        size="lg"
      >
        <ClientDetail client={detail.client} />
      </Modal>
    </div>
  )
}
