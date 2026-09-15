# Despliegue en Render

Arquitectura: **React/Vite (Static Site) → Flask/Gunicorn (Web Service) → PostgreSQL (Managed)**.

Hay dos formas: con el Blueprint `render.yaml` (recomendada) o creando cada servicio a mano.

---

## Requisito previo

Subir el proyecto a un repositorio en GitHub o GitLab. Render despliega desde ahí.

Verificar antes de subir que **no se sube ningún `.env`** (ya están en `.gitignore`).

---

## Opción A — Blueprint (recomendada)

1. En Render: **New +** → **Blueprint** → conecta el repositorio.
2. Render detecta `render.yaml` y propone crear 3 recursos:
   - `inmobiliaria-db` (PostgreSQL)
   - `inmobiliaria-backend` (Flask/Gunicorn)
   - `inmobiliaria-frontend` (Static Site)
3. Render pedirá completar las variables marcadas como `sync: false`. Ver la
   sección **Variables** más abajo. Como aún no conoces las URLs finales, puedes
   poner un valor temporal y ajustarlo tras el primer deploy (paso 5).
4. Deploy. Render crea la BD, corre las migraciones (ver **Esquema de BD**) y publica.
5. Cuando termine, copia las URLs públicas que asignó Render y actualiza:
   - En el **backend**: `FRONTEND_URL` y `CORS_ORIGINS` = URL del frontend
     (ej. `https://inmobiliaria-frontend.onrender.com`).
   - En el **frontend**: `VITE_API_URL` = URL del backend + `/api`
     (ej. `https://inmobiliaria-backend.onrender.com/api`).
   Vuelve a desplegar el servicio que hayas cambiado (el frontend requiere
   rebuild porque `VITE_API_URL` se hornea en tiempo de build).

---

## Opción B — Manual

### 1. Base de datos
New + → **PostgreSQL**. Nombre `inmobiliaria-db`, database `inmobiliaria_db`,
user `inmobiliaria`. Al crearse, copia la **Internal Database URL**.

### 2. Backend (Web Service)
New + → **Web Service** → repo. Configuración:
- Root Directory: `backend`
- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 "app:create_app()"`
- Health Check Path: `/api/health`
- Variables de entorno: ver **Variables**.

### 3. Frontend (Static Site)
New + → **Static Site** → repo. Configuración:
- Root Directory: `frontend`
- Build Command: `npm ci && npm run build`
- Publish Directory: `dist`
- Variable: `VITE_API_URL = https://<tu-backend>.onrender.com/api`
- Redirect/Rewrite Rule: `/*` → `/index.html` (Rewrite) para que funcione React Router.

---

## Variables de entorno

### Backend
| Variable | Valor | Notas |
|---|---|---|
| `FLASK_ENV` | `production` | Activa validación de claves y CORS restringido. |
| `DATABASE_URL` | (de la BD de Render) | Con Blueprint se enlaza sola. Manual: pegar la Internal URL. |
| `SECRET_KEY` | aleatorio ≥32 chars | Con Blueprint se genera solo. |
| `JWT_SECRET_KEY` | aleatorio ≥32 chars | Con Blueprint se genera solo. |
| `FRONTEND_URL` | URL del frontend | Para CORS. |
| `CORS_ORIGINS` | igual a `FRONTEND_URL` | Orígenes permitidos (coma-separados). |
| `PAGOPAR_*` | opcional | Si se dejan vacías, el pago va en modo TEST. |

> El código normaliza automáticamente el `DATABASE_URL` que entrega Render
> (`postgres://...`) al formato que usa el driver (`postgresql+psycopg://...`).

### Frontend
| Variable | Valor |
|---|---|
| `VITE_API_URL` | `https://<backend>.onrender.com/api` |

---

## Esquema de base de datos (primer despliegue)

La BD de Render arranca vacía. Para crear las tablas y datos, desde tu equipo
apuntando a la BD de Render (usa la **External Database URL** de Render):

```powershell
# 1) Crear tablas + admin + criterios
cd backend
$env:DATABASE_URL = "postgresql+psycopg://<external-url-de-render>"
.\venv\Scripts\python.exe seed.py

# 2) Aplicar funciones/triggers, vistas y seed del motor de reglas
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
& $psql "<external-url-de-render>" -f database\02_functions_triggers.sql
& $psql "<external-url-de-render>" -f database\03_views.sql
& $psql "<external-url-de-render>" -f database\04_seeds.sql
```

### Migrar tus datos actuales a Render (opcional)
Si quieres subir a Render los datos que ya migraste localmente:

```powershell
$psql    = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$pgdump  = "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

# Volcado de la base local (solo datos)
$env:PGPASSWORD = "tesisAliany2026@"
& $pgdump -U inmobiliaria -h localhost -d inmobiliaria_db --data-only --disable-triggers -f datos_local.sql

# Cargar en Render (external URL). Ejecutar seed.py + scripts de esquema ANTES.
& $psql "<external-url-de-render>" -f datos_local.sql
```

---

## Planes (configuración actual del `render.yaml`)
- **Backend**: plan `starter` (**$7/mes**). No se duerme por inactividad, arranque inmediato.
- **PostgreSQL**: plan `free`. **AVISO: la BD free de Render expira a los 30 días y
  se elimina** (se pierden los datos). Estrategias para no perder información:
  - Hacer respaldos periódicos con `pg_dump` (ver más abajo) y guardarlos aparte.
  - Antes de que expire, crear una BD nueva y restaurar el respaldo, o pasar a un
    plan de pago (`plan: basic-256mb`) cambiando esa línea en `render.yaml`.
  - Tu base local (SQL Server → PostgreSQL) sigue siendo tu copia maestra; puedes
    volver a cargar en Render cuando haga falta.
- **Frontend**: Static Site, **gratis** en Render.

Costo actual: **$7/mes** (solo el backend).

## Respaldo de la BD free (recomendado antes de los 30 días)

```powershell
$pgdump = "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
# External Database URL de Render (la de la BD en el dashboard)
& $pgdump "<external-url-de-render>" -Fc -f backup_render.dump
```
Para restaurar en una BD nueva:
```powershell
$pgrestore = "C:\Program Files\PostgreSQL\18\bin\pg_restore.exe"
& $pgrestore -d "<nueva-external-url>" --no-owner backup_render.dump
```

## Notas
- Con el plan `starter` el backend queda siempre activo (sin cold starts).
- El backend usa Gunicorn (no el servidor de desarrollo de Flask).
- El `frontend/Dockerfile` y `frontend/nginx.conf` son para Docker Compose local;
  en Render el frontend se sirve como Static Site y esos archivos se ignoran.
