# Manual Técnico

## Propósito del Documento

El presente manual técnico está dirigido al personal de Tecnologías de la Información (desarrolladores, administradores de sistemas y soporte técnico). Su objetivo es documentar la arquitectura, el stack tecnológico, los servicios (API REST), las validaciones aplicadas y los procedimientos exactos para la configuración, instalación y despliegue del sistema experto de evaluación de riesgo crediticio inmobiliario, tanto en un entorno de desarrollo como de producción.

El sistema es una plataforma **SaaS multi-empresa (multi-tenant)**: un mismo despliegue atiende a varias empresas inmobiliarias, aislando sus datos mediante el identificador de empresa (`id_empresa`). Existe un **propietario del sistema** (operador de la plataforma) y, por cada empresa cliente, usuarios con rol administrador o comercial.

---

## Arquitectura

El sistema fue construido bajo una arquitectura **Cliente-Servidor separada**, implementando el patrón de diseño **API RESTful**.

- **Frontend (Capa de Presentación):** Desarrollado como una Single Page Application (SPA) en React, responsable de la renderización dinámica de las interfaces de usuario en el navegador del cliente y de la gestión del estado de la aplicación (autenticación mediante React Context + `localStorage`).
- **Backend (Capa de Lógica y Datos):** Un servidor web independiente y sin estado (*stateless*) construido en Flask, que expone los *endpoints* (API REST) para procesar las reglas de negocio, validar permisos por rol, ejecutar los motores de inferencia de scoring y comunicarse con el motor de base de datos.
- **Base de Datos (Capa de Persistencia):** Motor PostgreSQL, accedido a través del ORM Flask-SQLAlchemy. Incluye *triggers* de auditoría a nivel de base de datos que distinguen las operaciones realizadas por la aplicación de las realizadas directamente sobre el motor.

### Patrón de diseño del backend

El backend aplica el patrón **Application Factory** (`create_app`) y organiza la lógica en **blueprints** (un módulo por dominio de negocio). Cada blueprint se registra bajo el prefijo `/api/<dominio>`. Los módulos con lógica de cálculo (evaluación por criterios y scoring experto) cuentan con un `engine.py` adicional que encapsula el motor de inferencia.

### Diagrama lógico

```
┌──────────────────────┐      HTTPS / JSON       ┌───────────────────────────┐
│   Frontend (SPA)     │  ───────────────────►   │   Backend REST (Flask)    │
│   React 18 + Vite    │   Authorization: Bearer │   Application Factory     │
│   Axios interceptors │  ◄───────────────────   │   Blueprints /api/*       │
└──────────────────────┘   {success,message,data}│   JWT + 2FA TOTP          │
                                                  │   Motores de scoring      │
                                                  └────────────┬──────────────┘
                                                               │ SQLAlchemy (psycopg3)
                                                               ▼
                                                  ┌───────────────────────────┐
                                                  │   PostgreSQL 15            │
                                                  │   inmobiliaria_db          │
                                                  │   + triggers de auditoría  │
                                                  └───────────────────────────┘
```

---

## Tecnologías y Herramientas

### Backend / API

| Componente | Tecnología / Versión |
|------------|----------------------|
| Lenguaje | Python 3.x |
| Framework | Flask 3.1.0 (patrón Application Factory) |
| ORM | Flask-SQLAlchemy 3.1.1 |
| Driver de BD | psycopg (v3) `psycopg[binary]==3.2.3` |
| Autenticación | Flask-JWT-Extended 4.6.0 (access 8 h / refresh 30 d) |
| Segundo factor (2FA) | pyotp 2.9.0 + qrcode[pil] 7.4.2 (TOTP / Google Authenticator) |
| CORS | Flask-CORS 4.0.0 |
| Validación | Validación manual + validador propio del Core de scoring (marshmallow 3.21.3 declarado) |
| Generación de PDF | reportlab 4.2.2 |
| Variables de entorno | python-dotenv 1.0.1 |
| Hashing de contraseñas | werkzeug.security 3.1.3 |
| Pasarela de pagos | Pagopar (Paraguay) vía `requests` 2.32.3 |
| Servidor WSGI (producción) | gunicorn 23.0.0 |

### Frontend / UI

| Componente | Tecnología / Versión |
|------------|----------------------|
| Framework | React 18.3 (JSX, sin TypeScript) |
| Build tool | Vite 5.4 |
| Routing | react-router-dom 6 |
| Cliente HTTP | Axios con interceptores (refresco automático de token) |
| Formularios | react-hook-form |
| Estilos | TailwindCSS 3.4 + PostCSS + Autoprefixer |
| Iconos | lucide-react |
| Gráficos | Recharts |
| Notificaciones | react-hot-toast |
| Estado global | React Context (AuthContext) |

