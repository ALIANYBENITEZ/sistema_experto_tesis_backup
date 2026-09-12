# Sistema Experto de Scoring Comercial

Sistema de evaluación de clientes para una empresa inmobiliaria. Permite registrar
clientes, evaluarlos mediante **criterios ponderados** y un **motor de inferencia
basado en reglas** (sistema experto IF-THEN), y generar reportes de riesgo
crediticio. Incluye facturación por consumo de reportes con pasarela de pagos.

> Contexto: Paraguay (documentos DNI/RUC/CE, montos en guaraníes). Idioma del
> dominio en español.

---

## Tabla de contenidos

- [Características](#características)
- [Arquitectura y stack](#arquitectura-y-stack)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)
- [Ejecución](#ejecución)
- [Roles y credenciales](#roles-y-credenciales)
- [Módulos principales](#módulos-principales)
- [Pasarela de pagos (Pagopar)](#pasarela-de-pagos-pagopar)
- [Base de datos: respaldo y restauración](#base-de-datos-respaldo-y-restauración)
- [Seguridad](#seguridad)
- [Solución de problemas](#solución-de-problemas)

---

## Características

- Autenticación con **JWT** (access 8h / refresh 30d) y **2FA** con Google Authenticator (TOTP).
- Recuperación de contraseña mediante código OTP del authenticator.
- Gestión de **clientes** con documentos adjuntos.
- **Evaluación por criterios** ponderados configurables.
- **Motor de reglas** IF-THEN con clasificación de riesgo (bajo/medio/alto/rechazado).
- **Reportes** en PDF y estadísticas de dashboard.
- **Facturación** prepago por reportes, con planes, consumo y **pagos vía Pagopar**.
- Modelo **multi-empresa** (multi-tenant) con bloqueo/desbloqueo por deuda.
- **Auditoría** de operaciones sensibles.

---

## Arquitectura y stack

**Backend — API REST (Flask)**
- Python 3.12, Flask 3.1 con patrón *Application Factory*.
- Flask-SQLAlchemy 3.1, Flask-JWT-Extended 4.6, Flask-CORS 4.
- SQL Server 2022 vía pyodbc (ODBC Driver 17/18).
- marshmallow (validación), reportlab (PDF), pyotp + qrcode (2FA), requests (Pagopar).
- Hashing de contraseñas con `werkzeug.security` (scrypt).

**Frontend — SPA (React)**
- React 18.3 (JSX), Vite 5.4, react-router-dom 6.
- Axios con interceptores (auto-refresh de token), react-hook-form.
- TailwindCSS 3.4, lucide-react, Recharts, react-hot-toast.
- Estado de sesión con React Context (`AuthContext`).

Respuestas JSON normalizadas: `{ "success": bool, "message": str, "data": ... }`.
Rutas bajo el prefijo `/api/<módulo>`.

---

## Estructura del proyecto

```
V.0.1/
├── backend/                    # API REST Flask
│   ├── app/
│   │   ├── __init__.py         # create_app (Application Factory)
│   │   ├── config.py           # Configuración por entorno
│   │   ├── extensions.py       # SQLAlchemy, JWT, CORS
│   │   ├── blueprints/         # Un blueprint por dominio
│   │   │   ├── auth/  clients/  evaluation/  scoring/
│   │   │   ├── reports/  users/  empresas/  facturacion/  auditoria/
│   │   ├── core/               # Motor de scoring (engine, classifier, ...)
│   │   ├── models/             # Modelos SQLAlchemy (tablas en español)
│   │   ├── services/           # pagopar_service, totp_service, auditoria_service, ...
│   │   └── utils/              # decorators, responses
│   ├── migrations/             # Scripts SQL (estructura de la BD)
│   ├── scripts/                # backup_db.ps1 / restore_db.ps1
│   ├── run.py                  # Entrypoint (puerto 5000)
│   ├── seed.py                 # Datos iniciales
│   └── requirements.txt
│
├── frontend/                   # SPA React + Vite
│   ├── src/
│   │   ├── api/                # Servicios HTTP (axiosConfig + por dominio)
│   │   ├── components/         # Layout, ProtectedRoute, ...
│   │   ├── context/            # AuthContext
│   │   └── pages/              # Una carpeta por módulo
│   ├── vite.config.js
│   └── package.json
│
├── credit-scoring/             # Prototipo standalone (Flask + Jinja2, datos mock)
├── backups/                    # Respaldos .bak (ignorado por Git)
├── INSTRUCTIVO.md              # Guía operativa detallada
└── README.md
```

---

## Requisitos previos

| Herramienta | Versión |
|---|---|
| Python | 3.12.x |
| Node.js | 18+ (probado con 24.x) |
| npm | 9+ |
| SQL Server | 2022 Express |
| ODBC Driver | 17 o 18 for SQL Server |

---

## Instalación

```bash
# 1) Clonar el repositorio
git clone https://github.com/ALIANYBENITEZ/Sistema_experto_tesis.git
cd Sistema_experto_tesis

# 2) Backend
cd backend
python -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt

# 3) Frontend
cd ../frontend
npm install
```

### Preparar la base de datos

Opción A — recrear la estructura desde cero (PC nueva):

```powershell
# Ejecutar en orden los scripts de backend/migrations/ con SSMS o sqlcmd:
#   01_create_tables.sql ... 07_fk_faltantes.sql
# Luego cargar los datos iniciales:
cd backend
.\venv\Scripts\python.exe seed.py
```

Opción B — restaurar un respaldo existente (ver
[respaldo y restauración](#base-de-datos-respaldo-y-restauración)).

---

## Variables de entorno

Copiá `backend/.env.example` a `backend/.env` y completá los valores.

```
FLASK_ENV=development
SECRET_KEY=<clave aleatoria de 32+ caracteres>
JWT_SECRET_KEY=<otra clave aleatoria de 32+ caracteres>

# SQL Server (autenticación Windows o SQL)
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=inmobiliaria_db
DB_DRIVER=ODBC Driver 17 for SQL Server
# DB_USER=sa
# DB_PASSWORD=...

# Pasarela Pagopar (opcional; si se deja vacío usa el pago de prueba)
PAGOPAR_PUBLIC_KEY=
PAGOPAR_PRIVATE_KEY=
PAGOPAR_BASE_URL=https://api.pagopar.com/api
PAGOPAR_URL_RETORNO=http://localhost:3000/facturacion
PAGOPAR_URL_NOTIFICACION=http://localhost:5000/api/facturacion/pagopar/webhook
```

Frontend — `frontend/.env`:

```
VITE_API_URL=http://localhost:5000/api
```

> Generar claves seguras:
> `python -c "import secrets; print(secrets.token_urlsafe(48))"`

En **producción** (`FLASK_ENV=production`), `SECRET_KEY` y `JWT_SECRET_KEY` son
obligatorias y deben tener al menos 32 caracteres, o el backend no arranca.

---

## Ejecución

Dos terminales en paralelo:

```powershell
# Terminal 1 — Backend (http://localhost:5000)
cd backend
.\venv\Scripts\Activate.ps1
python run.py

# Terminal 2 — Frontend (http://localhost:3000)
cd frontend
npm run dev
```

Abrí `http://localhost:3000`. Verificá el backend en
`http://localhost:5000/api/health`.

Build de producción del frontend: `npm run build`.

---

## Roles y credenciales

| Rol | Alcance |
|---|---|
| `propietario` | Dueño del sistema. Gestiona empresas, planes, facturación global. |
| `administrador` | Admin de su empresa: usuarios, configuración, facturación propia. |
| `comercial` | Registro de clientes, evaluaciones y consulta de reportes. |

Las credenciales iniciales se crean con `seed.py`. Consultá `INSTRUCTIVO.md`
para los usuarios de prueba.

---

## Módulos principales

- **Autenticación:** login con JWT + 2FA (TOTP), recuperación de contraseña por OTP.
- **Clientes:** CRUD con documentos.
- **Evaluación por criterios:** puntaje ponderado (Capacidad de Pago, Historial,
  Estabilidad Laboral, Documentación, Patrimonio).
- **Scoring / Motor de reglas:** sistema experto IF-THEN, reglas determinantes,
  clasificación automática de riesgo.
- **Reportes:** generación de PDF y estadísticas.
- **Facturación:** planes, consumo de reportes, pagos, bloqueo por deuda.
- **Gestión de usuarios y empresas:** alta/baja y multi-tenant.
- **Auditoría:** registro de operaciones sensibles.

---

## Pasarela de pagos (Pagopar)

El módulo de Facturación cobra los períodos pendientes con **Pagopar** (Paraguay,
guaraníes). Si no se cargan credenciales, el sistema usa un **pago de prueba (TEST)**
que no cobra dinero real.

Flujo: iniciar pago → redirección al checkout de Pagopar → webhook de
notificación → el pago se marca `APROBADO`, se actualiza el período y se
desbloquea la empresa si estaba bloqueada por deuda.

Endpoints:
- `GET  /api/facturacion/pagopar/estado` — indica si la pasarela está activa.
- `POST /api/facturacion/pagos/pagopar/iniciar` — inicia el pago, devuelve la URL del checkout.
- `POST /api/facturacion/pagopar/webhook` — recibe la notificación (público, valida token SHA1).

Para configurarlo y probarlo (incluye guía con **ngrok** para el webhook en local),
ver la sección "Pasarela de pagos Pagopar" en `INSTRUCTIVO.md`.

---

## Base de datos: respaldo y restauración

Los datos reales viven en SQL Server (no en el repositorio). Se versionan solo
los scripts de estructura (`backend/migrations/`) y los seeds.

```powershell
# Crear un respaldo (.bak en la carpeta backups/)
powershell -ExecutionPolicy Bypass -File ".\backend\scripts\backup_db.ps1"

# Restaurar el respaldo más reciente
powershell -ExecutionPolicy Bypass -File ".\backend\scripts\restore_db.ps1"
```

Los `.bak` contienen datos personales, por eso `backups/` está en `.gitignore`
y no se sube a GitHub. Copiá los respaldos a un disco externo o nube privada.

---

## Seguridad

- Claves (`SECRET_KEY`, `JWT_SECRET_KEY`) fuera del repositorio, obligatorias y
  validadas en producción.
- `backend/.env`, `frontend/.env`, `venv/`, `node_modules/` y `backups/`
  están en `.gitignore`.
- 2FA obligatorio con Google Authenticator.
- Contraseñas con hashing scrypt.
- El webhook de Pagopar valida la autenticidad con token SHA1.
- Soft-delete por campo `estado`/`activo` en lugar de borrado físico.

---

## Documentación adicional

- `INSTRUCTIVO.md` — guía operativa paso a paso (ejecución, Pagopar, backups).
- `DICCIONARIO_DE_DATOS.md` — diccionario de datos.
- `MODELO_LOGICO_ETIQUETAS.md` — modelo lógico.

---

*Sistema Experto de Scoring Comercial — v0.1*
