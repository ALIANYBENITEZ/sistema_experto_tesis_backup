import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuth } from '../../context/AuthContext'
import { forgotPassword } from '../../api/authApi'
import toast from 'react-hot-toast'
import './login-neon.css'

// Isotipo minimalista (asterisco/estrella)
const Mark = () => (
  <svg className="lm-mark" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path
      d="M24 4v40M9 12l30 24M39 12L9 36"
      stroke="currentColor"
      strokeWidth="4.5"
      strokeLinecap="round"
    />
  </svg>
)

// Arcos decorativos sutiles para el panel de marca
const BrandArcs = () => (
  <svg
    className="lm-brand-arcs"
    viewBox="0 0 600 800"
    preserveAspectRatio="xMidYMid slice"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <g stroke="#ffffff" strokeOpacity="0.08" strokeWidth="1.5" fill="none">
      <path d="M-40 40 Q 360 120 340 520" />
      <path d="M-40 90 Q 400 160 380 560" />
      <path d="M-40 140 Q 440 200 420 600" />
      <path d="M-40 190 Q 480 240 460 640" />
      <path d="M-40 240 Q 520 280 500 680" />
    </g>
  </svg>
)

// Panel de marca (columna izquierda), común a todas las pantallas
function BrandPanel() {
  return (
    <div className="lm-brand">
      <BrandArcs />
      <div className="lm-brand-content">
        <Mark />
      </div>
      <div className="lm-brand-content">
        <h2 className="lm-brand-heading">Bienvenido de<br />nuevo</h2>
        <p className="lm-brand-text">
          Sistema experto de scoring comercial. Evalúa clientes con criterios
          ponderados y un motor de reglas para decisiones de crédito más ágiles.
        </p>
      </div>
      <div className="lm-brand-footer">© {new Date().getFullYear()} Scoring Comercial. Todos los derechos reservados.</div>
    </div>
  )
}

