import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { getClients } from '../../api/clientApi'
import { getMotores, getHistorial, evaluar } from '../../api/scoringApi'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

const CAMPOS = [
  { key: 'ingresos_mensuales',    label: 'Ingresos Mensuales (Gs)',       tipo: 'number', placeholder: 'Ej: 5000000' },
  { key: 'edad',                  label: 'Edad (años)',                   tipo: 'number', placeholder: 'Ej: 35' },
  { key: 'nivel_endeudamiento',   label: 'Nivel de Endeudamiento (%)',    tipo: 'number', placeholder: 'Ej: 25.5' },
  { key: 'meses_empleo_actual',   label: 'Antigüedad Laboral (meses)',    tipo: 'number', placeholder: 'Ej: 12' },
  { key: 'cantidad_atrasos',      label: 'Cantidad de Atrasos',           tipo: 'number', placeholder: 'Ej: 0' },
  { key: 'deuda_total_sistema',   label: 'Deuda Total en Sistema (Gs)',   tipo: 'number', placeholder: 'Ej: 10000000' },
  { key: 'score_externo',         label: 'Score Crediticio Externo',      tipo: 'number', placeholder: 'Ej: 650' },
  { key: 'historial_pagos',       label: 'Historial de Pagos',            tipo: 'select',
    opciones: [
      { v: 'bueno',         l: 'Bueno' },
      { v: 'regular',       l: 'Regular' },
      { v: 'malo',          l: 'Malo' },
      { v: 'sin_historial', l: 'Sin historial' },
    ]
  },
  { key: 'en_lista_negra',        label: 'En Lista Negra / OFAC',         tipo: 'select',
    opciones: [{ v: 'false', l: 'No' }, { v: 'true', l: 'Sí' }]
  },
  { key: 'tipo_empleo',           label: 'Tipo de Empleo',                tipo: 'select',
    opciones: [
      { v: 'dependiente',   l: 'Dependiente' },
      { v: 'independiente', l: 'Independiente' },
      { v: 'desempleado',   l: 'Desempleado' },
    ]
  },
  { key: 'referencias_personales',label: 'Referencias Personales',        tipo: 'select',
    opciones: [
      { v: 'buenas',         l: 'Buenas' },
      { v: 'regulares',      l: 'Regulares' },
      { v: 'malas',          l: 'Malas' },
      { v: 'no_verificadas', l: 'No verificadas' },
    ]
  },
]

