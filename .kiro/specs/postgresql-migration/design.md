# Diseño Técnico — Migración de SQL Server 2022 a PostgreSQL

## 1. Resumen y objetivo

Migrar el motor de base de datos del sistema de evaluación de clientes (inmobiliaria) de **SQL Server 2022 / pyodbc** a **PostgreSQL**, preservando exactamente la funcionalidad para el usuario final: mismas APIs, mismos códigos HTTP, misma estructura JSON, misma lógica de negocio y mismos resultados del motor de scoring.

La migración NO altera la lógica de negocio ni el frontend. Cambia: capa de conexión, tipos de columna a nivel físico, scripts DDL, triggers de auditoría a nivel BD, mecanismo de marcado de sesión de la aplicación, dependencias, empaquetado (Docker) y preparación para despliegue en Render.

Arquitectura objetivo:

```
React/Vite  →  Flask (Gunicorn)  →  PostgreSQL
```

## 2. Estado actual (inventario de lo afectado)

### 2.1 Conexión y configuración
- `backend/app/config.py`: construye `SQLALCHEMY_DATABASE_URI` con dialecto `mssql+pyodbc`, variables `DB_SERVER`, `DB_NAME`, `DB_DRIVER`, `DB_USER`, `DB_PASSWORD`, soporte de Windows Auth (`trusted_connection=yes`). `SQLALCHEMY_ENGINE_OPTIONS` con `pool_pre_ping` y `pool_recycle`.
- `backend/app/extensions.py`: `db = SQLAlchemy()` (agnóstico, no cambia).
- `backend/.env` y `backend/.env.example`: variables de SQL Server.

### 2.2 Punto crítico: marcado de sesión con `CONTEXT_INFO`
- `backend/app/__init__.py`: listener `@event.listens_for(engine, "checkout")` ejecuta `SET CONTEXT_INFO 0x415050` en cada conexión. Es **100% específico de SQL Server**. Los triggers de auditoría a nivel BD leen ese `CONTEXT_INFO` para NO duplicar lo que ya audita el backend.

### 2.3 Modelos SQLAlchemy (`backend/app/models/` + `backend/app/core/models.py`)
Todos usan tipos portables de SQLAlchemy (`db.Integer`, `db.String`, `db.Numeric`, `db.Boolean`, `db.DateTime`, `db.Date`, `db.Text`), por lo que `db.create_all()` genera DDL válido en PostgreSQL. Tablas: `usuarios`, `empresas`, `clientes`, `cliente_empresa`, `paises`, `departamento`, `ciudad`, `criterios`, `evaluaciones`, `evaluacion_detalle`, `documentos`, `motor_reglas`, `reglas`, `historial_crediticio`, `evaluacion_riesgo`, `resultado_detalle`, `detalle_operacion`, `lista_negra_onu`, `planes`, `empresa_planes`, `periodos_facturacion`, `consumo_reportes`, `pagos`, `historial_empresa_planes`, `auditoria`, y las `scoring_*` del core.

**Detalle relevante:** `User`, `Client`, `Empresa` y `ClienteEmpresa` declaran `__table_args__ = {"implicit_returning": False}`. Esto se agregó para SQL Server porque los triggers rompían la cláusula `OUTPUT` que SQLAlchemy usa para recuperar la PK autogenerada. En PostgreSQL, SQLAlchemy usa `RETURNING`, que **sí es compatible con triggers**, por lo que `implicit_returning=False` deja de ser necesario (aunque no causa error si se deja).

### 2.4 Scripts SQL (`backend/migrations/`)
- `00_script_completo_tesis.sql`: DDL consolidado + los 4 triggers de auditoría (T-SQL).
- `01_create_tables.sql`, `02_database_complete.sql`: DDL con `IDENTITY(1,1)`, `BIT`, `DATETIME2`, `NVARCHAR(MAX)`, `DEFAULT SYSUTCDATETIME()`, `CONCAT`, `ISNULL`, vistas `vw_resumen_evaluaciones`, `vw_dashboard_stats`.
- `03_scoring_module.sql`: tablas de scoring, `SCOPE_IDENTITY()`, `SELECT TOP 1`, vista `vw_evaluaciones_riesgo`, índices con `sys.indexes`.
- `04_update_tipo_doc.sql`: alter de CHECK constraint (`sys.check_constraints`).
- `05_detalle_operacion.sql`: tabla + índice.
- `06_auditoria_triggers.sql`: función `fn_auditoria_es_app` + 4 triggers de auditoría (`trg_aud_usuarios`, `trg_aud_clientes`, `trg_aud_empresas`, `trg_aud_cliente_empresa`) usando `CONTEXT_INFO()`, `SUSER_SNAME()`, `HOST_NAME()`, `PROGRAM_NAME()`, `STRING_ESCAPE`, `SYSUTCDATETIME()`, tablas mágicas `inserted`/`deleted`.
- `07_fk_faltantes.sql`: FKs adicionales usando `sys.foreign_keys`, `sys.key_constraints`, `ALTER COLUMN`.

