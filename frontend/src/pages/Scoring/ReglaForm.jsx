import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { getParametros } from '../../api/scoringApi'
import toast from 'react-hot-toast'

const OPERADORES_LABELS = {
  '>=': 'Mayor o igual que (>=)',
  '<=': 'Menor o igual que (<=)',
  '==': 'Igual a (==)',
  '>':  'Mayor que (>)',
  '<':  'Menor que (<)',
  '!=': 'Diferente de (!=)',
}

export default function ReglaForm({ regla, motorId, onSaved, onCancel, onSubmitFn }) {
  const isEdit = Boolean(regla)
  const [parametros, setParametros] = useState([])
  const [operadores, setOperadores] = useState([])

  const { register, handleSubmit, watch, setValue, formState: { errors, isSubmitting } } = useForm({
    defaultValues: regla ?? {
      nombre: '', descripcion: '', parametro: '', operador: '>=',
      valor_referencia: '', peso_puntos: '', es_determinante: false, activo: true, orden: 0,
    },
  })

  const parametroSeleccionado = watch('parametro')

  useEffect(() => {
    getParametros().then(r => {
      setParametros(r.data.data.parametros)
      setOperadores(r.data.data.operadores)
    })
  }, [])

  // Cuando cambia el parámetro, auto-ajustar el tipo
  useEffect(() => {
    const found = parametros.find(p => p.valor === parametroSeleccionado)
    if (found) {
      setValue('tipo_valor', found.tipo)
      // Para booleanos, sugerir el operador ==
      if (found.tipo === 'booleano') setValue('operador', '==')
    }
  }, [parametroSeleccionado, parametros, setValue])

  const tipoActual = parametros.find(p => p.valor === parametroSeleccionado)?.tipo || 'numerico'

  const onSubmit = async (data) => {
    try {
      await onSubmitFn(data)
      toast.success(isEdit ? 'Regla actualizada' : 'Regla creada')
      onSaved()
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al guardar')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="label">Nombre de la regla *</label>
          <input className={`input ${errors.nombre ? 'border-red-400' : ''}`}
            placeholder="Ej: Ingresos mínimos requeridos"
            {...register('nombre', { required: 'Requerido' })} />
          {errors.nombre && <p className="text-xs text-red-600 mt-1">{errors.nombre.message}</p>}
        </div>
        <div className="col-span-2">
          <label className="label">Descripción</label>
          <input className="input" placeholder="Explicación de la regla..."
            {...register('descripcion')} />
        </div>
      </div>

      {/* Condición IF */}
      <div className="border border-primary-200 rounded-lg p-4 bg-primary-50">
        <p className="text-xs font-semibold text-primary-700 uppercase mb-3">
          Condición IF — cuando el parámetro cumple la condición
        </p>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="label text-xs">Parámetro *</label>
            <select className={`input text-sm ${errors.parametro ? 'border-red-400' : ''}`}
              {...register('parametro', { required: 'Requerido' })}>
              <option value="">— Seleccionar —</option>
              {parametros.map(p => (
                <option key={p.valor} value={p.valor}>{p.label}</option>
              ))}
            </select>
            {errors.parametro && <p className="text-xs text-red-600 mt-1">{errors.parametro.message}</p>}
          </div>
          <div>
            <label className="label text-xs">Operador *</label>
            <select className="input text-sm" {...register('operador', { required: true })}>
              {operadores.map(op => (
                <option key={op} value={op}>{OPERADORES_LABELS[op] || op}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label text-xs">Valor de referencia *</label>
            {tipoActual === 'booleano' ? (
              <select className="input text-sm" {...register('valor_referencia', { required: 'Requerido' })}>
                <option value="true">Verdadero (true)</option>
                <option value="false">Falso (false)</option>
              </select>
            ) : tipoActual === 'texto' ? (
              <select className="input text-sm" {...register('valor_referencia', { required: 'Requerido' })}>
                {parametroSeleccionado === 'historial_pagos' && <>
                  <option value="bueno">Bueno</option>
                  <option value="regular">Regular</option>
                  <option value="malo">Malo</option>
                  <option value="sin_historial">Sin historial</option>
                </>}
                {parametroSeleccionado === 'tipo_empleo' && <>
                  <option value="dependiente">Dependiente</option>
                  <option value="independiente">Independiente</option>
                  <option value="desempleado">Desempleado</option>
                </>}
                {parametroSeleccionado === 'referencias_personales' && <>
                  <option value="buenas">Buenas</option>
                  <option value="regulares">Regulares</option>
                  <option value="malas">Malas</option>
                  <option value="no_verificadas">No verificadas</option>
                </>}
              </select>
            ) : (
              <input type="number" step="any" className={`input text-sm ${errors.valor_referencia ? 'border-red-400' : ''}`}
                placeholder="Ej: 3000000"
                {...register('valor_referencia', { required: 'Requerido' })} />
            )}
            {errors.valor_referencia && <p className="text-xs text-red-600 mt-1">{errors.valor_referencia.message}</p>}
          </div>
        </div>
      </div>

      {/* THEN */}
      <div className="border border-green-200 rounded-lg p-4 bg-green-50">
        <p className="text-xs font-semibold text-green-700 uppercase mb-3">
          THEN — puntos obtenidos si la condición se cumple
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label text-xs">Puntaje *</label>
            <input type="number" step="0.5" min="0.5" className={`input text-sm ${errors.peso_puntos ? 'border-red-400' : ''}`}
              placeholder="Ej: 100"
              {...register('peso_puntos', { required: 'Requerido', min: { value: 0.5, message: 'Debe ser > 0' } })} />
            {errors.peso_puntos && <p className="text-xs text-red-600 mt-1">{errors.peso_puntos.message}</p>}
          </div>
          <div>
            <label className="label text-xs">Orden de evaluación</label>
            <input type="number" min="0" className="input text-sm" {...register('orden')} />
          </div>
        </div>
      </div>

      {/* Opciones */}
      <div className="flex gap-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="w-4 h-4 text-red-600 rounded"
            {...register('es_determinante')} />
          <span className="text-sm font-medium text-red-700">
            Regla determinante
          </span>
          <span className="text-xs text-gray-500">(si falla → rechazo directo)</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="w-4 h-4 text-primary-600 rounded"
            {...register('activo')} />
          <span className="text-sm font-medium text-gray-700">Activa</span>
        </label>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        <button type="submit" className="btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando…' : isEdit ? 'Actualizar' : 'Agregar regla'}
        </button>
      </div>
    </form>
  )
}
