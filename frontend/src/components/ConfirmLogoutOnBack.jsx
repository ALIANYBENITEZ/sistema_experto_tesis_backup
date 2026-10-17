import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

/**
 * Intercepta el botón "atrás" del navegador mientras el usuario está dentro de
 * la aplicación (sesión iniciada) y pregunta si desea cerrar sesión.
 *
 * Cómo funciona: al montarse empuja un estado al historial del navegador. Si el
 * usuario pulsa "atrás", el navegador dispara 'popstate' en vez de salir; ahí
 * mostramos el diálogo y volvemos a dejar el estado en el historial para seguir
 * "atrapando" el botón hasta que el usuario decida. Si confirma, se cierra la
 * sesión y se va al login; si cancela, permanece en la página actual.
 */
export default function ConfirmLogoutOnBack() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [visible, setVisible] = useState(false)
  const cerrandoRef = useRef(false)

  useEffect(() => {
    // Sembrar una entrada en el historial para capturar el primer "atrás".
    window.history.pushState({ guard: true }, '')

    const onPopState = () => {
      // Si ya estamos cerrando sesión, no reintervenir.
      if (cerrandoRef.current) return
      // Volver a empujar el estado para no perder el control del botón atrás
      // mientras el usuario decide en el diálogo.
      window.history.pushState({ guard: true }, '')
      setVisible(true)
    }

    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  const confirmar = async () => {
    cerrandoRef.current = true
    setVisible(false)
    try { await logout() } catch {}
    toast.success('Sesión cerrada')
    // Reemplazar para que el login no quede "detrás" en el historial.
    navigate('/login', { replace: true })
  }

  const cancelar = () => {
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-xl bg-white shadow-xl">
        <div className="flex items-center gap-3 border-b border-gray-100 px-6 py-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-700">
            <LogOut className="h-5 w-5" />
          </div>
          <h2 className="text-base font-semibold text-gray-800">Cerrar sesión</h2>
        </div>

        <div className="px-6 py-5">
          <p className="text-sm text-gray-600">
            ¿Quieres cerrar sesión? Si continúas, saldrás del sistema y deberás
            iniciar sesión nuevamente.
          </p>
        </div>

        <div className="flex justify-end gap-3 border-t border-gray-100 px-6 py-4">
          <button
            onClick={cancelar}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            No, permanecer
          </button>
          <button
            onClick={confirmar}
            className="rounded-lg bg-primary-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-800"
          >
            Sí, cerrar sesión
          </button>
        </div>
      </div>
    </div>
  )
}