### 2.5 Consultas del backend
- No hay SQL crudo con dialecto SQL Server en la lógica de la app. La única sentencia cruda es el `SET CONTEXT_INFO` (2.2).
- Paginación con `query.paginate(...)` (Flask-SQLAlchemy, portable).
- Búsquedas con `.ilike(...)` en `lista_negra_checker.py`, `clients/routes.py`, `auditoria/routes.py`. `ILIKE` es nativo de PostgreSQL (case-insensitive real), mientras que en SQL Server dependía del collation `CI` (case-insensitive). Compatible y más explícito en PostgreSQL.
- Filtros de fecha con comparadores estándar (`>=`, `<`), formateo con `strftime` en Python (no en BD). Portable.
- Utilidad de introspección `backend/_gen_docx.py` usa vistas de sistema `sys.indexes`, `sys.foreign_keys` (solo para generar documentación; no es parte del runtime de la app).

### 2.6 Dependencias (`backend/requirements.txt`)
- `pyodbc==5.1.0` → se reemplaza por driver PostgreSQL.
- Resto (`Flask`, `Flask-SQLAlchemy`, `Flask-JWT-Extended`, `Flask-CORS`, `marshmallow`, `Werkzeug`, `reportlab`, `pyotp`, `qrcode`, `requests`, `python-dotenv`) se conserva.
- Falta `gunicorn` para producción.

### 2.7 Empaquetado y despliegue
- `backend/Dockerfile`: instala `msodbcsql17` y `unixodbc-dev` (dependencias de pyodbc). Usa `CMD ["python", "run.py"]` (dev server).
- `docker-compose.yml`: servicio `db` con imagen `mcr.microsoft.com/mssql/server:2022-latest`, variables `DB_*`, volumen `sqlserver_data`.
- `backend/run.py`: `app.run(host="0.0.0.0", port=5000, debug=True)` (dev server, hardcodea puerto).
- Sin configuración de Render.

### 2.8 Scripts operativos (PowerShell)
- `backend/scripts/backup_db.ps1` y `restore_db.ps1`: usan `sqlcmd`, `.bak`, `RESTORE DATABASE`, rutas locales de SQL Server. Son específicos de SQL Server; se sustituyen por equivalentes PostgreSQL (`pg_dump`/`pg_restore`) o se marcan como obsoletos.

### 2.9 Frontend
- `frontend/src/api/axiosConfig.js`, `vite.config.js`, `.env`: agnósticos del motor de BD. Solo dependen de la URL del backend (`VITE_API_URL`). **Sin cambios funcionales.** Se añade `frontend/.env.example`.

### 2.10 Prototipo `credit-scoring/`
- No usa pyodbc ni SQLAlchemy (datos mock). **No afectado.**

### 2.11 Migraciones y pruebas
- No hay Alembic ni Flask-Migrate. La creación de esquema real se hace vía `db.create_all()` en `seed.py`, y los scripts SQL sirven como referencia/instalación manual.
- No hay pruebas automatizadas (`pytest`) en el proyecto.

## 3. Mapeo de tipos de datos SQL Server → PostgreSQL