### Base de Datos

- **Motor:** PostgreSQL 15.x.
- **Conexión:** mediante el driver `psycopg` v3. La URI se construye con el esquema `postgresql+psycopg://`.
- **Base de datos por defecto:** `inmobiliaria_db`.
- **Migraciones:** scripts SQL manuales en `backend/migrations/` (no se usa Alembic).
- **Nomenclatura:** nombres de tablas y campos de dominio en español.
- **Auditoría:** las conexiones de la aplicación se marcan con `SET app.origen = 'APP'` para que los *triggers* de auditoría distingan el origen de cada operación.

> **Nota de dominio:** el sistema está adaptado al contexto de **Paraguay**. Los tipos de documento de cliente son `CI`, `RUC` y `PAS`; los montos se expresan en guaraníes (Gs); el catálogo territorial corresponde a departamentos y ciudades de Paraguay; y la pasarela de pagos integrada es Pagopar.

---

## Modelo de Seguridad y Roles

### Autenticación sin estado (JWT)

Las sesiones no se guardan en el servidor. Tras autenticarse, el sistema emite un **JSON Web Token (JWT)** de acceso con expiración de **8 horas** y un token de refresco con expiración de **30 días**. El frontend debe adjuntar el token de acceso en el *header* `Authorization: Bearer <token>` de cada petición protegida.

Los claims relevantes del token de acceso son:
- `auth_state`: `2fa_setup` | `2fa_pending` | `authenticated`.
- `2fa`: booleano que indica si el segundo factor ya fue superado.
- `identity`: el `id` del usuario (como cadena).

### Segundo factor obligatorio (2FA / TOTP)

El inicio de sesión aplica autenticación en dos pasos basada en **TOTP** (compatible con Google Authenticator). En el primer login el sistema genera un secreto, entrega un código QR en base64 y exige validar un código de 6 dígitos para activar el 2FA. En logins posteriores se exige el código OTP antes de emitir los tokens completos.

### Cifrado de credenciales

Las contraseñas se almacenan en PostgreSQL en forma de *hash* generado con `werkzeug.security.generate_password_hash` (algoritmo por defecto de Werkzeug, no reversible). Nunca se almacena ni se devuelve la contraseña en texto plano.

### Roles del sistema

| Rol | Valor interno | Alcance |
|-----|---------------|---------|
| Propietario del sistema | `propietario` (con `id_empresa = 0`) | Acceso total: gestiona empresas, planes de facturación, motores/modelos de scoring y ve datos de todas las empresas. |
| Administrador de empresa | `administrador` | Gestiona los usuarios y datos de **su** empresa, configura evaluaciones y consulta auditoría de su empresa. |
| Comercial | `comercial` | Registra clientes, ejecuta evaluaciones y consulta reportes de su empresa. |

**Decoradores de autorización** (en `app/utils/decorators.py`):
- `@jwt_required()` — exige un token de acceso válido.
- `@roles_required(*roles)` — restringe a los roles indicados; devuelve 403 si el usuario está inactivo o no tiene el rol.
- `@admin_required` — atajo de `roles_required("propietario", "administrador")`.
- `@propietario_required` — acceso exclusivo del propietario del sistema (`is_propietario()` = rol `propietario` **y** `id_empresa == 0`).

### Aislamiento multi-tenant

El propietario ve y gestiona todos los registros. Los usuarios de empresa solo acceden a los datos filtrados por su `id_empresa` (directamente o a través de la tabla puente `cliente_empresa`).

### Protección CORS

En **producción**, el backend restringe las peticiones a los orígenes definidos en `CORS_ORIGINS` o `FRONTEND_URL` (separados por coma). En **desarrollo**, se permite cualquier origen para comodidad de trabajo local.

### Protección de variables de entorno

Los archivos `.env` (con cadenas de conexión y claves secretas) están excluidos del control de versiones mediante `.gitignore`. En producción, `SECRET_KEY` y `JWT_SECRET_KEY` son obligatorias y deben tener al menos 32 caracteres (la aplicación aborta el arranque si no se cumplen).

---

## Convenciones de la API

### Formato de respuesta estándar

Todas las respuestas JSON siguen esta estructura:

```json
{
  "success": true,
  "message": "Texto descriptivo",
  "data": { }
}
```

En caso de error:

```json
{
  "success": false,
  "message": "Descripción del error",
  "details": "opcional"
}
```

### Códigos HTTP utilizados

