export default function ResultadoBadge({ resultado }) {
  const map = {
    aprobado:  'badge-green',
    observado: 'badge-yellow',
    rechazado: 'badge-red',
    bajo:      'badge-green',
    medio:     'badge-yellow',
    alto:      'badge-red',
  }
  const labels = {
    aprobado:  'Aprobado',
    observado: 'Observado',
    rechazado: 'Rechazado',
    bajo:      'Bajo Riesgo',
    medio:     'Medio Riesgo',
    alto:      'Alto Riesgo',
  }
  return (
    <span className={map[resultado] ?? 'badge-gray'}>
      {labels[resultado] ?? resultado ?? '—'}
    </span>
  )
}
