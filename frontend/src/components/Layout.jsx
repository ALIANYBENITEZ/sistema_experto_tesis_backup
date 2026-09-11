import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, UserCircle, ClipboardList,
  BarChart2, LogOut, Menu, Building2, ShieldCheck, Briefcase, Lock, CreditCard, ScrollText,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

const NAV_ITEMS = [
  { to: '/dashboard',   label: 'Dashboard',          icon: LayoutDashboard, roles: ['propietario', 'administrador', 'comercial'] },
  { to: '/clients',     label: 'Clientes',           icon: UserCircle,      roles: ['propietario', 'administrador', 'comercial'] },
  { to: '/evaluations', label: 'Evaluaciones',       icon: ClipboardList,   roles: ['propietario', 'administrador', 'comercial'] },
  { to: '/scoring',     label: 'Scoring Riesgo',     icon: ShieldCheck,     roles: ['propietario', 'administrador'] },
  { to: '/reports',     label: 'Reportes',           icon: BarChart2,       roles: ['propietario', 'administrador', 'comercial'] },
  { to: '/facturacion', label: 'Facturación',        icon: CreditCard,      roles: ['propietario', 'administrador'] },
  { to: '/seguridad',   label: 'Seguridad',          icon: Lock,            roles: ['propietario', 'administrador'] },
  { to: '/auditoria',   label: 'Auditoría',          icon: ScrollText,      roles: ['propietario', 'administrador'] },
  { to: '/empresas',    label: 'Empresas Clientes',  icon: Briefcase,       roles: ['propietario'] },
  { to: '/users',       label: 'Usuarios',           icon: Users,           roles: ['propietario'] },
]


export default function Layout() {
  const { user, logout, isAdmin } = useAuth()
  const navigate  = useNavigate()
  const [open, setOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    toast.success('Sesión cerrada')
    navigate('/login')
  }

  const items = NAV_ITEMS.filter(i => i.roles.includes(user?.rol))

  const SidebarContent = () => (
    <>
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-primary-700">
        <Building2 className="h-8 w-8 text-primary-200" />
        <div>
          <p className="text-white font-bold text-sm leading-tight">Sistema</p>
          <p className="text-white/70 text-xs">Inmobiliaria</p>
        </div>
      </div>

      {/* Navegación */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto no-scrollbar">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
               ${isActive
                 ? 'bg-primary-700 text-white'
                 : 'text-white hover:bg-primary-700/50 hover:text-white'}`
            }
          >
            <Icon className="h-5 w-5 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Usuario */}
      <div className="px-4 py-4 border-t border-primary-700">
        <div className="flex items-center gap-3 mb-3 px-2">
          <div className="h-8 w-8 rounded-full bg-primary-400 flex items-center justify-center text-white font-bold text-sm">
            {user?.nombre?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white text-sm font-medium truncate">{user?.nombre} {user?.apellido}</p>
            <p className="text-white/70 text-xs capitalize">{user?.rol}</p>
          </div>
        </div>
        <button onClick={handleLogout} className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-white hover:bg-primary-700/50 hover:text-white text-sm transition-colors">
          <LogOut className="h-4 w-4" />
          Cerrar sesión
        </button>
      </div>
    </>
  )

  return (
    <div className="flex h-full">
      {/* Sidebar Desktop */}
      <aside className="hidden lg:flex lg:flex-col w-64 bg-primary-900 flex-shrink-0">
        <SidebarContent />
      </aside>

      {/* Sidebar Mobile overlay */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="relative flex flex-col w-64 h-full bg-primary-900 z-50">
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar mobile */}
        <header className="lg:hidden flex items-center gap-3 px-4 py-3 bg-white border-b border-gray-200 shadow-sm">
          <button onClick={() => setOpen(true)} className="p-1.5 rounded-md text-gray-500 hover:bg-gray-100">
            <Menu className="h-5 w-5" />
          </button>
          <Building2 className="h-6 w-6 text-primary-600" />
          <span className="font-semibold text-gray-800 text-sm">Sistema Inmobiliaria</span>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
