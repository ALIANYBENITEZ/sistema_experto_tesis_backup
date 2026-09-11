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

## Estructura del proyecto

```
V.0.1/
├── backend/
│   ├── app/               ← Código Flask
│   ├── migrations/        ← Scripts SQL
│   ├── venv/              ← Entorno virtual Python (NO subir a Git)
│   ├── .env               ← Configuración BD y JWT
│   ├── run.py             ← Punto de entrada
│   └── seed.py            ← Datos iniciales (ejecutar solo una vez)
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