| Código | Significado en el sistema |
|--------|---------------------------|
| 200 | Operación exitosa |
| 201 | Recurso creado correctamente |
| 400 | Datos inválidos o campos obligatorios faltantes |
| 401 | No autenticado / credenciales u OTP incorrectos |
| 403 | Autenticado pero sin permisos (rol o empresa) |
| 404 | Recurso no encontrado |
| 409 | Conflicto (dato duplicado: documento, email, RUC) |
| 500 | Error interno del servidor |
| 502 / 503 | Error o indisponibilidad de la pasarela de pagos |

### Paginación estándar

Los endpoints de listado paginados aceptan los parámetros de consulta `page` (por defecto 1) y `per_page` (por defecto 20, salvo auditoría que usa 25). La respuesta tiene la forma:

```json
{
  "items": [ ],
  "total": 120,
  "page": 1,
  "pages": 6,
  "per_page": 20
}
```

### Health check

- `GET /api/health` → `{ "status": "ok", "env": "development" }`. No requiere autenticación.

---

## Catálogo de Servicios (API REST)

Base de la API: todos los endpoints cuelgan del prefijo `/api`. La columna **Seguridad** indica el decorador aplicado.

### 1. Autenticación — `/api/auth`

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| POST | `/login` | Pública | Inicia sesión; devuelve el estado de 2FA (`2fa_setup_required`, `2fa_required`) o autenticado. |
| POST | `/2fa/setup` | Token parcial `2fa_setup` | Valida el primer OTP y activa el 2FA; devuelve tokens completos. |
| POST | `/2fa/verify` | Token parcial `2fa_pending` | Valida el OTP en cada login; devuelve tokens completos. |
| POST | `/2fa/reset/<user_id>` | `@jwt_required()` | Restablece el 2FA de un usuario (propietario o admin de la misma empresa). |
| POST | `/change-password` | `@jwt_required()` | Cambia la contraseña del usuario autenticado. |
| POST | `/forgot-password` | Pública | Restablece la contraseña validando OTP (solo usuarios con 2FA activo). |
| POST | `/refresh` | `@jwt_required(refresh=True)` | Emite un nuevo token de acceso. |
| GET | `/me` | `@jwt_required()` | Devuelve los datos del usuario autenticado. |
| POST | `/logout` | `@jwt_required()` | Cierra la sesión (registra auditoría). |
| GET | `/security/users` | Admin (`is_admin`) | Lista usuarios con su estado de 2FA. |

**Campos y validaciones principales:**

| Endpoint | Campo | Obligatorio | Validación |
|----------|-------|-------------|------------|
| `/login` | `email` | Sí | No vacío; se normaliza a minúsculas |
| `/login` | `password` | Sí | No vacío; se compara contra el hash. Credenciales incorrectas → 401. Usuario inactivo → 403 |
| `/2fa/setup`, `/2fa/verify` | `codigo` | Sí | Exactamente 6 dígitos; OTP válido contra el secreto TOTP (401 si no) |
| `/change-password` | `current_password` | Sí | Debe coincidir con la actual (401 si no) |
| `/change-password` | `new_password` | Sí | Longitud mínima 8 caracteres |
| `/change-password` | `confirm_password` | Sí | Debe ser igual a `new_password` |
| `/forgot-password` | `email`, `codigo`, `new_password`, `confirm_password` | Sí | OTP válido; longitud ≥ 8; coincidencia de confirmación. Mensaje genérico para no revelar la existencia del email |

