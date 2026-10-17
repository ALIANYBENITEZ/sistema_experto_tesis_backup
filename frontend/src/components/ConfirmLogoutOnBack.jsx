import { useEffect, useState, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

/**
 * Intercepta el botón "atrás" del navegador mientras el usuario está dentro de
 * la aplicación (sesión iniciada) y pregunta si desea cerrar sesión.
 *
 * Estrategia: mantener SIEMPRE una entrada "guard" en la cima del historial.
 * Cada vez que cambia la ruta (el usuario navega), se reinyecta esa entrada, de
 * modo que el próximo "atrás" dispare 'popstate' en esta guardia en lugar de
 * retroceder de página. Al detectar el 'popstate' se muestra el diálogo y se
 * vuelve a sembrar la entrada para seguir atrapando el botón hasta que el
 * usuario decida. Si confirma, se cierra sesión; si cancela, permanece.
 */
export default function ConfirmLogoutOnBack() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [visible, setVisible] = useState(false)
  const cerrandoRef = useRef(false)

  // Reinyectar la entrada "guard" en cada cambio de ruta. Así, sin importar en
  // qué página esté el usuario, el próximo "atrás" cae en nuestra guardia.
  useEffect(() => {
    window.history.pushState({ guard: true }, '')
  }, [location.pathname])

  useEffect(() => {
    const onPopState = () => {
      if (cerrandoRef.current) return
      // Volver a dejar la entrada en el historial para no perder el control
      // del botón atrás mientras el usuario decide en el diálogo.
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