| SQL Server | PostgreSQL | Notas para este proyecto |
|---|---|---|
| `INT IDENTITY(1,1)` | `INTEGER GENERATED BY DEFAULT AS IDENTITY` (o `SERIAL`) | PK autoincremental. SQLAlchemy lo genera automáticamente desde `db.Integer primary_key`. |
| `INT` | `INTEGER` | Directo. |
| `BIGINT` | `BIGINT` | No usado actualmente, mapeo directo. |
| `SMALLINT` | `SMALLINT` | Directo. |
| `BIT` | `BOOLEAN` | `activo`, `es_determinante`, `en_lista_negra`, etc. SQLAlchemy `db.Boolean` ya lo maneja. Valores `1/0` → `true/false`. |
| `VARCHAR(n)` | `VARCHAR(n)` | Directo. |
| `NVARCHAR(n)` | `VARCHAR(n)` | PostgreSQL es Unicode (UTF-8) nativo; no necesita `N`. |
| `NVARCHAR(MAX)` | `TEXT` | `observaciones` en `evaluaciones`. Modelo ya usa `db.Text`. |
| `CHAR(n)` | `CHAR(n)` | No usado. |
| `TEXT` | `TEXT` | Directo. |
| `DATE` | `DATE` | `fecha_nacimiento`. Directo. |
| `DATETIME` / `DATETIME2` | `TIMESTAMP` (o `TIMESTAMPTZ`) | Ver 3.1. |
| `DECIMAL(p,s)` / `NUMERIC(p,s)` | `NUMERIC(p,s)` | Pesos, scores, montos. Directo (misma precisión). |
| `FLOAT` | `DOUBLE PRECISION` | No usado en modelos. |
| `UNIQUEIDENTIFIER` | `UUID` | No usado en el proyecto. |

### 3.1 Decisión sobre fechas (crítica para no cambiar comportamiento)
El código Python genera las fechas con `datetime.now(timezone.utc)` (aware, UTC) y las serializa con `.isoformat()`. Los defaults SQL usaban `SYSUTCDATETIME()` (UTC). Para preservar el comportamiento exacto:
- Los modelos usan `db.DateTime` → PostgreSQL `TIMESTAMP WITHOUT TIME ZONE`, igual que hoy en SQL Server (`DATETIME2` sin tz). **Se mantiene `TIMESTAMP` sin tz** para que la serialización JSON no cambie de forma (no aparece offset nuevo). Los valores se siguen generando en UTC desde Python.
- Los `DEFAULT SYSUTCDATETIME()` de los scripts SQL se traducen a `DEFAULT (now() AT TIME ZONE 'utc')` para que las inserciones directas por SQL (fuera de la app) también queden en UTC.

## 4. Diseño de alto nivel (High-Level Design)

### 4.1 Capas afectadas
```
┌─────────────────────────────────────────────────────────┐
│ Frontend React/Vite   (SIN CAMBIOS funcionales)          │
│   └── + frontend/.env.example                            │
├─────────────────────────────────────────────────────────┤
│ Flask API (blueprints, core scoring)                     │
│   • Lógica de negocio: SIN CAMBIOS                        │
│   • config.py: nueva conexión PostgreSQL (DATABASE_URL)  │
│   • __init__.py: marcado de sesión app (CONTEXT_INFO →   │
│     GUC de sesión PostgreSQL)                             │
│   • run.py: HOST/PORT desde entorno                       │
├─────────────────────────────────────────────────────────┤
│ SQLAlchemy (driver psycopg → PostgreSQL)                 │
├─────────────────────────────────────────────────────────┤
│ PostgreSQL                                                │
│   • DDL portado                                           │
│   • Función + 4 triggers de auditoría en PL/pgSQL         │
│   • Vistas portadas                                       │
│   • Seeds                                                 │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Estrategia de esquema: dos fuentes coherentes
1. **`db.create_all()`** (vía `seed.py`) sigue siendo la forma canónica de crear tablas desde los modelos. Genera DDL PostgreSQL correcto sin cambios en los modelos.
2. **Scripts SQL** portados a PostgreSQL, reorganizados en `backend/database/`, para instalación reproducible y para los objetos que `create_all()` NO genera: **triggers, función de auditoría, vistas, seeds**.

Orden de instalación desde cero:
```
1. crear BD + rol/usuario
2. db.create_all()  (o 01_schema.sql)     → tablas, PK, FK, UNIQUE, CHECK, índices
3. 02_functions_triggers.sql               → fn_auditoria_es_app + 4 triggers PL/pgSQL
4. 03_views.sql                            → vistas
5. seed.py                                 → admin + criterios + datos base
6. (opcional) 04_seeds.sql                 → motor de reglas de ejemplo, lista negra
```

### 4.3 Mecanismo de marcado de sesión (reemplazo de CONTEXT_INFO)
SQL Server usaba `CONTEXT_INFO` para que los triggers distinguieran operaciones de la app (ya auditadas por el servicio) de operaciones directas en BD.

PostgreSQL no tiene `CONTEXT_INFO`, pero ofrece **parámetros de sesión personalizados (GUC)** vía `SET`/`current_setting()`. Diseño:
- En `__init__.py`, el listener `checkout` ejecuta: `SET app.origen = 'APP'` (en lugar de `SET CONTEXT_INFO 0x415050`).
- La función `fn_auditoria_es_app()` en PL/pgSQL evalúa `current_setting('app.origen', true) = 'APP'`. El segundo parámetro `true` evita error si la variable no está definida (operaciones directas).

Esto preserva exactamente el comportamiento: la app marca su sesión, los triggers se saltan lo ya auditado, y las operaciones directas en BD quedan registradas con origen `BD_DIRECTO`.

## 5. Diseño de bajo nivel (Low-Level Design)

### 5.1 `backend/app/config.py`
Reemplazar el bloque de construcción de URI por:
- Prioridad 1: `DATABASE_URL` (usada por Render y desarrollo). Normalizar el prefijo `postgres://` → `postgresql+psycopg://` (Render entrega `postgres://`, SQLAlchemy 2.x + psycopg 3 requiere el dialecto explícito).
- Prioridad 2 (fallback local): construir desde `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` → `postgresql+psycopg://user:pass@host:port/db`.
- Mantener `SQLALCHEMY_ENGINE_OPTIONS` con `pool_pre_ping=True`, `pool_recycle=1800`. Añadir `sslmode=require` cuando la URL sea de Render (se puede pasar en la query string de `DATABASE_URL`; no hardcodear).
- Eliminar `DB_SERVER`, `DB_DRIVER`, `trusted_connection`.

