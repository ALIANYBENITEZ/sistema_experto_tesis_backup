// Utilidades de formato de fechas.
//
// IMPORTANTE: para fechas "solo día" (p. ej. fecha_nacimiento, que llega como
// 'YYYY-MM-DD' sin hora) NO se debe usar new Date(...), porque JavaScript la
// interpreta como medianoche UTC y, al convertirla a la zona horaria local,
// puede correrla un día (mostrar 25 cuando la base dice 26). Estas fechas se
// formatean directamente desde el texto, tal cual están en la base de datos.

const LOCALE = 'es-PY'

/**
 * Formatea una fecha "solo día" a DD/MM/YYYY sin aplicar zona horaria.
 * Acepta 'YYYY-MM-DD' o ISO con hora ('YYYY-MM-DDTHH:mm:ss'); en ambos casos
 * usa únicamente la parte de la fecha.
 */
export function fmtFechaSolo(valor) {
  if (!valor) return '—'
  const soloFecha = String(valor).split('T')[0]
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(soloFecha)
  if (m) {
    const [, y, mes, dia] = m
    return `${dia}/${mes}/${y}`
  }
  // Fallback para formatos no esperados
  const d = new Date(valor)
  return Number.isNaN(d.getTime())
    ? String(valor)
    : d.toLocaleDateString(LOCALE, { day: '2-digit', month: '2-digit', year: 'numeric' })
}

/**
 * Formatea un timestamp (con hora) a fecha local es-PY. Para estos valores sí
 * corresponde aplicar la zona horaria, ya que representan un instante concreto.
 */
export function fmtFechaHora(valor, opts = { dateStyle: 'short', timeStyle: 'short' }) {
  if (!valor) return '—'
  const d = new Date(valor)
  return Number.isNaN(d.getTime()) ? String(valor) : d.toLocaleString(LOCALE, opts)
}

/**
 * Formatea un timestamp a solo fecha local es-PY (DD/MM/YYYY), aplicando zona
 * horaria. Usar para timestamps (creado_en, fecha de evaluación), no para
 * fechas "solo día".
 */
export function fmtFechaLocal(valor) {
  if (!valor) return '—'
  const d = new Date(valor)
  return Number.isNaN(d.getTime())
    ? String(valor)
    : d.toLocaleDateString(LOCALE, { day: '2-digit', month: '2-digit', year: 'numeric' })
}