### 2. Clientes — `/api/clients`

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/` | `@jwt_required()` | Lista paginada de clientes (filtra por empresa salvo propietario). |
| GET | `/<client_id>` | `@jwt_required()` | Detalle del cliente, incluye sus documentos. |
| POST | `/` | `@jwt_required()` | Registra un cliente nuevo o lo vincula a la empresa si ya existe. |
| PUT | `/<client_id>` | `@jwt_required()` | Actualiza datos del cliente (audita campos cambiados). |
| DELETE | `/<client_id>` | `@jwt_required()` | Soft-delete: desvincula/inactiva al cliente. |
| GET | `/paises` | `@jwt_required()` | Catálogo de países. |
| GET | `/departamentos` | `@jwt_required()` | Catálogo de departamentos (Paraguay). |
| GET | `/departamentos/<depto_id>/ciudades` | `@jwt_required()` | Ciudades de un departamento. |

**Parámetros de consulta del listado (`GET /`):** `page`, `per_page`, `search` (búsqueda OR por nombre/apellido/num_doc/email), `num_doc`, `nombre`, `apellido` (filtros AND tipo *contiene*).

**Campos del cliente (`POST /` y `PUT /`):**

| Campo | Tipo | Obligatorio | Validación funcional / de servicio |
|-------|------|-------------|-------------------------------------|
| `tipo_doc` | string | **Sí** | Debe ser uno de `CI`, `RUC`, `PAS` |
| `num_doc` | string | **Sí** | Único en el sistema. Si ya existe se vincula a la empresa (409 si ya está vinculado activo) |
| `nombre` | string | **Sí** | No vacío |
| `apellido` | string | No | — |
| `email` | string | No | Se normaliza; se guarda `null` si viene vacío |
| `telefono` | string | No | Solo dígitos y símbolos `+ - ( ) espacio` (expresión regular `^[0-9+\-\s()]+$`); no admite letras |
| `direccion` | string | No | — |
| `fecha_nacimiento` | string (YYYY-MM-DD) | No | Formato ISO; no puede ser futura; el cliente debe ser **mayor de edad** (edad mínima 18) |
| `nacionalidad` | string | No | FK a país |
| `id_ciudad` | int | No | FK a ciudad |
| `id_empresa` | int | No | Solo el propietario puede indicarlo; para los demás se toma su propia empresa |

### 3. Evaluación por Criterios Ponderados — `/api/evaluations`

Sistema de evaluación por criterios configurables con peso. El motor (`engine.py`) normaliza cada valor a 0–100, lo pondera por el peso del criterio activo y normaliza por el peso total. Umbrales de resultado: **≥ 70 → aprobado**, **≥ 50 → observado**, **< 50 → rechazado**.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/criteria` | `@jwt_required()` | Lista de criterios. |
| POST | `/criteria` | `@admin_required` | Crea un criterio. |
| PUT | `/criteria/<criterion_id>` | `@admin_required` | Edita un criterio. |
| GET | `/` | `@jwt_required()` | Lista paginada de evaluaciones (filtros `cliente_id`, `resultado`). |
| GET | `/<eval_id>` | `@jwt_required()` | Detalle de la evaluación con sus detalles y datos del cliente. |
| POST | `/` | `@jwt_required()` | Registra una evaluación por criterios. |
| PUT | `/<eval_id>` | `@jwt_required()` | Actualiza observaciones/estado. |

**Validaciones:**

| Endpoint | Campo | Obligatorio | Validación |
|----------|-------|-------------|------------|
| `POST /criteria` | `nombre` | Sí | No vacío |
| `POST /criteria` | `peso` | Sí | Numérico `0 < peso ≤ 100` |
| `POST /criteria` | `descripcion` | No | — |
| `POST /` | `cliente_id` | Sí | El cliente debe existir (404 si no) |
| `POST /` | `detalles` | Sí | Lista de `{criterio_id, valor, comentario?}`; cada `valor` se acota al rango 0–100 |
| `POST /` | `observaciones` | No | — |

### 4. Scoring Experto IF-THEN (motor de reglas v1) — `/api/scoring`