### 5.2 `backend/app/__init__.py`
- Sustituir el cuerpo del listener `checkout`:
  - De: `cursor.execute("SET CONTEXT_INFO 0x415050")`
  - A: `cursor.execute("SET app.origen = 'APP'")`
- Mantener el `try/except` para no romper si el motor no soporta el `SET`.
- El resto (registro de blueprints, health check en `/api/health`, manejadores de error) no cambia.

### 5.3 Modelos
- Sin cambios obligatorios. Opcionalmente, eliminar `implicit_returning: False` de `User`, `Client`, `Empresa`, `ClienteEmpresa` porque en PostgreSQL `RETURNING` convive con triggers. Se conservará por seguridad salvo que se decida limpiar (decisión de bajo riesgo; documentada, no funcional).

### 5.4 Scripts SQL portados (`backend/database/`)
Nueva estructura propuesta (respeta y reemplaza `backend/migrations/`, que queda como histórico SQL Server o se archiva):

```
backend/database/
├── 01_schema.sql            # CREATE TABLE, PK, FK, UNIQUE, CHECK, DEFAULT, índices
├── 02_functions_triggers.sql# fn_auditoria_es_app() + 4 triggers PL/pgSQL
├── 03_views.sql             # vw_resumen_evaluaciones, vw_dashboard_stats, vw_evaluaciones_riesgo
├── 04_seeds.sql             # criterios, motor de reglas de ejemplo, países/ciudades
└── README.md                # procedimiento de instalación desde cero
```

