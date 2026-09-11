import { useState, useEffect, useCallback } from 'react'
import { ScrollText, Search, Filter, ChevronLeft, ChevronRight, RefreshCw, Eye, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { getAuditoria, getAuditoriaFiltros } from '../../api/auditoriaApi'
import { useAuth } from '../../context/AuthContext'

const TIPO_COLORS = {
  AUTENTICACION: 'bg-blue-100 text-blue-700',
  SEGURIDAD:     'bg-purple-100 text-purple-700',
  USUARIOS:      'bg-indigo-100 text-indigo-700',
  EMPRESAS:      'bg-teal-100 text-teal-700',
  CLIENTES:      'bg-green-100 text-green-700',
  EVALUACIONES:  'bg-amber-100 text-amber-700',
  FACTURACION:   'bg-pink-100 text-pink-700',
}

function fmtFecha(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('es-PY', { dateStyle: 'short', timeStyle: 'medium' })
}

function parseJson(str) {
  if (!str) return null
  try { return JSON.parse(str) } catch { return str }
}

export default function AuditoriaPage() {
  const { user } = useAuth()
  const esPropietario = user?.rol === 'propietario' && user?.id_empresa === 0

  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 1 })
  const [loading, setLoading] = useState(false)
  const [opciones, setOpciones] = useState({ tipos_evento: [], resultados: [], acciones: [], modulos: [], empresas: [] })
  const [detalle, setDetalle] = useState(null)

  const [filtros, setFiltros] = useState({
    fecha_from: '', fecha_to: '', tipo_evento: '', accion: '',
    modulo: '', resultado: '', id_empresa: '', search: '',
  })
  const [page, setPage] = useState(1)

  useEffect(() => {
    getAuditoriaFiltros()
      .then(setOpciones)
      .catch(() => {})
  }, [])

  const cargar = useCallback(() => {
    setLoading(true)
    const params = { page, per_page: 25 }
    Object.entries(filtros).forEach(([k, v]) => { if (v) params[k] = v })
    getAuditoria(params)
      .then(setData)
      .catch(() => toast.error('No se pudo cargar la auditoría'))
      .finally(() => setLoading(false))
  }, [page, filtros])

  useEffect(() => { cargar() }, [cargar])

  const aplicarFiltros = () => { setPage(1); cargar() }
  const limpiar = () => {
    setFiltros({ fecha_from: '', fecha_to: '', tipo_evento: '', accion: '', modulo: '', resultado: '', id_empresa: '', search: '' })
    setPage(1)
  }

  const setF = (k, v) => setFiltros((prev) => ({ ...prev, [k]: v }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-primary-100 rounded-lg">
          <ScrollText className="h-6 w-6 text-primary-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Auditoría del Sistema</h1>
          <p className="text-gray-500 text-sm">Bitácora de eventos y acciones realizadas</p>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-4">
        <div className="flex items-center gap-2 text-gray-700 font-medium text-sm">
          <Filter className="h-4 w-4" /> Filtros
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Desde</label>
            <input type="date" value={filtros.fecha_from} onChange={(e) => setF('fecha_from', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Hasta</label>
            <input type="date" value={filtros.fecha_to} onChange={(e) => setF('fecha_to', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Tipo de evento</label>
            <select value={filtros.tipo_evento} onChange={(e) => setF('tipo_evento', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todos</option>
              {opciones.tipos_evento.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Resultado</label>
            <select value={filtros.resultado} onChange={(e) => setF('resultado', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todos</option>
              {opciones.resultados.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Acción</label>
            <select value={filtros.accion} onChange={(e) => setF('accion', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todas</option>
              {opciones.acciones.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Módulo</label>
            <select value={filtros.modulo} onChange={(e) => setF('modulo', e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Todos</option>
              {opciones.modulos.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          {esPropietario && (
            <div>
              <label className="block text-xs text-gray-500 mb-1">Empresa</label>
              <select value={filtros.id_empresa} onChange={(e) => setF('id_empresa', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="">Todas</option>
                {(opciones.empresas || []).map((e) => <option key={e.id} value={e.id}>{e.nombre}</option>)}
              </select>
            </div>
          )}
          <div>
            <label className="block text-xs text-gray-500 mb-1">Búsqueda</label>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
              <input type="text" value={filtros.search} onChange={(e) => setF('search', e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && aplicarFiltros()}
                placeholder="Usuario, acción, entidad..."
                className="w-full border border-gray-300 rounded-lg pl-8 pr-3 py-2 text-sm" />
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={aplicarFiltros}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
            Aplicar filtros
          </button>
          <button onClick={limpiar}
            className="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50">
            Limpiar
          </button>
          <button onClick={cargar}
            className="px-3 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 flex items-center gap-1.5">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> Actualizar
          </button>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-left">
              <tr>
                <th className="px-4 py-3 font-medium">Fecha</th>
                <th className="px-4 py-3 font-medium">Usuario</th>
                <th className="px-4 py-3 font-medium">Tipo</th>
                <th className="px-4 py-3 font-medium">Acción</th>
                <th className="px-4 py-3 font-medium">Entidad</th>
                {esPropietario && <th className="px-4 py-3 font-medium">Empresa</th>}
                <th className="px-4 py-3 font-medium">Resultado</th>
                <th className="px-4 py-3 font-medium text-center">Ver</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.items.length === 0 && !loading && (
                <tr><td colSpan={esPropietario ? 8 : 7} className="px-4 py-8 text-center text-gray-400">
                  No hay eventos que coincidan con los filtros
                </td></tr>
              )}
              {data.items.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{fmtFecha(a.fecha)}</td>
                  <td className="px-4 py-3 text-gray-800">{a.usuario_nombre || '—'}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${TIPO_COLORS[a.tipo_evento] || 'bg-gray-100 text-gray-600'}`}>
                      {a.tipo_evento}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{a.accion}</td>
                  <td className="px-4 py-3 text-gray-500">{a.entidad || '—'}{a.registro_id ? ` #${a.registro_id}` : ''}</td>
                  {esPropietario && <td className="px-4 py-3 text-gray-500">{a.empresa_nombre}</td>}
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${a.resultado === 'FALLO' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                      {a.resultado}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button onClick={() => setDetalle(a)} className="text-primary-600 hover:text-primary-800">
                      <Eye className="h-4 w-4 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 text-sm text-gray-600">
          <span>{data.total} evento(s) — página {data.page} de {data.pages || 1}</span>
          <div className="flex gap-2">
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}
              className="p-1.5 border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button disabled={page >= (data.pages || 1)} onClick={() => setPage((p) => p + 1)}
              className="p-1.5 border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Modal detalle */}
      {detalle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setDetalle(null)}>
          <div className="bg-white rounded-xl w-full max-w-lg max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-800">Detalle del evento #{detalle.id}</h3>
              <button onClick={() => setDetalle(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-5 space-y-3 text-sm">
              <DetRow label="Fecha" value={fmtFecha(detalle.fecha)} />
              <DetRow label="Usuario" value={detalle.usuario_nombre} />
              <DetRow label="Tipo de evento" value={detalle.tipo_evento} />
              <DetRow label="Acción" value={detalle.accion} />
              <DetRow label="Módulo" value={detalle.modulo} />
              <DetRow label="Entidad" value={detalle.entidad} />
              <DetRow label="Registro ID" value={detalle.registro_id} />
              <DetRow label="Empresa" value={detalle.empresa_nombre} />
              <DetRow label="Resultado" value={detalle.resultado} />
              <DetRow label="IP" value={detalle.ip} />
              <JsonBlock label="Información adicional" value={parseJson(detalle.info_adicional)} />
              <JsonBlock label="Valores anteriores" value={parseJson(detalle.valores_anteriores)} />
              <JsonBlock label="Valores nuevos" value={parseJson(detalle.valores_nuevos)} />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function DetRow({ label, value }) {
  if (!value) return null
  return (
    <div className="flex gap-3">
      <span className="w-36 flex-shrink-0 text-gray-500">{label}</span>
      <span className="text-gray-800 break-all">{value}</span>
    </div>
  )
}

function JsonBlock({ label, value }) {
  if (!value) return null
  return (
    <div>
      <p className="text-gray-500 mb-1">{label}</p>
      <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
      </pre>
    </div>
  )
}