Motor de inferencia basado en reglas IF-THEN. Operadores soportados: `>=`, `<=`, `==`, `>`, `<`, `!=`. Tipos de valor: `numerico`, `texto`, `booleano`. Las reglas marcadas como **determinantes** provocan un rechazo inmediato si no se cumplen. La clasificación se obtiene por porcentaje sobre el puntaje máximo: **≥ 75 % → bajo**, **≥ 50 % → medio**, **< 50 % → alto**, regla determinante fallida → **rechazado**.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/motores` | `@jwt_required()` | Lista de motores de reglas. |
| GET | `/motores/<id>` | `@jwt_required()` | Detalle del motor con sus reglas. |
| POST | `/motores` | `@admin_required` + propietario | Crea un motor (solo el propietario). |
| PUT | `/motores/<id>` | `@admin_required` + propietario | Edita un motor. |
| PATCH | `/motores/<id>/toggle` | `@admin_required` | Activa/desactiva el motor. |
| GET | `/motores/<id>/reglas` | `@jwt_required()` | Lista de reglas del motor. |
| POST | `/motores/<id>/reglas` | `@admin_required` + propietario | Crea una regla. |
| PUT | `/reglas/<id>` | `@admin_required` | Edita una regla. |
| PATCH | `/reglas/<id>/toggle` | `@admin_required` | Activa/desactiva la regla. |
| DELETE | `/reglas/<id>` | `@admin_required` | Elimina la regla. |
| GET | `/historial/<cliente_id>` | `@jwt_required()` | Historial crediticio del cliente. |
| PUT | `/historial/<cliente_id>` | `@jwt_required()` | Crea/actualiza (upsert) el historial crediticio. |
| POST | `/evaluar` | `@jwt_required()` | Ejecuta el motor de reglas sobre un cliente. |
| GET | `/evaluaciones` | `@jwt_required()` | Lista paginada de evaluaciones de riesgo. |
| GET | `/evaluaciones/<id>` | `@jwt_required()` | Detalle de una evaluación con recomendación. |
| GET | `/parametros` | `@jwt_required()` | Parámetros y operadores disponibles. |

**Validaciones de reglas (`POST /motores/<id>/reglas`):**

| Campo | Obligatorio | Validación |
|-------|-------------|------------|
| `nombre` | Sí | No vacío |
| `parametro` | Sí | Debe pertenecer al catálogo de parámetros del motor |
| `operador` | Sí | Debe pertenecer a `>=, <=, ==, >, <, !=` |
| `valor_referencia` | Sí | Se almacena como texto; se castea según `tipo_valor` |
| `peso_puntos` | Sí | Número **positivo** (> 0) |
| `tipo_valor` | No | Autodetectado por el parámetro si no se envía |
| `es_determinante`, `activo` | No | Booleanos |
| `orden` | No | Entero |

**Validaciones de la evaluación (`POST /evaluar`):**

| Campo | Obligatorio | Validación |
|-------|-------------|------------|
| `cliente_id` | Sí | El cliente debe existir (404 si no) |
| `motor_id` | Sí | El motor debe existir y estar **activo** (400 si no) |
| `hechos` | Sí | Diccionario con los valores del cliente; se enriquece con el historial y la edad calculada |
| `observaciones` | No | — |
| `operacion` | No | Objeto con `tipo_propiedad`, `valor_propiedad`, `monto_solicitado`, `plazo_meses`, `ubicacion`, `destino` |

### 5. Core de Scoring (motor configurable v2) — `/api/core`

Motor de decisión por **factores → reglas → niveles → pesos → score → clasificación → explicación**, configurable por empresa. Es el motor que consumen los módulos de reportes y de facturación. Verifica además listas negras internacionales (ONU/OFAC) y genera PDF por evaluación.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| POST | `/evaluar` | `@jwt_required()` | Ejecuta el modelo de scoring sobre un cliente y registra consumo de facturación. |
| GET | `/evaluaciones` | `@jwt_required()` | Lista paginada (filtro `clasificacion`). |
| GET | `/evaluaciones/<id>` | `@jwt_required()` | Detalle con impacto de factores. |
| GET | `/evaluaciones/<id>/pdf` | `@jwt_required()` | Genera el PDF de la evaluación. |
| GET | `/verificar-lista-negra/<cliente_id>` | `@jwt_required()` | Verifica al cliente contra la lista negra. |
| GET | `/modelos` | `@jwt_required()` | Lista de modelos de scoring. |
| GET | `/modelos/<id>` | `@jwt_required()` | Detalle del modelo con factores. |
| POST | `/modelos` | `@propietario_required` | Crea un modelo (opcionalmente a partir de una plantilla). |
| POST | `/modelos/clonar` | `@propietario_required` | Clona un modelo completo. |
| DELETE | `/modelos/<id>` | `@propietario_required` | Elimina (físico si no tiene evaluaciones; soft-delete si las tiene). |
| POST | `/modelos/<id>/factores` | `@propietario_required` | Agrega un factor al modelo. |
| POST | `/factores/<id>/reglas` | `@propietario_required` | Agrega una regla a un factor. |
| POST | `/modelos/<id>/umbrales` | `@propietario_required` | Define los umbrales de clasificación. |

**Validaciones de la evaluación (`POST /evaluar`):**

| Campo | Obligatorio | Validación |
|-------|-------------|------------|
| `cliente_id` | Sí | El cliente debe existir (404 si no) |
| `modelo_id` | Sí | El modelo debe existir y estar **activo** (400 si no) |
| `datos` | Sí | Diccionario `{codigo_factor: valor}`; validado por tipo (numérico, porcentaje 0–100, booleano, catálogo, texto), no negativos y opciones de catálogo válidas |
| `tipo_persona` | No | `PF` o `PJ`; se autodetecta (`RUC` → PJ, resto → PF) |

> Si la empresa tiene las consultas bloqueadas por deuda, la evaluación responde **403** (control del servicio de facturación).

**Validaciones de modelo/factor/regla:**

| Endpoint | Campos obligatorios | Observaciones |
|----------|---------------------|---------------|
| `POST /modelos` | `nombre`, `id_empresa` | Opcional `base_modelo_id` (plantilla por defecto id=1) |
| `POST /modelos/clonar` | `origen_id`, `id_empresa` | Clona factores, catálogos, reglas y umbrales |
| `POST /modelos/<id>/factores` | `codigo`, `nombre`, `tipo_dato` | `tipo_persona` por defecto `AMBOS`; `obligatorio` por defecto `true` |
| `POST /factores/<id>/reglas` | `nombre`, `operador`, `nivel`, `peso` | `nivel` ∈ `bajo/medio/alto`; peso positivo=desfavorable, negativo=favorable |

### 6. Reportes — `/api/reports`

Opera sobre las evaluaciones del Core (v2). Multi-tenant por `id_empresa` (el propietario ve todas las empresas).

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/summary` | `@jwt_required()` | Totales del dashboard: evaluaciones, por nivel de riesgo, rechazados, clientes. |
| GET | `/evaluations` | `@jwt_required()` | Listado de evaluaciones (con filtros). |
| GET | `/evaluations/pdf` | `@jwt_required()` | Exporta el listado como PDF (A4 horizontal). |