Conversiones concretas de sintaxis:
- `INT IDENTITY(1,1)` → `INTEGER GENERATED BY DEFAULT AS IDENTITY`.
- `BIT ... DEFAULT 1/0` → `BOOLEAN ... DEFAULT TRUE/FALSE`.
- `DATETIME2 ... DEFAULT SYSUTCDATETIME()` → `TIMESTAMP ... DEFAULT (now() AT TIME ZONE 'utc')`.
- `NVARCHAR(MAX)` → `TEXT`; `NVARCHAR(n)` → `VARCHAR(n)`.
- `IF OBJECT_ID('x','U') IS NULL BEGIN CREATE TABLE ... END` → `CREATE TABLE IF NOT EXISTS ...`.
- `IF NOT EXISTS (SELECT 1 FROM sys.indexes ...) CREATE INDEX ...` → `CREATE INDEX IF NOT EXISTS ...`.
- `CONCAT(a,' ',ISNULL(b,''))` → `concat_ws(' ', a, coalesce(b,''))` o `a || ' ' || coalesce(b,'')`.
- `ISNULL(x, y)` → `COALESCE(x, y)`.
- `SELECT TOP 1 ...` → `SELECT ... LIMIT 1`.
- `SCOPE_IDENTITY()` → `... RETURNING id` capturado en variable PL/pgSQL, o `currval(pg_get_serial_sequence(...))`.
- `ROUND(x,1)` → `ROUND(x, 1)` (compatible).
- Eliminar `USE inmobiliaria_db; GO`, `SET NOCOUNT ON`, separadores `GO`, prefijo `dbo.`.
- `PRINT '...'` → `RAISE NOTICE '...'` dentro de bloques `DO $$ ... $$;` cuando se requiera.

### 5.5 Triggers de auditoría en PL/pgSQL
Reemplazar los 4 triggers `AFTER INSERT/UPDATE/DELETE` y la función helper. Diseño por tabla (`usuarios`, `clientes`, `empresas`, `cliente_empresa`):

- Función helper `fn_auditoria_es_app()` → `RETURNS boolean` usando `current_setting('app.origen', true) = 'APP'`.
- Una **función trigger** por tabla (PL/pgSQL) que:
  - Sale temprano si `fn_auditoria_es_app()` es verdadero (`RETURN NEW/OLD`).
  - Determina la acción según `TG_OP` (`INSERT`/`UPDATE`/`DELETE`) — reemplaza la lógica `inserted`/`deleted`.
  - Usa `NEW`/`OLD` en lugar de las tablas mágicas `inserted`/`deleted`.
  - Metadatos de sesión: `SUSER_SNAME()` → `current_user`/`session_user`; `HOST_NAME()` → `inet_client_addr()` (o `''`); `PROGRAM_NAME()` → `current_setting('application_name', true)`.
  - Escapado JSON: en lugar de `STRING_ESCAPE(...,'json')`, construir el JSON con `to_jsonb(...)` / `jsonb_build_object(...)` y castear a `text`, que garantiza escapado correcto.
  - Fecha: `SYSUTCDATETIME()` → `now() AT TIME ZONE 'utc'`.
  - `INSERT INTO auditoria (...)` idéntico en columnas y valores semánticos (`tipo_evento`, `accion`, `modulo='BD'`, `usuario_nombre='BD: '||current_user`, etc.).
- Cada trigger se crea con `CREATE TRIGGER ... AFTER INSERT OR UPDATE OR DELETE ... FOR EACH ROW EXECUTE FUNCTION ...`.

Nota sobre granularidad: los triggers T-SQL eran a nivel sentencia (procesaban conjuntos `inserted`/`deleted`). Los de PL/pgSQL serán `FOR EACH ROW`, lo que produce el **mismo registro de auditoría por fila** afectada (comportamiento equivalente, ya que el trigger original insertaba una fila de auditoría por cada fila de `inserted`/`deleted`).

### 5.6 Vistas
Portar `vw_resumen_evaluaciones`, `vw_dashboard_stats` y `vw_evaluaciones_riesgo`:
- `CONCAT` + `ISNULL` → `concat_ws`/`coalesce`.
- Subconsultas `(SELECT COUNT(*) ...)` → idénticas (portables).
- `CASE WHEN ... THEN ROUND(...) ELSE 0 END` → idéntico.
- `CREATE OR REPLACE VIEW` en lugar del patrón `IF OBJECT_ID(...) DROP VIEW ... GO CREATE VIEW`.

### 5.7 Dependencias (`requirements.txt`)
- Quitar: `pyodbc==5.1.0`.
- Agregar: `psycopg[binary]==3.2.*` (driver PostgreSQL moderno, compatible con SQLAlchemy 2.x y con Render) y `gunicorn==23.*`.
- Conservar el resto sin cambios.

### 5.8 Empaquetado Docker
- `backend/Dockerfile`:
  - Eliminar instalación de `msodbcsql17`, `unixodbc-dev`, claves de Microsoft.
  - Base `python:3.11-slim` (se mantiene). `psycopg[binary]` no requiere paquetes de sistema.
  - `CMD` → `gunicorn --bind 0.0.0.0:${PORT:-5000} "app:create_app()"`.
