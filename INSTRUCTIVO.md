# Instructivo de Ejecución del Sistema
## Sistema de Evaluación de Clientes — Inmobiliaria

---

## Requisitos previos (ya instalados)

| Herramienta | Versión | Verificar con |
|---|---|---|
| Python | 3.12.x | `python3.12 --version` |
| Node.js | 24.x | `node --version` |
| npm | 11.x | `npm --version` |
| SQL Server | 2022 Express | SSMS conectado |
| ODBC Driver | 17 for SQL Server | Ya instalado |

---

## PASO 1 — Levantar el Backend (Flask)

Abre una ventana de **PowerShell** y ejecuta:

```powershell
# 1. Ir a la carpeta del backend
cd "C:\Users\RYZEN\Documents\TESIS 2026\SISTEMA\V.0.1\backend"

# 2. Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# 3. Verificar que el venv está activo
# Deberías ver (venv) al inicio del prompt

# 4. Levantar el servidor Flask
python run.py
```

Deberías ver:
```
* Running on http://127.0.0.1:5000
* Debugger is active!
```

> **El backend queda corriendo en esta ventana. NO la cierres.**

---

## PASO 2 — Levantar el Frontend (React)

Abre una **segunda ventana de PowerShell** y ejecuta:

```powershell
# 1. Ir a la carpeta del frontend
cd "C:\Users\RYZEN\Documents\TESIS 2026\SISTEMA\V.0.1\frontend"

# 2. Levantar el servidor de desarrollo
npm run dev
```

Deberías ver:
```
VITE v5.x  ready in 630 ms
➜  Local:   http://localhost:3000/
```

> **El frontend queda corriendo en esta ventana. NO la cierres.**

---

## PASO 3 — Abrir el sistema

Abre tu navegador y ve a:

```
http://localhost:3000
```

### Credenciales de acceso

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | `admin@inmobiliaria.com` | `Admin@2026` |
| Operador | `operador@inmobiliaria.com` | `Operador@2026` |

---

## Resumen: 2 ventanas siempre abiertas

```
Ventana 1 — Backend          Ventana 2 — Frontend
─────────────────────        ─────────────────────
cd backend                   cd frontend
.\venv\Scripts\Activate.ps1  npm run dev
python run.py
```

---

## Detener el sistema

En cada ventana presiona `Ctrl + C` para detener el servidor.

---

## Solución de problemas frecuentes

### "npm no se reconoce"
```powershell
# Verificar que el PATH tiene Node
$env:PATH -split ";" | Where-Object { $_ -like "*nodejs*" }
# Si no aparece, agregar C:\Program Files\nodejs\ a Variables de entorno
```

### "python3.12 no se reconoce"
```powershell
# Usar la ruta completa si falla
C:\Users\RYZEN\AppData\Local\Microsoft\WindowsApps\python3.12.exe run.py
```

### "No se puede cargar el script Activate.ps1"
```powershell
# Habilitar ejecución de scripts (solo una vez)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### El frontend muestra errores 422
- El backend no está corriendo o el venv no está activado
- Verifica que `http://localhost:5000/api/health` responde en el navegador

### No conecta a SQL Server
- Verificar que el servicio SQL Server Express está iniciado:
  `Win + R` → `services.msc` → buscar `SQL Server (SQLEXPRESS)` → Iniciar

---

## Respaldo y restauración de la base de datos

Los datos reales (clientes, evaluaciones, usuarios) viven en SQL Server, **no** en el
repositorio. Para respaldarlos se usan dos scripts en `backend/scripts/`.

> Los respaldos (`.bak`) contienen datos personales, por eso la carpeta `backups/`
> está en `.gitignore` y **nunca se sube a GitHub**.

### Crear un respaldo

```powershell
cd "C:\Users\RYZEN\Documents\TESIS 2026\SISTEMA\V.0.1"
powershell -ExecutionPolicy Bypass -File ".\backend\scripts\backup_db.ps1"
```

- Genera un archivo `inmobiliaria_db_AAAAMMDD_HHMMSS.bak` dentro de `backups/`.
- Puede aparecer un aviso de Windows (UAC): acéptalo (la copia necesita permisos).
- En otra PC/instancia:
  `... backup_db.ps1 -Server "MI-PC\SQLEXPRESS" -Database "inmobiliaria_db"`

> **Importante:** copia el `.bak` a un disco externo o nube privada. Un respaldo
> en el mismo disco no protege ante una falla del disco.

### Restaurar un respaldo

```powershell
# Restaura el .bak más reciente de la carpeta backups/
powershell -ExecutionPolicy Bypass -File ".\backend\scripts\restore_db.ps1"

# O un archivo específico
powershell -ExecutionPolicy Bypass -File ".\backend\scripts\restore_db.ps1" -BakFile "C:\ruta\al\archivo.bak"
```

- Pide confirmación escribiendo `SI` porque **reemplaza** la base existente.
- Reubica automáticamente los archivos de datos/log según la instancia destino,
  por lo que sirve también para restaurar en otra PC.

### Recrear la base desde cero (sin respaldo, solo estructura + datos iniciales)

Si no tienes un `.bak` (por ejemplo en una PC nueva tras clonar el repo):

```powershell
# 1) Ejecutar los scripts SQL de estructura en orden (con SSMS o sqlcmd)
#    backend/migrations/01_create_tables.sql ... 07_fk_faltantes.sql
# 2) Cargar los datos iniciales
cd backend
.\venv\Scripts\python.exe seed.py
```

---

## Estructura del proyecto

```
V.0.1/
├── backend/
│   ├── app/               ← Código Flask
│   ├── migrations/        ← Scripts SQL (estructura de la BD)
│   ├── scripts/           ← backup_db.ps1 / restore_db.ps1
│   ├── venv/              ← Entorno virtual Python (NO subir a Git)
│   ├── .env               ← Configuración BD y JWT (NO subir a Git)
│   ├── run.py             ← Punto de entrada
│   └── seed.py            ← Datos iniciales (ejecutar solo una vez)
│
├── backups/               ← Respaldos .bak (NO subir a Git)
│
└── frontend/
    ├── src/               ← Código React
    ├── node_modules/      ← Dependencias npm (NO subir a Git)
    ├── .env               ← URL del backend
    └── package.json       ← Dependencias
```

---

## Primer uso (solo una vez, ya ejecutado)

Estos pasos ya están hechos. Solo como referencia:

```powershell
# Backend — crear venv e instalar dependencias
cd backend
python3.12 -m venv venv
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\python.exe seed.py   # crea admin y criterios

# Frontend — instalar dependencias
cd frontend
npm install
```

---

*Sistema de Evaluación de Clientes — Inmobiliaria v0.1*