**Filtros de consulta:** `fecha_from`, `fecha_to` (ISO), `resultado` o `categoria` (nivel de riesgo), `evaluador_id`.

### 7. Empresas — `/api/empresas`

Gestión de empresas cliente y de sus usuarios. **Todos los endpoints requieren `@propietario_required`** salvo donde se indique.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/` | `@propietario_required` | Lista de empresas. |
| GET | `/<id>` | `@propietario_required` | Detalle de la empresa con sus usuarios. |
| POST | `/` | `@propietario_required` | Crea una empresa. |
| PUT | `/<id>` | `@propietario_required` | Edita una empresa. |
| PATCH | `/<id>/toggle` | `@propietario_required` | Activa/desactiva la empresa. |
| GET | `/<id>/usuarios` | `@propietario_required` | Usuarios de la empresa. |
| POST | `/<id>/usuarios` | `@propietario_required` | Crea un usuario de empresa. |
| PUT | `/usuarios/<user_id>` | `@propietario_required` | Edita un usuario (no al propietario, 403). |
| PATCH | `/usuarios/<user_id>/toggle` | `@propietario_required` | Activa/desactiva un usuario. |

**Validaciones:**

| Endpoint | Campo | Obligatorio | Validación |
|----------|-------|-------------|------------|
| `POST /` | `nombre` | Sí | No vacío |
| `POST /` | `ruc` | No | Único (409 si duplicado) |
| `POST /` | `direccion`, `telefono`, `email` | No | — |
| `POST /<id>/usuarios` | `nombre`, `apellido`, `email`, `password` | Sí | `email` único (409) |
| `POST /<id>/usuarios` | `rol` | No | `administrador` o `comercial` (por defecto `comercial`) |

### 8. Facturación — `/api/facturacion`

Modelo prepago por reportes consumidos, con planes, períodos mensuales y pagos (modo TEST o pasarela Pagopar). El consumo bloquea/desbloquea automáticamente las consultas de la empresa según su saldo.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/planes` | `@jwt_required()` | Planes activos. |
| POST | `/planes` | `@propietario_required` | Crea un plan. |
| PUT | `/planes/<id>` | `@propietario_required` | Edita un plan. |
| GET | `/mi-plan` | `@jwt_required()` | Plan y consumo del período actual de la empresa. |
| GET | `/mi-historial` | `@jwt_required()` | Historial de períodos de facturación. |
| POST | `/pagos` | `@jwt_required()` | Crea una transacción de pago (modo TEST). |
| POST | `/pagos/<id>/test-aprobar` | `@jwt_required()` | Aprueba un pago de prueba y desbloquea la empresa. |
| POST | `/pagos/<id>/test-rechazar` | `@jwt_required()` | Rechaza un pago de prueba. |
| GET | `/pagos` | `@jwt_required()` | Lista de pagos. |
| GET | `/pagopar/estado` | `@jwt_required()` | Estado de la integración Pagopar. |
| POST | `/pagos/pagopar/iniciar` | `@jwt_required()` | Inicia un pago real en Pagopar. |
| POST | `/pagopar/webhook` | Pública (token SHA1 de Pagopar) | Notificación de pago desde Pagopar. |
| GET | `/admin/empresas` | `@propietario_required` | Vista de facturación de todas las empresas. |
| POST | `/admin/empresas/<id>/asignar-plan` | `@propietario_required` | Asigna un plan a una empresa. |
| POST | `/admin/empresas/<id>/bloquear` | `@propietario_required` | Bloquea las consultas de una empresa. |
| POST | `/admin/empresas/<id>/desbloquear` | `@propietario_required` | Desbloquea las consultas de una empresa. |

