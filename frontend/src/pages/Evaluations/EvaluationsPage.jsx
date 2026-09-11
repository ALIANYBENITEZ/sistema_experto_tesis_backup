import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Eye } from 'lucide-react'
import { coreGetEvaluaciones } from '../../api/coreApi'
import { Table, Pagination } from '../../components/Table'
import ResultadoBadge from '../../components/ResultadoBadge'
import toast from 'react-hot-toast'

export default function EvaluationsPage() {
  const navigate = useNavigate()
  const [data, setData] = useState({ items: [], total: 0, pages: 1 })
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [filtro, setFiltro] = useState('')

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page, per_page: 15 }
      if (filtro) params.clasificacion = filtro
      const r = await coreGetEvaluaciones(params)
      setData(r.data.data)
    } catch {
      toast.error('Error al cargar evaluaciones')
    } finally {
      setLoading(false)
    }
  }, [page, filtro])

  useEffect(() => { fetch() }, [fetch])
  useEffect(() => { setPage(1) }, [filtro])

  const columns = [
    { key: 'id', label: '#' },
    { key: 'fecha', label: 'Fecha',
      render: (r) => r.fecha ? new Date(r.fecha).toLocaleDateString('es-PY') : '—' },
    { key: 'cliente_nombre', label: 'Cliente' },
    { key: 'num_doc', label: 'N° Doc' },
    { key: 'score_total', label: 'Score',
      render: (r) => <span className="font-bold text-gray-800">{r.score_total?.toFixed(1)} pts</span>
    },
    { key: 'clasificacion', label: 'Riesgo',
      render: (r) => <ResultadoBadge resultado={r.clasificacion} />
    },
    { key: 'tipo_persona', label: 'Tipo',
      render: (r) => <span className="text-xs text-gray-500">{r.tipo_persona}</span>
    },
    { key: 'acciones', label: 'Acciones',
      render: (r) => (
        <button onClick={() => navigate(`/evaluations/resultado/${r.id}`)} className="btn-secondary btn-sm">
          <Eye className="h-3.5 w-3.5" /> Ver
        </button>
      )
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Evaluaciones</h1>
          <p className="text-gray-500 text-sm">Historial de evaluaciones de riesgo comercial</p>
        </div>
        <button onClick={() => navigate('/evaluations/new')} className="btn-primary">
          <Plus className="h-4 w-4" /> Nueva evaluación
        </button>
      </div>

      <div className="flex gap-2 flex-wrap">
        {[
          { v: '', l: 'Todos' },
          { v: 'bajo', l: 'Riesgo Bajo' },
          { v: 'medio', l: 'Riesgo Medio' },
          { v: 'alto', l: 'Riesgo Alto' },
        ].map(f => (
          <button key={f.v} onClick={() => setFiltro(f.v)}
            className={`btn btn-sm ${filtro === f.v ? 'btn-primary' : 'btn-secondary'}`}>
            {f.l}
          </button>
        ))}
      </div>

      <Table columns={columns} data={data.items} loading={loading}
        emptyMessage="No hay evaluaciones registradas" />
      <Pagination page={page} pages={data.pages} total={data.total}
        perPage={15} onPageChange={setPage} />
    </div>
  )
}
