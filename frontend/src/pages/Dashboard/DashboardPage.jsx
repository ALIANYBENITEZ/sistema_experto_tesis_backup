import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, ClipboardCheck, ShieldCheck, ShieldAlert, ShieldX, Ban } from 'lucide-react'
import { getSummary } from '../../api/reportApi'
import { getEvaluacionesRiesgo } from '../../api/scoringApi'
import ResultadoBadge from '../../components/ResultadoBadge'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'

const COLORS = {
  bajo: '#16a34a',
  medio: '#ca8a04',
  alto: '#ea580c',
  rechazado: '#dc2626',
}

// Etiqueta del gráfico de torta: muestra solo el porcentaje CENTRADO dentro de
// cada porción (evita que los nombres se encimen). Los nombres van en la leyenda.
const RADIAN = Math.PI / 180
function renderPieLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }) {
  if (percent < 0.05) return null // no mostrar porciones muy pequeñas
  const radius = innerRadius + (outerRadius - innerRadius) / 2
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  return (
    <text
      x={x}
      y={y}
      fill="#ffffff"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={12}
      fontWeight="bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [recents, setRecents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getSummary(),
      getEvaluacionesRiesgo({ per_page: 8 }),
    ])
      .then(([s, e]) => {
        setSummary(s.data.data)
        setRecents(e.data.data.items)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    )
  }

  const stats = summary ? [
    { label: 'Clientes Activos',    value: summary.total_clientes,     icon: Users,        color: 'bg-blue-50 text-blue-600' },
    { label: 'Evaluaciones',        value: summary.total_evaluaciones, icon: ClipboardCheck, color: 'bg-indigo-50 text-indigo-600' },
    { label: 'Bajo Riesgo',         value: summary.bajo_riesgo,        icon: ShieldCheck,  color: 'bg-green-50 text-green-600' },
    { label: 'Medio Riesgo',        value: summary.medio_riesgo,       icon: ShieldAlert,  color: 'bg-yellow-50 text-yellow-600' },
    { label: 'Alto Riesgo',         value: summary.alto_riesgo,        icon: ShieldX,      color: 'bg-orange-50 text-orange-600' },
    { label: 'Rechazados',          value: summary.rechazados,         icon: Ban,          color: 'bg-red-50 text-red-600' },
  ] : []

  const pieData = summary ? [
    { name: 'Bajo Riesgo',   value: summary.bajo_riesgo,   color: COLORS.bajo },
    { name: 'Medio Riesgo',  value: summary.medio_riesgo,  color: COLORS.medio },
    { name: 'Alto Riesgo',   value: summary.alto_riesgo,   color: COLORS.alto },
    { name: 'Rechazado',     value: summary.rechazados,    color: COLORS.rechazado },
  ].filter(d => d.value > 0) : []

  const barData = summary ? [
    { name: 'Bajo',      cantidad: summary.bajo_riesgo,   fill: COLORS.bajo },
    { name: 'Medio',     cantidad: summary.medio_riesgo,  fill: COLORS.medio },
    { name: 'Alto',      cantidad: summary.alto_riesgo,   fill: COLORS.alto },
    { name: 'Rechazado', cantidad: summary.rechazados,    fill: COLORS.rechazado },
  ] : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Resumen del sistema experto de scoring</p>
      </div>

      {/* Stats Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          {stats.map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card flex flex-col items-center text-center gap-2 p-4">
              <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <span className="text-2xl font-bold text-gray-900">{value}</span>
              <span className="text-xs text-gray-500 leading-tight">{label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pie Chart - Distribución de Riesgo */}
        <div className="card">
          <h2 className="font-semibold text-gray-900 mb-4">Distribución de Categorías de Riesgo</h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%" cy="45%"
                  innerRadius={55} outerRadius={95}
                  paddingAngle={3}
                  dataKey="value"
                  labelLine={false}
                  label={renderPieLabel}
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} evaluaciones`, name]} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-400 text-center py-16">Sin evaluaciones aún</p>
          )}
        </div>

        {/* Bar Chart - Cantidad por categoría */}
        <div className="card">
          <h2 className="font-semibold text-gray-900 mb-4">Evaluaciones por Nivel de Riesgo</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData} barSize={52}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="cantidad" radius={[6, 6, 0, 0]}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Últimas evaluaciones */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Últimas Evaluaciones de Riesgo</h2>
          <button onClick={() => navigate('/scoring')} className="text-xs text-primary-600 hover:underline">
            Ver todas
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-xs text-gray-500 uppercase">
                <th className="pb-2 pr-4">#</th>
                <th className="pb-2 pr-4">Cliente</th>
                <th className="pb-2 pr-4">Documento</th>
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Score</th>
                <th className="pb-2 pr-4">Categoría</th>
              </tr>
            </thead>
            <tbody>
              {recents.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center text-gray-400 py-8">Sin evaluaciones aún</td>
                </tr>
              )}
              {recents.map((ev) => (
                <tr
                  key={ev.id}
                  onClick={() => navigate(`/scoring/resultado/${ev.id}`)}
                  className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="py-3 pr-4 font-medium text-gray-700">{ev.id}</td>
                  <td className="py-3 pr-4 text-gray-800">{ev.cliente_nombre || `Cliente #${ev.cliente_id}`}</td>
                  <td className="py-3 pr-4 text-gray-600">{ev.num_doc || '—'}</td>
                  <td className="py-3 pr-4 text-gray-500">{ev.fecha_analisis ? new Date(ev.fecha_analisis).toLocaleDateString('es-PY') : '—'}</td>
                  <td className="py-3 pr-4 font-bold text-gray-800">
                    {ev.score_final}/{ev.score_maximo}
                  </td>
                  <td className="py-3"><ResultadoBadge resultado={ev.categoria_riesgo} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
