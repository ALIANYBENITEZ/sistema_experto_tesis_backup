import { useForm } from 'react-hook-form'
import { createUser, updateUser } from '../../api/userApi'
import toast from 'react-hot-toast'

export default function UserForm({ user, onSaved, onCancel }) {
  const isEdit = Boolean(user)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    defaultValues: user
      ? { nombre: user.nombre, apellido: user.apellido, email: user.email, rol: user.rol, password: '' }
      : { nombre: '', apellido: '', email: '', rol: 'operador', password: '' },
  })

  const onSubmit = async (data) => {
    try {
      if (isEdit) {
        const payload = { ...data }
        if (!payload.password) delete payload.password
        await updateUser(user.id, payload)
        toast.success('Usuario actualizado')
      } else {
        await createUser(data)
        toast.success('Usuario creado')
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
          <label className="label">Nombre *</label>
          <input className={`input ${errors.nombre ? 'border-red-400' : ''}`}
            {...register('nombre', { required: 'Requerido' })} />
          {errors.nombre && <p className="text-xs text-red-600 mt-1">{errors.nombre.message}</p>}
        </div>
        <div>
          <label className="label">Apellido *</label>
          <input className={`input ${errors.apellido ? 'border-red-400' : ''}`}
            {...register('apellido', { required: 'Requerido' })} />
          {errors.apellido && <p className="text-xs text-red-600 mt-1">{errors.apellido.message}</p>}
        </div>
      </div>

      <div>
        <label className="label">Email *</label>
        <input type="email" className={`input ${errors.email ? 'border-red-400' : ''}`}
          disabled={isEdit}
          {...register('email', {
            required: 'Requerido',
            pattern: { value: /\S+@\S+\.\S+/, message: 'Email inválido' },
          })} />
        {errors.email && <p className="text-xs text-red-600 mt-1">{errors.email.message}</p>}
      </div>

      <div>
        <label className="label">Rol *</label>
        <select className="input" {...register('rol', { required: true })}>
          <option value="operador">Operador</option>
          <option value="administrador">Administrador</option>
        </select>
      </div>

      <div>
        <label className="label">{isEdit ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña *'}</label>
        <input
          type="password" className="input"
          placeholder={isEdit ? 'Solo si desea cambiarla' : ''}
          {...register('password', { required: !isEdit ? 'Requerido' : false, minLength: { value: 6, message: 'Mínimo 6 caracteres' } })}
        />
        {errors.password && <p className="text-xs text-red-600 mt-1">{errors.password.message}</p>}
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        <button type="submit" className="btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando…' : isEdit ? 'Actualizar' : 'Crear usuario'}
        </button>
      </div>
    </form>
  )
}
