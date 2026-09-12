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

## Pasarela de pagos Pagopar

El módulo de Facturación puede cobrar los períodos pendientes mediante **Pagopar**
(Paraguay, guaraníes). Mientras no se carguen las credenciales, el sistema sigue
usando el **pago de prueba (TEST)** y no cobra dinero real.

### Cómo funciona (flujo)

1. El admin de la empresa entra a **Facturación** y pulsa **Pagar con Pagopar**.
2. El backend crea el pedido en Pagopar y redirige al **checkout** de Pagopar.
3. El usuario paga (tarjeta, transferencia, billetera, boca de cobro).
4. Pagopar **notifica** al backend por un webhook; el pago se marca como
   `APROBADO`, se actualiza el período y se **desbloquea** la empresa si estaba
   bloqueada por deuda.
5. Pagopar redirige de vuelta a la página de Facturación.

### Paso 1 — Cargar credenciales

Obtené `public key` y `private key` en el panel de Pagopar
(**Integrar con mi sitio web**) y completá en `backend/.env`:

```
PAGOPAR_PUBLIC_KEY=tu_public_key
PAGOPAR_PRIVATE_KEY=tu_private_key
PAGOPAR_BASE_URL=https://api.pagopar.com/api
PAGOPAR_URL_RETORNO=http://localhost:3000/facturacion
PAGOPAR_URL_NOTIFICACION=http://localhost:5000/api/facturacion/pagopar/webhook
```

Reiniciá el backend. El botón **Pagar con Pagopar** aparecerá automáticamente
(el frontend consulta `GET /api/facturacion/pagopar/estado`).

> Las claves viven solo en `backend/.env`, que está en `.gitignore` y **no** se
> sube a GitHub.

### Paso 2 — Probar el webhook en local con ngrok

Pagopar necesita una **URL pública** para notificar el pago. `localhost` no le
sirve. En desarrollo se usa **ngrok** para exponer el backend temporalmente.

1. Instalá ngrok desde https://ngrok.com/download (o `choco install ngrok`).
2. Con el backend corriendo en el puerto 5000, abrí otra terminal y ejecutá:

   ```powershell
   ngrok http 5000
   ```

3. ngrok te dará una URL pública, por ejemplo `https://abcd-1234.ngrok-free.app`.
4. Poné esa URL en `backend/.env` (y reiniciá el backend):

   ```
   PAGOPAR_URL_NOTIFICACION=https://abcd-1234.ngrok-free.app/api/facturacion/pagopar/webhook
   ```

5. Si tu panel de Pagopar pide registrar la URL de notificación, usá esa misma.

> La URL de ngrok cambia cada vez que lo reinicias (en el plan gratuito). Hay que
> actualizar `PAGOPAR_URL_NOTIFICACION` cada vez.

### Paso 3 — Realizar una transacción de prueba

1. Iniciá sesión como **admin de una empresa** que tenga un período con saldo.
2. Andá a **Facturación** → **Pagar con Pagopar**.
3. Completá el pago en el checkout de Pagopar (usá los datos de prueba que
   Pagopar habilite para tu comercio).
4. Verificá que:
   - El pago pasa a `APROBADO` en el historial.
   - El saldo del período baja y, si queda en 0, el estado es `PAGADO`.
   - Si la empresa estaba bloqueada por deuda, vuelve a quedar habilitada.
5. Revisá el módulo **Auditoría**: deben aparecer los eventos
   `PAGO_PAGOPAR_INICIADO` y `WEBHOOK_PAGOPAR_PAGADO`.

### Notas y solución de problemas

- **El botón "Pagar con Pagopar" no aparece:** faltan las credenciales en `.env`
  o no reiniciaste el backend.
- **"La pasarela Pagopar no está configurada":** `PAGOPAR_PUBLIC_KEY` o
  `PAGOPAR_PRIVATE_KEY` están vacías.
- **El pago no se marca como aprobado:** el webhook no llegó. Revisá que
  `PAGOPAR_URL_NOTIFICACION` sea la URL pública (ngrok/producción) y que ngrok
  siga activo. Podés ver las llamadas entrantes en el panel de ngrok
  (`http://localhost:4040`).
- **Los nombres de algunos campos pueden variar** según la versión de tu cuenta
  Pagopar. Si tras una prueba real el parseo falla, ajustá
  `backend/app/services/pagopar_service.py` (funciones `iniciar_transaccion`,
  `consultar_pedido`, `procesar_webhook`).
- **Endpoints usados:** `POST /api/facturacion/pagos/pagopar/iniciar` (inicia el
  pago) y `POST /api/facturacion/pagopar/webhook` (recibe la notificación, es
  público y valida el token SHA1 de Pagopar).

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
│   │   └── services/      ← pagopar_service.py, totp_service.py, etc.
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