**Validaciones:**

| Endpoint | Campos obligatorios | Observaciones |
|----------|---------------------|---------------|
| `POST /planes` | `nombre`, `cantidad_reportes_incluidos`, `precio_plan`, `precio_reporte_sobre_facturado` | Montos en Gs (enteros) |
| `POST /pagos` | `periodo_facturacion_id` | Valida que el período sea de la empresa del usuario (403 si no). `monto` opcional (por defecto el saldo pendiente) |
| `POST /admin/empresas/<id>/asignar-plan` | `plan_id` | Finaliza el plan anterior y crea el nuevo con copia de precios |

### 9. Auditoría — `/api/auditoria`

Consulta de la bitácora de eventos del sistema (solo lectura). Acceso para administradores (`is_admin`); el propietario ve todas las empresas, el administrador solo la suya.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/` | Admin | Lista paginada de eventos (por defecto `per_page = 25`). |
| GET | `/filtros` | Admin | Catálogos para los filtros (tipos de evento, resultados, acciones, módulos). |

**Filtros de consulta:** `fecha_from`, `fecha_to` (YYYY-MM-DD; 400 si el formato es inválido), `usuario_id`, `tipo_evento`, `accion`, `modulo`, `resultado` (`EXITO`/`FALLO`), `id_empresa` (solo propietario), `search`.

**Tipos de evento auditados:** `AUTENTICACION`, `SEGURIDAD`, `USUARIOS`, `EMPRESAS`, `CLIENTES`, `EVALUACIONES`, `FACTURACION`.

### 10. Usuarios — `/api/users`

Módulo administrativo de usuarios. Todos los endpoints usan `@admin_required`. La gestión operativa de usuarios de empresa se realiza preferentemente desde el módulo **Empresas**.

| Método | Ruta | Seguridad | Descripción |
|--------|------|-----------|-------------|
| GET | `/` | `@admin_required` | Lista de usuarios. |
| GET | `/<user_id>` | `@admin_required` | Detalle del usuario. |
| POST | `/` | `@admin_required` | Crea un usuario (`email` único → 409). |
| PUT | `/<user_id>` | `@admin_required` | Edita el usuario. |
| PATCH | `/<user_id>/toggle` | `@admin_required` | Activa/desactiva el usuario. |

---

## Resumen de Validaciones a Nivel de Servicio

| Tipo de validación | Dónde se aplica | Comportamiento |
|--------------------|-----------------|----------------|
| **Campos obligatorios** | Todos los POST/PUT con cuerpo | Responde 400 con el mensaje `Campos requeridos: ...` listando los faltantes |
| **Autenticación** | Endpoints protegidos | 401 si falta o es inválido el token |
| **Autorización por rol** | Decoradores `admin_required`, `propietario_required`, `roles_required` | 403 si el rol no corresponde o el usuario está inactivo |
| **Aislamiento por empresa** | Clientes, evaluaciones, reportes, auditoría, facturación | Filtro automático por `id_empresa`; el propietario ve todo |
| **Unicidad** | `num_doc` (cliente), `email` (usuario), `ruc` (empresa) | 409 cuando ya existe |
| **Formato de documento** | `tipo_doc` del cliente | Solo `CI`, `RUC`, `PAS` |
| **Formato de teléfono** | `telefono` del cliente | Solo dígitos y `+ - ( ) espacio` |
| **Edad mínima** | `fecha_nacimiento` del cliente | Debe ser mayor de edad (≥ 18) y no futura |
| **Rangos numéricos** | `peso` de criterio (0–100), `peso_puntos` de regla (> 0), valores de detalle (0–100) | 400 si fuera de rango |
| **Enumeraciones** | Operadores de regla, niveles, tipos de persona, estados de pago | 400 si el valor no pertenece al conjunto permitido |
| **Estado del motor/modelo** | Evaluaciones | 400 si el motor/modelo no está activo |
| **Facturación / bloqueo** | Core `/evaluar` | 403 si la empresa tiene las consultas bloqueadas por deuda |
| **Segundo factor (OTP)** | Login y recuperación | Código de 6 dígitos válido; 401 si es incorrecto |

---

## Configuración del Entorno

Para desplegar la aplicación en un nuevo servidor o estación de trabajo, el equipo debe contar obligatoriamente con el siguiente software instalado:

- **Python 3.x** y el gestor de paquetes `pip`.
- **Node.js** (v18.x o superior) y su gestor de paquetes **npm**.
- **Servidor PostgreSQL 15.x** ejecutándose localmente o en red, con la base de datos `inmobiliaria_db` creada.
- **Git** (para el control de versiones y la clonación del proyecto).

---

## Instalación y Plan de Despliegue

### Paso 1: Clonación del Repositorio

Descargar el código fuente en el directorio local:

```bash
git clone [URL_DEL_REPOSITORIO]
cd V.0.1
```

### Paso 2: Despliegue y Configuración del Backend (API)

1. Navegar a la carpeta del backend:
   ```bash
   cd backend
   ```
2. (Recomendado) Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Linux / macOS:
   source venv/bin/activate
   ```