- `docker-compose.yml`:
  - Servicio `db` → imagen `postgres:16-alpine`, variables `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, volumen `postgres_data`, healthcheck con `pg_isready`.
  - Servicio `backend` → `DATABASE_URL=postgresql+psycopg://...@db:5432/...`, `depends_on: db (service_healthy)`.
  - Se explica el cambio; no se elimina la configuración previa en silencio.

### 5.9 `run.py`
- `port = int(os.getenv("PORT", 5000))`, `host = os.getenv("HOST", "0.0.0.0")`, `debug` según `FLASK_ENV`. Solo para desarrollo; en producción se usa Gunicorn.

### 5.10 Variables de entorno
`backend/.env.example` (nuevas):
```
FLASK_ENV=development
SECRET_KEY=
JWT_SECRET_KEY=
# PostgreSQL — desarrollo local
DATABASE_URL=postgresql+psycopg://inmobiliaria:CAMBIAR@localhost:5432/inmobiliaria_db
# Alternativa por partes (si no se usa DATABASE_URL):
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inmobiliaria_db
DB_USER=inmobiliaria
DB_PASSWORD=
# URLs de la app
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:5000
# Pagopar (opcional; vacío = modo TEST)
PAGOPAR_PUBLIC_KEY=
PAGOPAR_PRIVATE_KEY=
PAGOPAR_BASE_URL=https://api.pagopar.com/api
PAGOPAR_URL_RETORNO=http://localhost:3000/facturacion
PAGOPAR_URL_NOTIFICACION=http://localhost:5000/api/facturacion/pagopar/webhook
```
`frontend/.env.example` (nuevo): `VITE_API_URL=http://localhost:5000/api`.
`.gitignore` ya excluye `.env` y `backend/.env` (verificado); se conserva.

### 5.11 PostgreSQL local en Windows
Dos caminos documentados en `backend/database/README.md`:
- **Opción A (Docker, recomendada):** `docker compose up db` levanta PostgreSQL 16 con la BD creada por variables de entorno.
- **Opción B (instalación nativa):** instalar PostgreSQL 16 desde el instalador oficial (EDB). Luego crear rol y BD:
  ```sql
  CREATE ROLE inmobiliaria WITH LOGIN PASSWORD 'CAMBIAR';
  CREATE DATABASE inmobiliaria_db OWNER inmobiliaria;
  ```
- Encoding UTF-8 (por defecto en PostgreSQL) cubre el dominio en español; el collation `Modern_Spanish_CI_AI` de SQL Server no es necesario porque las búsquedas usan `ILIKE` (case-insensitive explícito).

### 5.12 Preparación para Render
- **Web Service (backend):**
  - Build: `pip install -r requirements.txt`.
  - Start: `gunicorn --bind 0.0.0.0:$PORT "app:create_app()"` (Render inyecta `$PORT`).
  - Env: `FLASK_ENV=production`, `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL` (enlazada desde la BD de Render), `FRONTEND_URL`.
  - Health check path: `/api/health`.
  - CORS: hoy es `origins: "*"`. Para producción, restringir a `FRONTEND_URL` (mejora de seguridad, no rompe funcionalidad).
- **PostgreSQL administrado (Render):** la app toma `DATABASE_URL` del entorno; normalización `postgres://` → `postgresql+psycopg://` en `config.py`. `sslmode=require` vía query string de la URL. Sin dependencia de `localhost`, IP local, SQL Server ni rutas de Windows.
- **Frontend (Static Site):** build `npm run build`, publish `dist/`, variable `VITE_API_URL` apuntando al backend de Render.
- Documento `RENDER.md` con los pasos (opcional `render.yaml` como blueprint).

### 5.13 Scripts operativos PostgreSQL
- Sustituir `backup_db.ps1`/`restore_db.ps1` (basados en `sqlcmd`/`.bak`) por equivalentes con `pg_dump`/`pg_restore`, o marcarlos como obsoletos con nota. Decisión: crear `backend/scripts/pg_backup.ps1` y `pg_restore.ps1` mínimos, y dejar los `.bak` antiguos documentados como legado.
- `backend/_gen_docx.py` (introspección con `sys.*`): reescribir consultas a catálogos de PostgreSQL (`information_schema` / `pg_catalog`) o marcar como utilidad legado. No es runtime; prioridad baja.

