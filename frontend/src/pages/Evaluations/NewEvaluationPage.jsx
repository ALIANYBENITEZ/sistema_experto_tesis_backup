import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { getClients } from '../../api/clientApi'
import { coreGetModelos, coreGetModelo, coreEvaluar, coreVerificarListaNegra } from '../../api/coreApi'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

export default function NewEvaluationPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [modelos, setModelos] = useState([])
  const [modeloId, setModeloId] = useState('')
  const [factores, setFactores] = useState([])
  const [clienteId, setClienteId] = useState('')
  const [clienteInfo, setClienteInfo] = useState(null)
  const [tipoPers, setTipoPers] = useState('PF')

  // Búsqueda de cliente
  const [busqueda, setBusqueda] = useState({ num_doc: '', nombre: '', apellido: '' })
  const [resultados, setResultados] = useState([])
  const [buscando, setBuscando] = useState(false)
  const [listaNegra, setListaNegra] = useState(null)

  const { register, handleSubmit, setValue, formState: { isSubmitting } } = useForm()

  // Cargar modelos al montar
  useEffect(() => {
    coreGetModelos().then(r => {
      const activos = r.data.data.filter(m => m.activo)
      setModelos(activos)
      if (activos.length === 1) {
        setModeloId(String(activos[0].id))
      }
    }).catch(() => {})
  }, [])

  // Cargar factores al seleccionar modelo
  useEffect(() => {
    if (!modeloId) { setFactores([]); return }
    coreGetModelo(modeloId).then(r => {
      const data = r.data.data
      // Filtrar por tipo de persona
      const filtered = (data.factores || []).filter(f =>
        f.tipo_persona === 'AMBOS' || f.tipo_persona === tipoPers
      )
      setFactores(filtered)
    }).catch(() => {})
  }, [modeloId, tipoPers])

  // Búsqueda en tiempo real
  useEffect(() => {
    const { num_doc, nombre, apellido } = busqueda
    if (!num_doc && !nombre && !apellido) { setResultados([]); return }
    const timer = setTimeout(async () => {
      setBuscando(true)
      try {
        const params = { per_page: 10 }
        if (num_doc) params.num_doc = num_doc
        if (nombre) params.nombre = nombre
        if (apellido) params.apellido = apellido
        const r = await getClients(params)
        setResultados(r.data.data.items)
      } catch {}
      finally { setBuscando(false) }
    }, 300)
    return () => clearTimeout(timer)
  }, [busqueda])

  const seleccionarCliente = async (cliente) => {
    setClienteId(String(cliente.id))
    setClienteInfo(cliente)
    setResultados([])
    setBusqueda({ num_doc: '', nombre: '', apellido: '' })

    // Auto-detectar tipo de persona según tipo de documento
    const tipoDoc = (cliente.tipo_doc || '').toUpperCase()
    if (tipoDoc === 'RUC') {
      setTipoPers('PJ')
    } else {
      setTipoPers('PF')
    }

    // Verificar lista negra automáticamente
    try {
      const r = await coreVerificarListaNegra(cliente.id)
      setListaNegra(r.data.data)
    } catch {
      setListaNegra(null)
    }
  }

  const limpiarCliente = () => { setClienteId(''); setClienteInfo(null); setListaNegra(null) }

  const onSubmit = async (formData) => {
    if (!clienteId) { toast.error('Seleccione un cliente'); return }
    if (!modeloId) { toast.error('Seleccione un modelo'); return }

    // Construir datos por factor
    const datos = {}
    factores.forEach(f => {
      const v = formData[f.codigo]
      if (v !== '' && v !== undefined && v !== null) {
        if (f.tipo_dato === 'numerico' || f.tipo_dato === 'porcentaje') {
          datos[f.codigo] = parseFloat(v)
        } else if (f.tipo_dato === 'booleano') {
          datos[f.codigo] = v === 'true' || v === true
        } else {
          datos[f.codigo] = v
        }
      }
    })

    // Calcular relación cuota/ingreso automáticamente
    if (formData.monto_cuota && datos.ingresos_mensuales) {
      const cuota = parseFloat(formData.monto_cuota)
      const ingresos = datos.ingresos_mensuales
      if (ingresos > 0) {
        datos.relacion_cuota_ingreso = Math.round((cuota / ingresos) * 100 * 100) / 100
      }
    }

    try {
      const r = await coreEvaluar({
        cliente_id: parseInt(clienteId),
        modelo_id: parseInt(modeloId),
        tipo_persona: tipoPers,
        datos,
      })
      toast.success('Evaluación completada')
      navigate(`/evaluations/resultado/${r.data.data.id}`)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al evaluar')
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Nueva Evaluación de Riesgo</h1>
        <p className="text-gray-500 text-sm">Evaluación basada en el Core de Scoring Comercial</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

        {/* Buscar cliente */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Buscar Cliente</h2>
          {!clienteInfo ? (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label text-xs">CI / RUC</label>
                  <input type="text" className="input text-sm" placeholder="Número de documento"
                    value={busqueda.num_doc} onChange={e => setBusqueda(b => ({ ...b, num_doc: e.target.value }))} />
                </div>
                <div>
                  <label className="label text-xs">Nombre</label>
                  <input type="text" className="input text-sm" placeholder="Nombre"
                    value={busqueda.nombre} onChange={e => setBusqueda(b => ({ ...b, nombre: e.target.value }))} />
                </div>
                <div>
                  <label className="label text-xs">Apellido</label>
                  <input type="text" className="input text-sm" placeholder="Apellido"
                    value={busqueda.apellido} onChange={e => setBusqueda(b => ({ ...b, apellido: e.target.value }))} />
                </div>
              </div>
              {(resultados.length > 0 || buscando) && (
                <div className="mt-3 border border-gray-200 rounded-lg overflow-hidden max-h-60 overflow-y-auto shadow-sm">
                  {buscando && <div className="px-4 py-3 text-sm text-gray-500 flex items-center gap-2"><span className="h-3 w-3 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />Buscando...</div>}
                  {!buscando && resultados.length === 0 && (busqueda.num_doc || busqueda.nombre || busqueda.apellido) && (
                    <div className="px-4 py-3 text-sm text-gray-400">No se encontraron clientes</div>
                  )}
                  {resultados.map(c => (
                    <div key={c.id} onClick={() => seleccionarCliente(c)}
                      className="flex items-center justify-between px-4 py-3 border-b border-gray-100 last:border-b-0 hover:bg-blue-50 cursor-pointer transition-colors">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{c.nombre} {c.apellido || ''}</p>
                        <p className="text-xs text-gray-500">{c.tipo_doc}: {c.num_doc}</p>
                      </div>
                      <span className="text-xs text-primary-600 font-medium">Seleccionar</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">
                  {clienteInfo.nombre?.[0]}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{clienteInfo.nombre} {clienteInfo.apellido || ''}</p>
                  <p className="text-sm text-gray-500">{clienteInfo.tipo_doc}: {clienteInfo.num_doc}</p>
                </div>
              </div>
              <button type="button" onClick={limpiarCliente} className="text-xs text-red-600 hover:underline">Cambiar</button>
            </div>
          )}

          {/* Resultado verificación lista negra */}
          {listaNegra && clienteInfo && (
            <div className={`mt-4 rounded-lg border p-4 ${
              listaNegra.nivel_alerta === 'ninguno'
                ? 'bg-green-50 border-green-200'
                : listaNegra.nivel_alerta === 'posible'
                ? 'bg-yellow-50 border-yellow-300'
                : 'bg-red-50 border-red-300'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-lg ${
                  listaNegra.nivel_alerta === 'ninguno' ? '✅' :
                  listaNegra.nivel_alerta === 'posible' ? '⚠️' : '🚨'
                }`}>
                  {listaNegra.nivel_alerta === 'ninguno' ? '✅' :
                   listaNegra.nivel_alerta === 'posible' ? '⚠️' : '🚨'}
                </span>
                <p className={`font-semibold text-sm ${
                  listaNegra.nivel_alerta === 'ninguno' ? 'text-green-800' :
                  listaNegra.nivel_alerta === 'posible' ? 'text-yellow-800' : 'text-red-800'
                }`}>
                  {listaNegra.nivel_alerta === 'ninguno'
                    ? 'Cliente NO aparece en listas de sanciones (ONU/OFAC)'
                    : listaNegra.nivel_alerta === 'posible'
                    ? 'POSIBLE coincidencia en listas de sanciones'
                    : 'ALERTA: Coincidencia CONFIRMADA en listas de sanciones'}
                </p>
              </div>
              {listaNegra.coincidencias?.length > 0 && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs font-semibold text-gray-600">Coincidencias encontradas:</p>
                  {listaNegra.coincidencias.map((c, i) => (
                    <div key={i} className="text-xs text-gray-700 pl-4 border-l-2 border-gray-300">
                      <span className="font-medium">{c.nombre} {c.apellido}</span>
                      {c.cargo && <span className="text-gray-500"> — {c.cargo}</span>}
                      <span className="text-gray-400 ml-2">({c.tipo_match}, confianza: {c.confianza}%)</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Configuración */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Configuración</h2>
          {user?.empresa_nombre && (
            <div className="mb-4 px-3 py-2 bg-indigo-50 border border-indigo-200 rounded-lg inline-block">
              <span className="text-xs text-indigo-600">Empresa: </span>
              <span className="text-sm font-semibold text-indigo-900">{user.empresa_nombre}</span>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Modelo de scoring *</label>
              <select className="input" value={modeloId} onChange={e => setModeloId(e.target.value)}>
                <option value="">— Seleccionar —</option>
                {modelos.map(m => <option key={m.id} value={m.id}>{m.nombre} v{m.version}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Tipo de persona</label>
              <input type="text" className="input bg-gray-100" readOnly
                value={tipoPers === 'PF' ? 'Persona Física' : 'Persona Jurídica'} />
              <p className="text-xs text-gray-400 mt-1">Detectado automáticamente según tipo de documento</p>
            </div>
          </div>
        </div>

        {/* Factores */}
        {factores.length > 0 && (
          <div className="card">
            <h2 className="font-semibold text-gray-800 mb-1">Factores de Evaluación</h2>
            <p className="text-xs text-gray-500 mb-4">Complete los valores para cada factor.</p>

            {/* Principales */}
            {factores.filter(f => f.categoria === 'principal').length > 0 && (
              <div className="mb-6">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-3">Factores Principales</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {factores.filter(f => f.categoria === 'principal').map(f => (
                    <FactorInput key={f.codigo} factor={f} register={register} />
                  ))}
                </div>
              </div>
            )}

            {/* Complementarios */}
            {factores.filter(f => f.categoria === 'complementario').length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase mb-3">Factores Complementarios</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {factores.filter(f => f.categoria === 'complementario').map(f => (
                    <FactorInput key={f.codigo} factor={f} register={register} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <button type="button" onClick={() => navigate('/evaluations')} className="btn-secondary">Cancelar</button>
          <button type="submit" className="btn-primary px-6" disabled={isSubmitting}>
            {isSubmitting
              ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2 inline-block" />Evaluando…</>
              : 'Ejecutar Evaluación'}
          </button>
        </div>
      </form>
    </div>
  )
}

// Componente para renderizar un factor según su tipo
function FactorInput({ factor, register }) {
  const f = factor

  // El factor relacion_cuota_ingreso se captura como monto de cuota
  if (f.codigo === 'relacion_cuota_ingreso') {
    return (
      <div className="border border-gray-200 rounded-lg p-3">
        <label className="label text-xs mb-1">
          Monto de Cuota Solicitada (Gs) {f.obligatorio && <span className="text-red-500">*</span>}
        </label>
        <p className="text-xs text-gray-400 mb-2">El sistema calculará automáticamente el % sobre los ingresos</p>
        <input type="number" step="any" min="0"
          className="input text-sm" placeholder="Ej: 2500000"
          {...register('monto_cuota')} />
      </div>
    )
  }

  return (
    <div className="border border-gray-200 rounded-lg p-3">
      <label className="label text-xs mb-1">
        {f.nombre} {f.obligatorio && <span className="text-red-500">*</span>}
      </label>
      {f.descripcion && <p className="text-xs text-gray-400 mb-2">{f.descripcion}</p>}

      {(f.tipo_dato === 'numerico' || f.tipo_dato === 'porcentaje') && (
        <input type="number" step="any" min="0" max={f.tipo_dato === 'porcentaje' ? 100 : undefined}
          className="input text-sm" placeholder={f.tipo_dato === 'porcentaje' ? '0 - 100' : '0'}
          {...register(f.codigo)} />
      )}

      {f.tipo_dato === 'booleano' && (
        <select className="input text-sm" {...register(f.codigo)}>
          <option value="">— Seleccionar —</option>
          <option value="false">No</option>
          <option value="true">Sí</option>
        </select>
      )}

      {(f.tipo_dato === 'catalogo' || f.tipo_dato === 'texto') && f.catalogo && (
        <select className="input text-sm" {...register(f.codigo)}>
          <option value="">— Seleccionar —</option>
          {f.catalogo.map(c => <option key={c.valor} value={c.valor}>{c.etiqueta}</option>)}
        </select>
      )}

      {f.tipo_dato === 'texto' && !f.catalogo && (
        <input type="text" className="input text-sm" {...register(f.codigo)} />
      )}
    </div>
  )
}