export default function EvaluarClientePage() {
  const navigate        = useNavigate()
  const { user }        = useAuth()
  const [motores,   setMotores]   = useState([])
  const [clienteId, setClienteId] = useState('')
  const [motorId,   setMotorId]   = useState('')
  const [clienteInfo, setClienteInfo] = useState(null)

  // Búsqueda de cliente
  const [busqueda, setBusqueda] = useState({ num_doc: '', nombre: '', apellido: '' })
  const [resultados, setResultados] = useState([])
  const [buscando, setBuscando] = useState(false)

  const { register, handleSubmit, setValue, formState: { isSubmitting } } = useForm()

  useEffect(() => {
    getMotores().then(m => {
      const activos = m.data.data.filter(x => x.activo)
      setMotores(activos)
      if (activos.length === 1) setMotorId(String(activos[0].id))
    })
  }, [])

  // Búsqueda en tiempo real al escribir
  useEffect(() => {
    const { num_doc, nombre, apellido } = busqueda
    if (!num_doc && !nombre && !apellido) {
      setResultados([])
      return
    }
    const timer = setTimeout(async () => {
      setBuscando(true)
      try {
        const params = { per_page: 10 }
        if (num_doc) params.num_doc = num_doc
        if (nombre)  params.nombre = nombre
        if (apellido) params.apellido = apellido
        const r = await getClients(params)
        setResultados(r.data.data.items)
      } catch { /* ignore */ }
      finally { setBuscando(false) }
    }, 300) // debounce 300ms
    return () => clearTimeout(timer)
  }, [busqueda])

  // Seleccionar un cliente de los resultados
  const seleccionarCliente = async (cliente) => {
    setClienteId(String(cliente.id))
    setClienteInfo(cliente)
    setResultados([])
    setBusqueda({ num_doc: '', nombre: '', apellido: '' })

    // Calcular edad automáticamente
    if (cliente.fecha_nacimiento) {
      const hoy = new Date()
      const fnac = new Date(cliente.fecha_nacimiento)
      let edad = hoy.getFullYear() - fnac.getFullYear()
      const m = hoy.getMonth() - fnac.getMonth()
      if (m < 0 || (m === 0 && hoy.getDate() < fnac.getDate())) edad--
      setValue('edad', String(edad))
    }

    // Pre-cargar historial crediticio
    try {
      const r = await getHistorial(cliente.id)
      const h = r.data.data
      if (h) {
        CAMPOS.forEach(c => {
          if (h[c.key] !== null && h[c.key] !== undefined) {
            setValue(c.key, String(h[c.key]))
          }
        })
      }
    } catch { /* sin historial previo */ }
  }

  // Limpiar selección
  const limpiarCliente = () => {
    setClienteId('')
    setClienteInfo(null)
  }

  const onSubmit = async (formData) => {
    if (!clienteId) { toast.error('Seleccione un cliente'); return }
    if (!motorId)   { toast.error('Seleccione un motor de reglas'); return }

    // Construir hechos
    const hechos = {}
    CAMPOS.forEach(c => {
      const v = formData[c.key]
      if (v !== '' && v !== undefined && v !== null) {
        hechos[c.key] = c.tipo === 'number' ? parseFloat(v) : v
      }
    })

    // Construir datos de operación inmobiliaria
    const operacion = {}
    if (formData.tipo_propiedad) operacion.tipo_propiedad = formData.tipo_propiedad
    if (formData.valor_propiedad) operacion.valor_propiedad = parseFloat(formData.valor_propiedad)
    if (formData.monto_solicitado) operacion.monto_solicitado = parseFloat(formData.monto_solicitado)
    if (formData.plazo_meses) operacion.plazo_meses = parseInt(formData.plazo_meses)
    if (formData.ubicacion) operacion.ubicacion = formData.ubicacion
    if (formData.destino) operacion.destino = formData.destino

    try {
      const r = await evaluar({
        cliente_id:    parseInt(clienteId),
        motor_id:      parseInt(motorId),
        hechos,
        operacion: operacion.tipo_propiedad ? operacion : undefined,
        observaciones: formData.observaciones || '',
      })
      toast.success('Evaluación completada')
      navigate(`/scoring/resultado/${r.data.data.id}`)
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al evaluar')
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Nueva Evaluación de Riesgo</h1>
        <p className="text-gray-500 text-sm">Complete los datos del cliente para ejecutar el motor de reglas</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">

        {/* Búsqueda de cliente */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Buscar Cliente</h2>
          {!clienteInfo ? (
            <div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="label text-xs">CI / RUC</label>
                  <input
                    type="text" className="input text-sm"
                    placeholder="Número de documento"
                    value={busqueda.num_doc}
                    onChange={e => setBusqueda(b => ({ ...b, num_doc: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="label text-xs">Nombre</label>
                  <input
                    type="text" className="input text-sm"
                    placeholder="Nombre del cliente"
                    value={busqueda.nombre}
                    onChange={e => setBusqueda(b => ({ ...b, nombre: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="label text-xs">Apellido</label>
                  <input
                    type="text" className="input text-sm"
                    placeholder="Apellido del cliente"
                    value={busqueda.apellido}
                    onChange={e => setBusqueda(b => ({ ...b, apellido: e.target.value }))}
                  />
                </div>
              </div>

              {/* Panel de resultados en tiempo real */}
              {(resultados.length > 0 || buscando) && (
                <div className="mt-3 border border-gray-200 rounded-lg overflow-hidden max-h-60 overflow-y-auto shadow-sm">
                  {buscando && (
                    <div className="flex items-center gap-2 px-4 py-3 text-sm text-gray-500">
                      <span className="h-3 w-3 animate-spin rounded-full border-2 border-primary-600 border-t-transparent" />
                      Buscando...
                    </div>
                  )}
                  {!buscando && resultados.length === 0 && (busqueda.num_doc || busqueda.nombre || busqueda.apellido) && (
                    <div className="px-4 py-3 text-sm text-gray-400">No se encontraron clientes</div>
                  )}
                  {resultados.map(c => (
                    <div key={c.id}
                      onClick={() => seleccionarCliente(c)}
                      className="flex items-center justify-between px-4 py-3 border-b border-gray-100 last:border-b-0 hover:bg-blue-50 cursor-pointer transition-colors">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{c.nombre} {c.apellido || ''}</p>
                        <p className="text-xs text-gray-500">{c.tipo_doc}: {c.num_doc} · {c.email || 'Sin email'}</p>
                      </div>
                      <span className="text-xs text-primary-600 font-medium">Seleccionar</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            /* Cliente seleccionado */
            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-bold">
                  {clienteInfo.nombre?.[0]}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{clienteInfo.nombre} {clienteInfo.apellido || ''}</p>
                  <p className="text-sm text-gray-500">{clienteInfo.tipo_doc}: {clienteInfo.num_doc} · {clienteInfo.email || 'Sin email'}</p>
                </div>
              </div>
              <button type="button" onClick={limpiarCliente} className="text-xs text-red-600 hover:underline">
                Cambiar cliente
              </button>
            </div>
          )}
        </div>

        {/* Motor de reglas */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Motor de reglas</h2>
          {user?.empresa_nombre && (
            <div className="mb-4 px-3 py-2 bg-indigo-50 border border-indigo-200 rounded-lg">
              <p className="text-xs text-indigo-600">Empresa</p>
              <p className="font-semibold text-indigo-900">{user.empresa_nombre}</p>
            </div>
          )}
          <div>
            <label className="label">Motor de reglas *</label>
            <select className="input" value={motorId} onChange={e => setMotorId(e.target.value)}>
              <option value="">— Seleccionar motor —</option>
              {motores.map(m => (
                <option key={m.id} value={m.id}>{m.nombre} v{m.version}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Datos del cliente */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-1">Datos para evaluación</h2>
          <p className="text-xs text-gray-500 mb-4">
            Si el cliente tiene historial registrado, los campos se pre-llenan automáticamente.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {CAMPOS.map(campo => (
              <div key={campo.key}>
                <label className="label text-xs">{campo.label}</label>
                {campo.tipo === 'select' ? (
                  <select className="input text-sm" {...register(campo.key)}>
                    <option value="">— No especificado —</option>
                    {campo.opciones.map(o => (
                      <option key={o.v} value={o.v}>{o.l}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="number" step="any" min="0"
                    className="input text-sm"
                    placeholder={campo.placeholder}
                    {...register(campo.key)}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Datos de la operación inmobiliaria */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-1">Datos de la Operación Inmobiliaria</h2>
          <p className="text-xs text-gray-500 mb-4">
            Información de la propiedad que el cliente desea adquirir o alquilar.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <div>
              <label className="label text-xs">Tipo de propiedad</label>
              <select className="input text-sm" {...register('tipo_propiedad')}>
                <option value="">— Seleccionar —</option>
                <option value="casa">Casa</option>
                <option value="departamento">Departamento</option>
                <option value="terreno">Terreno</option>
                <option value="local_comercial">Local Comercial</option>
                <option value="oficina">Oficina</option>
              </select>
            </div>
            <div>
              <label className="label text-xs">Valor de la propiedad (Gs)</label>
              <input type="number" step="any" min="0" className="input text-sm"
                placeholder="Ej: 500000000"
                {...register('valor_propiedad')} />
            </div>
            <div>
              <label className="label text-xs">Monto solicitado (Gs)</label>
              <input type="number" step="any" min="0" className="input text-sm"
                placeholder="Ej: 350000000"
                {...register('monto_solicitado')} />
            </div>
            <div>
              <label className="label text-xs">Plazo (meses)</label>
              <input type="number" min="1" className="input text-sm"
                placeholder="Ej: 120"
                {...register('plazo_meses')} />
            </div>
            <div>
              <label className="label text-xs">Ubicación</label>
              <input type="text" className="input text-sm"
                placeholder="Ej: Asunción, Barrio"
                {...register('ubicacion')} />
            </div>
            <div>
              <label className="label text-xs">Destino</label>
              <select className="input text-sm" {...register('destino')}>
                <option value="">— Seleccionar —</option>
                <option value="vivienda">Vivienda</option>
                <option value="inversion">Inversión</option>
                <option value="comercial">Comercial</option>
              </select>
            </div>
          </div>
        </div>

        {/* Observaciones */}
        <div className="card">
          <label className="label">Observaciones</label>
          <textarea className="input resize-none h-20"
            placeholder="Notas adicionales sobre la evaluación..."
            {...register('observaciones')} />
        </div>

        <div className="flex justify-end gap-3">
          <button type="button" onClick={() => navigate('/evaluations')} className="btn-secondary">
            Cancelar
          </button>
          <button type="submit" className="btn-primary px-6" disabled={isSubmitting}>
            {isSubmitting
              ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2" />Evaluando…</>
              : 'Ejecutar Evaluación'
            }
          </button>
        </div>
      </form>
    </div>
  )
}
