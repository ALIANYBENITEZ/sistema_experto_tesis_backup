# Estructura del Proyecto

```
V.0.1/
├── backend/                    # API REST Flask
│   ├── app/
│   │   ├── __init__.py         # Application Factory (create_app)
│   │   ├── config.py           # Configuración por entorno (dev/prod)
│   │   ├── extensions.py       # Instancias de SQLAlchemy, JWT, CORS
│   │   ├── blueprints/         # Módulos de la API (un blueprint por dominio)
│   │   │   ├── auth/           # Login, refresh, logout, me
│   │   │   ├── clients/        # CRUD clientes
│   │   │   ├── evaluation/     # Evaluación por criterios ponderados + engine
│   │   │   ├── reports/        # Reportes y PDF
│   │   │   ├── scoring/        # Motor de reglas IF-THEN + engine
│   │   │   └── users/          # Gestión de usuarios (admin)
│   │   ├── models/             # Modelos SQLAlchemy (tablas en español)
│   │   │   ├── user.py         # Tabla: usuarios
│   │   │   ├── client.py       # Tabla: clientes
│   │   │   ├── evaluation.py   # Tablas: criterios, evaluaciones, evaluacion_detalle
│   │   │   ├── scoring.py      # Tablas: motor_reglas, reglas, historial_crediticio, evaluacion_riesgo
│   │   │   └── document.py     # Tabla: documentos
│   │   └── utils/
│   │       ├── decorators.py   # @admin_required, @roles_required
│   │       └── responses.py    # success(), error() helpers
│   ├── migrations/             # Scripts SQL manuales para SQL Server
│   ├── run.py                  # Entrypoint (puerto 5000)
│   ├── seed.py                 # Seed de datos iniciales
│   └── requirements.txt
│
├── frontend/                   # SPA React + Vite
│   ├── src/
│   │   ├── main.jsx            # Entrypoint (BrowserRouter, Toaster)
│   │   ├── App.jsx             # Rutas y layout principal
│   │   ├── api/                # Capa de servicios HTTP
│   │   │   ├── axiosConfig.js  # Instancia Axios con interceptors
│   │   │   └── authApi.js      # Funciones de auth
│   │   ├── components/         # Componentes compartidos
│   │   │   ├── Layout.jsx      # Sidebar + topbar + Outlet
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/            # React Context
│   │   │   └── AuthContext.jsx
│   │   └── pages/              # Páginas por feature (carpeta por módulo)
│   │       ├── Login/
│   │       ├── Dashboard/
│   │       ├── Clients/
│   │       ├── Evaluations/
│   │       ├── Scoring/
│   │       ├── Reports/
│   │       └── Users/
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
└── credit-scoring/             # Prototipo standalone (Flask + Jinja2)
    ├── app.py
    ├── templates/
    └── static/
```

## Convenciones de arquitectura

### Backend
- Cada blueprint tiene su propia carpeta con `__init__.py` (registra el blueprint) y `routes.py`.
- Los blueprints con lógica de cálculo tienen un `engine.py` adicional.
- Todas las rutas están bajo el prefijo `/api/<blueprint_name>`.
- Respuestas JSON normalizadas: `{"success": bool, "message": str, "data": ...}`.
- Paginación estándar con `page`, `per_page` → respuesta con `items`, `total`, `page`, `pages`.
- Modelos exponen `to_dict()` para serialización.
- Nombres de tablas y campos de dominio en español.
- Soft-delete via campo `estado` (activo/inactivo) en lugar de DELETE físico.
- Roles: `administrador`, `operador`.

### Frontend
- Cada módulo de página va en su carpeta dentro de `pages/` (ej: `pages/Scoring/`).
- Servicios API en `src/api/` separados por dominio.
- Autenticación mediante Context + localStorage (access_token, refresh_token).
- TailwindCSS con paleta custom `primary-*`.
- Rutas protegidas con `ProtectedRoute` (soporte `adminOnly`).
- Formularios con react-hook-form.
- Notificaciones con react-hot-toast.