## 6. Sistema de scoring (preservación exacta)

El motor vive en `backend/app/blueprints/scoring/engine.py` y `backend/app/core/` (engine, evaluator, validator, classifier, explainer). Es **lógica Python pura** que opera sobre objetos ya cargados por SQLAlchemy:
- Reglas IF-THEN con operadores `>=, <=, ==, >, <, !=` (módulo `operator`).
- Pesos (`Numeric`), umbrales (75% bajo / 50% medio / <50% alto), reglas determinantes → `rechazado`, factor lista negra → `alto`.

Ninguna de estas piezas consulta al motor de BD directamente ni usa SQL de dialecto. La migración **no toca este código**. Los tipos `Numeric` mantienen precisión idéntica en PostgreSQL, por lo que los cálculos de score no cambian.

**Verificación de equivalencia (antes/después):** ejecutar un conjunto fijo de casos de entrada contra el motor y comparar `score_final`, `porcentaje`, `categoria_riesgo`, `rechazado_por_regla`, clasificación Alto/Medio/Bajo y Apto/No apto. Como el motor es determinístico y desacoplado de la BD, la comparación se hace a nivel de función (`ejecutar_motor`, `ejecutar_evaluacion`) con datos idénticos.

## 7. APIs y seguridad (sin regresiones)

- Blueprints: `auth`, `users`, `clients`, `empresas`, `evaluation`, `reports`, `scoring`, `facturacion`, `auditoria`, `core`. Ninguno depende de sintaxis SQL Server; todos usan el ORM y helpers `success()/error()`. Se preservan endpoints, códigos HTTP y forma del JSON.
- Auth: JWT (access 8h, refresh 30d), roles (`propietario`, `administrador`, `comercial`), 2FA TOTP (`pyotp`), hash de contraseñas con `werkzeug.security` (scrypt). **Independiente del motor de BD.** Sin cambios.
- Auditoría a nivel servicio (`auditoria_service.registrar`) no cambia; la auditoría a nivel BD se preserva vía triggers PL/pgSQL.
- Secretos: siguen en variables de entorno; `config.py` mantiene la validación estricta en producción. No se introducen credenciales en código.

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| `DATABASE_URL` de Render llega como `postgres://` | Normalización a `postgresql+psycopg://` en `config.py`. |
| Triggers `FOR EACH ROW` vs sentencia | Comportamiento equivalente (una fila de auditoría por fila afectada), verificado con pruebas de INSERT/UPDATE/DELETE. |
| Booleanos `1/0` heredados en seeds/datos | DDL usa `BOOLEAN`; seeds portados usan `TRUE/FALSE`. |
| Case-insensitive perdido al dejar collation | Búsquedas ya usan `ILIKE` (case-insensitive real en PostgreSQL). |
| `implicit_returning=False` innecesario | Se conserva (no daña) o se limpia; sin impacto funcional. |
| Datos existentes en SQL Server | Migración de datos (si se requiere) vía export CSV/`INSERT`; el diseño prioriza esquema reproducible. No se ejecutan operaciones destructivas sin aviso. |

## 9. Entregables de la implementación

1. `backend/app/config.py` — conexión PostgreSQL basada en `DATABASE_URL` + fallback por partes.
2. `backend/app/__init__.py` — marcado de sesión `SET app.origen`.
3. `backend/run.py` — `HOST`/`PORT`/`debug` desde entorno.
4. `backend/database/01_schema.sql`, `02_functions_triggers.sql`, `03_views.sql`, `04_seeds.sql`, `README.md`.
5. `backend/requirements.txt` — `psycopg[binary]`, `gunicorn`; sin `pyodbc`.
6. `backend/Dockerfile` — sin ODBC, arranque con Gunicorn.
7. `docker-compose.yml` — servicio `postgres:16`.
8. `backend/.env.example`, `frontend/.env.example` — variables PostgreSQL/URLs.
9. `RENDER.md` (+ opcional `render.yaml`) — despliegue backend + BD + frontend.
10. Scripts operativos PostgreSQL (`pg_backup.ps1`, `pg_restore.ps1`) o nota de legado.
11. Prueba de equivalencia del motor de scoring (antes/después).
