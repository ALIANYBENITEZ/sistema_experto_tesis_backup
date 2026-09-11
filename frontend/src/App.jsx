import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import Layout from './components/Layout'

import LoginPage             from './pages/Login/LoginPage'
import DashboardPage         from './pages/Dashboard/DashboardPage'
import ClientsPage           from './pages/Clients/ClientsPage'
import EvaluationsPage       from './pages/Evaluations/EvaluationsPage'
import NewEvaluationPage     from './pages/Evaluations/NewEvaluationPage'
import CoreResultadoPage     from './pages/Evaluations/CoreResultadoPage'
import EvaluationDetailPage  from './pages/Evaluations/EvaluationDetailPage'
import ReportsPage           from './pages/Reports/ReportsPage'
import UsersPage             from './pages/Users/UsersPage'
import ScoringPage           from './pages/Scoring/ScoringPage'
import NuevoModeloPage       from './pages/Scoring/NuevoModeloPage'
import CoreModeloPage        from './pages/Scoring/CoreModeloPage'
import ResultadoPage         from './pages/Scoring/ResultadoPage'
import MotoresPage           from './pages/Scoring/MotoresPage'
import MotorDetallePage      from './pages/Scoring/MotorDetallePage'
import EmpresasPage          from './pages/Empresas/EmpresasPage'
import EmpresaDetailPage     from './pages/Empresas/EmpresaDetailPage'
import NewEmpresaPage        from './pages/Empresas/NewEmpresaPage'
import SecurityPage          from './pages/Security/SecurityPage'
import FacturacionPage       from './pages/Facturacion/FacturacionPage'
import AuditoriaPage         from './pages/Auditoria/AuditoriaPage'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard"              element={<DashboardPage />} />
            <Route path="/clients"                element={<ClientsPage />} />
            <Route path="/evaluations"            element={<EvaluationsPage />} />
            <Route path="/evaluations/new"        element={<NewEvaluationPage />} />
            <Route path="/evaluations/resultado/:evalId" element={<CoreResultadoPage />} />
            <Route path="/evaluations/:id"        element={<EvaluationDetailPage />} />
            <Route path="/reports"                element={<ReportsPage />} />

            {/* Scoring - admin y propietario */}
            <Route path="/scoring"                    element={<ScoringPage />} />
            <Route path="/scoring/nuevo-modelo"       element={<NuevoModeloPage />} />
            <Route path="/scoring/modelo/:modeloId"   element={<CoreModeloPage />} />
            <Route path="/scoring/evaluar"            element={<Navigate to="/evaluations/new" replace />} />
            <Route path="/scoring/resultado/:evalId"  element={<ResultadoPage />} />
            <Route path="/scoring/motores"            element={<MotoresPage />} />
            <Route path="/scoring/motores/:motorId"   element={<MotorDetallePage />} />

            {/* Solo propietario */}
            <Route path="/facturacion"            element={<FacturacionPage />} />
            <Route path="/auditoria"              element={<AuditoriaPage />} />
            <Route path="/seguridad"              element={<SecurityPage />} />
            <Route path="/empresas"               element={<EmpresasPage />} />
            <Route path="/empresas/new"           element={<NewEmpresaPage />} />
            <Route path="/empresas/:empresaId"    element={<EmpresaDetailPage />} />
            <Route path="/users"                  element={<UsersPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  )
}
