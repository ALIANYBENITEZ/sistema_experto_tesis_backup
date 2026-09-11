import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { createEmpresa } from '../../api/empresaApi'
import toast from 'react-hot-toast'

export default function NewEmpresaPage() {
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()

  const onSubmit = async (data) => {
    try {
      await createEmpresa(data)
      toast.success('Empresa registrada')
      navigate('/empresas')
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error al registrar')
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Nueva Empresa Cliente</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4">
        <div>
          <label className="label">Nombre de la empresa *</label>
          <input className={`input ${errors.nombre ? 'border-red-400' : ''}`}
            {...register('nombre', { required: 'Requerido' })} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">RUC</label>
            <input className="input" {...register('ruc')} />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" className="input" {...register('email')} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Teléfono</label>
            <input className="input" {...register('telefono')} />
          </div>
          <div>
            <label className="label">Dirección</label>
            <input className="input" {...register('direccion')} />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={() => navigate('/empresas')} className="btn-secondary">Cancelar</button>
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Registrando...' : 'Registrar Empresa'}
          </button>
        </div>
      </form>
    </div>
  )
}
