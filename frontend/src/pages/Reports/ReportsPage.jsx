import { useState } from 'react'
import { Download, Search } from 'lucide-react'
import { getReportList, exportPdf } from '../../api/reportApi'
import { Table } from '../../components/Table'
import ResultadoBadge from '../../components/ResultadoBadge'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function ReportsPage() {
  const { user } = useAuth()
  const esPropietario = user?.rol === 'propietario' && user?.id_empresa === 0

  const [filters, setFilters] = useState({ fecha_from: '', fecha_to: '', resultado: '' })
  const [data,    setData]    = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const buildParams = () => {
    const p = {}
    if (filters.fecha_from) p.fecha_from = filters.fecha_from
    if (filters.fecha_to)   p.fecha_to   = filters.fecha_to
    if (filters.resultado)  p.resultado  = filters.resultado
    return p
  }

  const handleSearch = async () => {
    setLoading(true)
    setSearched(true)
    try {
      const res = await getReportList(buildParams())
      setData(res.data.data.items)
    } catch {
      toast.error('Error al generar reporte')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      toast.loading('Generando PDF…', { id: 'pdf' })
      const res = await exportPdf(buildParams())
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a   = document.createElement('a')
      a.href = url
      a.download = `reporte_evaluaciones.pdf`
      a.click()
      URL.revokeObjectURL(url)
      toast.success('PDF descargado', { id: 'pdf' })
    } catch {
      toast.error('Error al exportar PDF', { id: 'pdf' })
    }
  }

  const columns = [
    { key: 'id',            label: '#' },
    { key: 'fecha',         label: 'Fecha' },
    // Columna de empresa cliente — solo visible para el propietario
    ...(esPropietario ? [{ key: 'empresa', label: 'Empresa cliente' }] : []),
    { key: 'cliente',       label: 'Cliente' },
    { key: 'num_doc',       label: 'N° Doc' },
    { key: 'puntaje_total', label: 'Puntaje', render: (r) => (
        <span className="font-bold">{r.puntaje_total?.toFixed(1)}</span>
      )
    },
    { key: 'resultado', label: 'Resultado', render: (r) => <ResultadoBadge resultado={r.resultado} /> },
    { key: 'estado', label: 'Estado', render: (r) => (
        <span className={r.estado === 'completado' ? 'badge-blue' : 'badge-gray'}>{r.estado}</span>
      )
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reportes</h1>
        <p className="text-gray-500 text-sm">Filtra y exporta evaluaciones</p>
      </div>

      {/* Filtros */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-4">Filtros</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="label">Fecha desde</label>
            <input
              type="date" className="input"
              value={filters.fecha_from}
              onChange={e => setFilters(f => ({ ...f, fecha_from: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Fecha hasta</label>
            <input
              type="date" className="input"
              value={filters.fecha_to}
              onChange={e => setFilters(f => ({ ...f, fecha_to: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Resultado</label>
            <select
              className="input"
              value={filters.resultado}
              onChange={e => setFilters(f => ({ ...f, resultado: e.target.value }))}
            >
              <option value="">Todos</option>
              <option value="bajo">Bajo riesgo</option>
              <option value="medio">Medio riesgo</option>
              <option value="alto">Alto riesgo</option>
              <option value="rechazado">Rechazado</option>
            </select>
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button onClick={handleSearch} className="btn-primary" disabled={loading}>
            <Search className="h-4 w-4" /> Buscar
          </button>
          {data.length > 0 && (
            <button onClick={handleExport} className="btn-secondary">
              <Download className="h-4 w-4" /> Exportar PDF
            </button>
          )}
        </div>
      </div>

      {/* Resultados */}
      {searched && (
        <div>
          <p className="text-sm text-gray-500 mb-3">{data.length} evaluaciones encontradas</p>
          <Table columns={columns} data={data} loading={loading} emptyMessage="Sin resultados para los filtros aplicados" />
        </div>
      )}
    </div>
  )
}