// Envoltura de dos paneles
function LoginShell({ children }) {
  return (
    <div className="lm-page">
      <BrandPanel />
      <div className="lm-form-panel">
        <div className="lm-form-inner">{children}</div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, authState, qrCode, complete2FASetup, complete2FAVerify } = useAuth()
  const [step, setStep] = useState('login') // login, 2fa_setup, 2fa_verify, forgot
  const { register, handleSubmit, formState: { isSubmitting } } = useForm()
  const {
    register: registerForgot,
    handleSubmit: handleSubmitForgot,
    reset: resetForgot,
    formState: { isSubmitting: isSubmittingForgot },
  } = useForm()
  const [otpCode, setOtpCode] = useState('')
  const [otpLoading, setOtpLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)

  // Cargar Google Fonts una sola vez
  useEffect(() => {
    const id = 'ln-google-fonts'
    if (!document.getElementById(id)) {
      const link = document.createElement('link')
      link.id = id
      link.rel = 'stylesheet'
      link.href = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:wght@500;600&display=swap'
      document.head.appendChild(link)
    }
  }, [])

  const showAdminNotice = () => {
    toast('Contáctese con su administrador.', { icon: 'ℹ️' })
  }

  const goToForgot = () => {
    resetForgot()
    setShowNewPassword(false)
    setStep('forgot')
  }

  const backToLogin = () => {
    resetForgot()
    setStep('login')
  }

  const onForgotPassword = async (data) => {
    if (data.new_password !== data.confirm_password) {
      toast.error('La nueva contraseña y su confirmación no coinciden')
      return
    }
    try {
      const { data: res } = await forgotPassword({
        email: data.email,
        codigo: data.codigo,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      })
      toast.success(res.message || 'Contraseña restablecida correctamente')
      backToLogin()
    } catch (err) {
      toast.error(err.response?.data?.message || 'No fue posible restablecer la contraseña')
    }
  }

  const onLogin = async (data) => {
    try {
      const result = await login(data.email, data.password)
      if (result.auth_state === 'authenticated') {
        navigate('/dashboard')
      } else if (result.auth_state === '2fa_setup_required') {
        setStep('2fa_setup')
      } else if (result.auth_state === '2fa_required') {
        setStep('2fa_verify')
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error de autenticación')
    }
  }

  const onVerifyOTP = async () => {
    if (!otpCode || otpCode.length !== 6) {
      toast.error('Ingrese un código de 6 dígitos')
      return
    }
    setOtpLoading(true)
    try {
      if (step === '2fa_setup') {
        await complete2FASetup(otpCode)
        toast.success('2FA configurado exitosamente')
      } else {
        await complete2FAVerify(otpCode)
      }
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.message || 'Código incorrecto')
      setOtpCode('')
    } finally {
      setOtpLoading(false)
    }
  }

  // ── Pantalla de Login ──
  if (step === 'login') {
    return (
      <LoginShell>
        <p className="lm-logo">Scoring Comercial</p>

        <h1 className="lm-title">Iniciar sesión</h1>
        <p className="lm-subtitle">Ingrese sus credenciales para acceder al sistema.</p>

        <form onSubmit={handleSubmit(onLogin)} className="lm-form">
          <div className="lm-field">
            <label className="lm-label">Correo electrónico</label>
            <div className="lm-input-wrap">
              <input
                type="email"
                className="lm-input"
                placeholder="correo@empresa.com"
                autoComplete="username"
                {...register('email', { required: true })}
              />
            </div>
          </div>

          <div className="lm-field">
            <label className="lm-label">Contraseña</label>
            <div className="lm-input-wrap">
              <input
                type={showPassword ? 'text' : 'password'}
                className="lm-input"
                placeholder="••••••••"
                autoComplete="current-password"
                {...register('password', { required: true })}
              />
              <button type="button" className="lm-eye" onClick={() => setShowPassword(!showPassword)} tabIndex={-1}>
                {showPassword ? 'ocultar' : 'ver'}
              </button>
            </div>
          </div>

          <div className="lm-links">
            <span className="lm-link" onClick={goToForgot}>¿Olvidó su contraseña?</span>
            <span className="lm-link" onClick={showAdminNotice}>Ayuda</span>
          </div>

          <button type="submit" className="lm-btn" disabled={isSubmitting}>
            {isSubmitting ? 'Verificando...' : 'Iniciar sesión'}
          </button>
        </form>
      </LoginShell>
    )
  }

  // ── Pantalla de configuración 2FA (primer uso) ──
  if (step === '2fa_setup') {
    return (
      <LoginShell>
        <p className="lm-logo">Scoring Comercial</p>

        <h1 className="lm-title">Configurar 2FA</h1>
        <p className="lm-subtitle">Proteja su cuenta con Google Authenticator.</p>

        <div className="lm-info">
          <p className="lm-info-title">Instrucciones:</p>
          <ol>
            <li>Instale <strong>Google Authenticator</strong> en su teléfono</li>
            <li>Abra la app y seleccione "Agregar cuenta"</li>
            <li>Escanee el código QR de abajo</li>
            <li>Ingrese el código de 6 dígitos</li>
          </ol>
        </div>

        {qrCode && (
          <div className="lm-qr-wrap">
            <img src={`data:image/png;base64,${qrCode}`} alt="Código QR" className="lm-qr" />
          </div>
        )}

        <input
          type="text" maxLength={6}
          className="lm-otp"
          placeholder="000000"
          value={otpCode}
          onChange={e => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
          onKeyDown={e => e.key === 'Enter' && onVerifyOTP()}
        />

        <button onClick={onVerifyOTP} className="lm-btn" disabled={otpLoading}>
          {otpLoading ? 'Verificando...' : 'Verificar y Activar'}
        </button>
      </LoginShell>
    )
  }

  // ── Pantalla de ingreso OTP (login recurrente) ──
  if (step === '2fa_verify') {
    return (
      <LoginShell>
        <p className="lm-logo">Scoring Comercial</p>

        <h1 className="lm-title">Verificación</h1>
        <p className="lm-subtitle">Ingrese el código de Google Authenticator.</p>

        <input
          type="text" maxLength={6}
          className="lm-otp"
          placeholder="000000"
          value={otpCode}
          onChange={e => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
          onKeyDown={e => e.key === 'Enter' && onVerifyOTP()}
          autoFocus
        />

        <button onClick={onVerifyOTP} className="lm-btn" disabled={otpLoading}>
          {otpLoading ? 'Verificando...' : 'Verificar'}
        </button>

        <p className="lm-hint">Abra Google Authenticator y copie el código de 6 dígitos</p>
      </LoginShell>
    )
  }

  // ── Pantalla de recuperación de contraseña (OTP de authenticator) ──
  if (step === 'forgot') {
    return (
      <LoginShell>
        <p className="lm-logo">Scoring Comercial</p>

        <h1 className="lm-title">Recuperar contraseña</h1>
        <p className="lm-subtitle">
          Verifique su identidad con el código de Google Authenticator y defina una nueva contraseña.
        </p>

        <form onSubmit={handleSubmitForgot(onForgotPassword)} className="lm-form">
          <div className="lm-field">
            <label className="lm-label">Correo electrónico</label>
            <div className="lm-input-wrap">
              <input
                type="email"
                className="lm-input"
                placeholder="correo@empresa.com"
                autoComplete="username"
                {...registerForgot('email', { required: true })}
              />
            </div>
          </div>

          <div className="lm-field">
            <label className="lm-label">Código de Google Authenticator</label>
            <div className="lm-input-wrap">
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                className="lm-input"
                placeholder="000000"
                {...registerForgot('codigo', {
                  required: true,
                  pattern: /^\d{6}$/,
                  setValueAs: v => (v || '').replace(/\D/g, '').slice(0, 6),
                })}
              />
            </div>
          </div>

          <div className="lm-field">
            <label className="lm-label">Nueva contraseña</label>
            <div className="lm-input-wrap">
              <input
                type={showNewPassword ? 'text' : 'password'}
                className="lm-input"
                placeholder="Mínimo 8 caracteres"
                autoComplete="new-password"
                {...registerForgot('new_password', { required: true, minLength: 8 })}
              />
              <button type="button" className="lm-eye" onClick={() => setShowNewPassword(!showNewPassword)} tabIndex={-1}>
                {showNewPassword ? 'ocultar' : 'ver'}
              </button>
            </div>
          </div>

          <div className="lm-field">
            <label className="lm-label">Confirmar contraseña</label>
            <div className="lm-input-wrap">
              <input
                type={showNewPassword ? 'text' : 'password'}
                className="lm-input"
                placeholder="Repita la nueva contraseña"
                autoComplete="new-password"
                {...registerForgot('confirm_password', { required: true, minLength: 8 })}
              />
            </div>
          </div>

          <button type="submit" className="lm-btn" disabled={isSubmittingForgot}>
            {isSubmittingForgot ? 'Restableciendo...' : 'Restablecer contraseña'}
          </button>

          <div className="lm-links" style={{ justifyContent: 'center' }}>
            <span className="lm-link" onClick={backToLogin}>Volver a iniciar sesión</span>
          </div>
        </form>

        <p className="lm-hint">
          ¿No tiene Google Authenticator configurado? Contáctese con su administrador.
        </p>
      </LoginShell>
    )
  }

  return null
}
