import { User, Mail, Phone, MapPin, Calendar, Globe, IdCard, CheckCircle2, XCircle } from 'lucide-react'
import { fmtFechaSolo, fmtFechaLocal } from '../../utils/fecha'

const TIPO_DOC_LABEL = { CI: 'Cédula de Identidad', RUC: 'RUC', PAS: 'Pasaporte' }

function Row({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
      <Icon className="h-4 w-4 text-gray-400 mt-0.5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-sm text-gray-800 break-words">{value || '—'}</p>
      </div>
    </div>
  )
}

export default function ClientDetail({ client }) {
  if (!client) return null

  const activo = client.estado === 'activo'
  const nombreCompleto = `${client.nombre} ${client.apellido ?? ''}`.trim()

  return (
    <div className="space-y-4">
      {/* Encabezado */}
      <div className="flex items-center gap-4 pb-4 border-b border-gray-200">
        <div className="h-14 w-14 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-xl">
          {client.nombre?.[0]?.toUpperCase() || '?'}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 truncate">{nombreCompleto}</h3>
          <p className="text-sm text-gray-500">
            {TIPO_DOC_LABEL[client.tipo_doc] || client.tipo_doc} · {client.num_doc}
          </p>
        </div>
        <span
          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
            activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
          }`}
        >
          {activo ? <CheckCircle2 className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
          {client.estado}
        </span>
      </div>

      {/* Datos */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6">
        <Row icon={IdCard}   label="Tipo de documento" value={TIPO_DOC_LABEL[client.tipo_doc] || client.tipo_doc} />
        <Row icon={IdCard}   label="N° de documento"   value={client.num_doc} />
        <Row icon={User}     label="Nombre"            value={client.nombre} />
        <Row icon={User}     label="Apellido"          value={client.apellido} />
        <Row icon={Mail}     label="Email"             value={client.email} />
        <Row icon={Phone}    label="Teléfono"          value={client.telefono} />
        <Row icon={Globe}    label="Nacionalidad"      value={client.nacionalidad_nombre || client.nacionalidad} />
        <Row icon={MapPin}   label="Ciudad"            value={client.ciudad_nombre} />
        <Row icon={MapPin}   label="Dirección"         value={client.direccion} />
        <Row icon={Calendar} label="Fecha de nacimiento" value={fmtFechaSolo(client.fecha_nacimiento)} />
        <Row icon={Calendar} label="Registrado el"     value={fmtFechaLocal(client.creado_en)} />
      </div>
    </div>
  )
}