3. Instalar las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```
4. Crear el archivo de variables de entorno `.env` en la raíz del backend (puede copiarse de `.env.example`) con las credenciales de conexión:
   ```env
   FLASK_ENV=development

   # Claves secretas (obligatorias y >= 32 caracteres en producción)
   SECRET_KEY=clave_aleatoria_de_al_menos_32_caracteres
   JWT_SECRET_KEY=otra_clave_aleatoria_distinta_de_32_caracteres

   # Opción A: URL completa de conexión
   DATABASE_URL=postgresql+psycopg://inmobiliaria:CAMBIAR@localhost:5432/inmobiliaria_db

   # Opción B: por partes (solo si DATABASE_URL está vacía)
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=inmobiliaria_db
   DB_USER=inmobiliaria
   DB_PASSWORD=CAMBIAR

   FRONTEND_URL=http://localhost:3000
   BACKEND_URL=http://localhost:5000
   ```
   > Para generar claves seguras: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

5. Ejecutar los scripts SQL de migración ubicados en `backend/migrations/` para construir las tablas en la base de datos (p. ej. con `psql` o DBeaver).

6. Ejecutar el *seed* inicial para crear el usuario administrador y los criterios por defecto:
   ```bash
   python seed.py
   ```
   > El *seed* crea el usuario `admin@inmobiliaria.com` con contraseña `Admin@2026` y los criterios base (Capacidad de Pago 25, Historial Crediticio 25, Estabilidad Laboral 20, Documentación 15, Patrimonio 15). **Cambie esta contraseña tras el primer acceso.**

7. Iniciar el servidor backend:
   ```bash
   python run.py
   ```
   El servidor quedará a la escucha en el puerto **5000** (`http://localhost:5000`). En producción se recomienda ejecutarlo con **gunicorn**.

### Paso 3: Despliegue del Frontend (Cliente Web)

1. Abrir una nueva terminal y navegar a la carpeta del cliente:
   ```bash
   cd frontend
   ```
2. Instalar las dependencias:
   ```bash
   npm install
   ```
3. Crear el archivo `.env` del cliente apuntando a la API:
   ```env
   VITE_API_URL=http://localhost:5000/api
   ```
4. Compilar y ejecutar el entorno de desarrollo:
   ```bash
   npm run dev
   ```
   La aplicación quedará disponible en el navegador en el puerto **3000** (`http://localhost:3000`), con *proxy* hacia el backend en el puerto 5000.

5. Para generar la compilación de producción:
   ```bash
   npm run build
   ```

---

## Seguridad Mínima Aplicada

El entorno de despliegue cuenta con las siguientes políticas de seguridad técnica activas:

- **Autenticación sin estado (JWT):** las sesiones no se guardan en el servidor. El sistema emite un token de acceso (8 h) que el frontend adjunta en el *header* `Authorization: Bearer <token>` de cada petición, y un token de refresco (30 d).
- **Segundo factor obligatorio (2FA / TOTP):** cada usuario debe configurar y usar un código temporal de 6 dígitos (Google Authenticator) para iniciar sesión.
- **Cifrado de credenciales:** las contraseñas se almacenan en PostgreSQL como *hash* no reversible generado con Werkzeug; nunca se devuelven en texto plano.
- **Autorización por rol y por empresa:** cada endpoint valida el rol del usuario (propietario, administrador, comercial) y aísla los datos por `id_empresa`.
- **Protección CORS:** en producción el backend rechaza peticiones de dominios no incluidos en `CORS_ORIGINS` / `FRONTEND_URL`.
- **Protección de variables de entorno:** los archivos `.env` están excluidos del control de versiones (`.gitignore`); en producción las claves secretas son obligatorias y de longitud mínima 32 caracteres.
- **Auditoría integral:** todas las operaciones sensibles (autenticación, usuarios, empresas, clientes, evaluaciones, facturación) quedan registradas en la bitácora, reforzada con *triggers* a nivel de base de datos.
- **Endurecimiento de cookies:** `HttpOnly`, `SameSite=Lax` y `Secure` activo en producción.
```
