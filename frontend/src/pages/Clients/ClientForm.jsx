import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { createClient, updateClient, getPaises, getDepartamentos, getCiudades } from '../../api/clientApi'
import toast from 'react-hot-toast'

export default function ClientForm({ client, onSaved, onCancel }) {
  const isEdit = Boolean(client)
  const { register, handleSubmit, setValue, formState: { errors, isSubmitting } } = useForm({
    defaultValues: client ?? {
      tipo_doc: 'CI',
      num_doc: '', nombre: '', apellido: '', email: '',
      telefono: '', direccion: '', fecha_nacimiento: '',
      nacionalidad: '', id_ciudad: '',
    },
  })

  const [paises, setPaises] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [ciudades, setCiudades] = useState([])
  const [paisId, setPaisId] = useState(client?.nacionalidad || '')
  const [deptoId, setDeptoId] = useState('')
  const [esParaguay, setEsParaguay] = useState(false)

  // Cargar países al montar
  useEffect(() => {
    getPaises().then(r => setPaises(r.data.data)).catch(() => {})
  }, [])

  // Detectar si es Paraguay y cargar departamentos
  useEffect(() => {
    const esPy = paisId === 'PY'
    setEsParaguay(esPy)
    if (esPy) {
      getDepartamentos().then(r => setDepartamentos(r.data.data)).catch(() => {})
    } else {
      setDepartamentos([])
      setCiudades([])
      setDeptoId('')
      setValue('id_ciudad', '')
    }
  }, [paisId])

  // Si es edición y tiene ciudad, buscar su departamento
  useEffect(() => {
    if (isEdit && client?.id_ciudad && departamentos.length > 0) {
      departamentos.forEach(d => {
        getCiudades(d.id).then(cr => {
          const found = cr.data.data.find(c => c.id === client.id_ciudad)
          if (found) {
            setDeptoId(String(d.id))
            setCiudades(cr.data.data)
          }
        }).catch(() => {})
      })
    }
  }, [isEdit, client, departamentos])

  // Al cambiar país
  const handlePaisChange = (e) => {
    const id = e.target.value
    setPaisId(id)
    setValue('nacionalidad', id)
    setDeptoId('')
    setCiudades([])
    setValue('id_ciudad', '')
  }

  // Al cambiar departamento → cargar ciudades
  const handleDeptoChange = (e) => {
    const id = e.target.value
    setDeptoId(id)
    setCiudades([])
    setValue('id_ciudad', '')
    if (id) {
      getCiudades(id).then(r => setCiudades(r.data.data)).catch(() => {})
    }
  }

  const onSubmit = async (data) => {
    try {
      if (isEdit) {
        await updateClient(client.id, data)
        toast.success('Cliente actualizado')
      } else {
        await createClient(data)
        toast.success('Cliente registrado')
      }
      onSaved()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al guardar')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Tipo documento</label>
          <select className="input" {...register('tipo_doc', { required: 'Requerido' })}>
            <option value="CI">CI</option>
            <option value="RUC">RUC</option>
            <option value="PAS">Pasaporte</option>
          </select>
        </div>
        <div>
          <label className="label">N° Documento</label>
          <input
            className={`input ${errors.num_doc ? 'border-red-400' : ''}`}
            disabled={isEdit}
            {...register('num_doc', { required: 'Requerido' })}
          />
          {errors.num_doc && <p className="text-xs text-red-600 mt-1">{errors.num_doc.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Nombre *</label>
          <input className={`input ${errors.nombre ? 'border-red-400' : ''}`} {...register('nombre', { required: 'Requerido' })} />
          {errors.nombre && <p className="text-xs text-red-600 mt-1">{errors.nombre.message}</p>}
        </div>
        <div>
          <label className="label">Apellido</label>
          <input className="input" {...register('apellido')} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Email</label>
          <input type="email" className="input" {...register('email')} />
        </div>
        <div>
          <label className="label">Teléfono</label>
          <input className="input" {...register('telefono')} />
        </div>
      </div>

      {/* Nacionalidad y Ciudad */}
      <div className={`grid gap-4 ${esParaguay ? 'grid-cols-3' : 'grid-cols-1'}`}>
        <div>
          <label className="label">Nacionalidad</label>
          <select className="input" value={paisId} onChange={handlePaisChange}>
            <option value="">— Seleccionar país —</option>
            {paises.map(p => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
          <input type="hidden" {...register('nacionalidad')} />
        </div>

        {esParaguay && (
          <>
            <div>
              <label className="label">Departamento</label>
              <select className="input" value={deptoId} onChange={handleDeptoChange}>
                <option value="">— Seleccionar —</option>
                {departamentos.map(d => (
                  <option key={d.id} value={d.id}>{d.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Ciudad</label>
              <select className="input" disabled={!deptoId} {...register('id_ciudad')}>
                <option value="">— Seleccionar —</option>
                {ciudades.map(c => (
                  <option key={c.id} value={c.id}>{c.nombre}</option>
                ))}
              </select>
            </div>
          </>
        )}
      </div>

      <div>
        <label className="label">Dirección</label>
        <input className="input" {...register('direccion')} />
      </div>

      <div>
        <label className="label">Fecha de nacimiento</label>
        <input type="date" className="input" {...register('fecha_nacimiento')} />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        <button type="submit" className="btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando…' : isEdit ? 'Actualizar' : 'Registrar'}
        </button>
      </div>
    </form>
  )
}
