// Utilidades de sesión: controlan el tiempo de sesión configurable que informa
// el backend (en segundos) y permiten saber si la sesión ya expiró.

const EXP_KEY = 'session_expires_at'

// Guarda el momento (epoch en ms) en que expira la sesión, a partir del tiempo
// de sesión en segundos recibido del backend al autenticarse.
export function guardarExpiracion(segundos) {
  if (!segundos) return
  const expiraEn = Date.now() + Number(segundos) * 1000
  localStorage.setItem(EXP_KEY, String(expiraEn))
}

// true si existe una marca de expiración y ya se cumplió.
export function sesionExpirada() {
  const exp = Number(localStorage.getItem(EXP_KEY) || 0)
  return exp > 0 && Date.now() >= exp
}

// Milisegundos restantes hasta la expiración (0 si no hay marca o ya expiró).
export function msHastaExpiracion() {
  const exp = Number(localStorage.getItem(EXP_KEY) || 0)
  if (exp <= 0) return 0
  return Math.max(0, exp - Date.now())
}
