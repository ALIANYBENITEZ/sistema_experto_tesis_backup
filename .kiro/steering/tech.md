# Stack Tecnológico

## Backend (Flask REST API)

- **Runtime**: Python 3.x
- **Framework**: Flask 3.1.0 con Application Factory pattern
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Base de datos**: SQL Server 2022 vía pyodbc (ODBC Driver 17)
- **Autenticación**: Flask-JWT-Extended 4.6.0 (access token 8h, refresh token 30d)
- **CORS**: Flask-CORS 4.0.0
- **Validación**: marshmallow 3.21.3
- **PDF**: reportlab 4.2.2
- **Variables de entorno**: python-dotenv
- **Hashing**: werkzeug.security (scrypt)

## Frontend (React SPA)

- **Framework**: React 18.3 (JSX, sin TypeScript)
- **Build tool**: Vite 5.4
- **Routing**: react-router-dom 6
- **HTTP client**: Axios con interceptors (auto-refresh de tokens)
- **Formularios**: react-hook-form
- **Estilos**: TailwindCSS 3.4 + PostCSS + Autoprefixer
- **Iconos**: lucide-react
- **Gráficos**: Recharts
- **Notificaciones**: react-hot-toast
- **Estado global**: React Context (AuthContext)

## Credit-Scoring (Prototipo standalone)

- Flask 3.0.3 con Jinja2 templates
- Aplicación monolítica de demostración con datos mock

## Base de Datos

- Motor: SQL Server 2022 (collation: Modern_Spanish_CI_AI)
- Conexión: pyodbc con soporte Windows Auth y SQL Auth
- Migraciones: Scripts SQL manuales en `backend/migrations/`
- No se usa Alembic

## Comandos comunes

```bash
# Backend - instalar dependencias
cd backend
pip install -r requirements.txt

# Backend - ejecutar servidor de desarrollo (puerto 5000)
python run.py

# Backend - ejecutar seed inicial (crear admin y criterios)
python seed.py

# Frontend - instalar dependencias
cd frontend
npm install

# Frontend - servidor de desarrollo (puerto 3000, proxy a :5000)
npm run dev

# Frontend - build de producción
npm run build

# Credit-scoring prototype
cd credit-scoring
pip install -r requirements.txt
python app.py
```

## Variables de entorno (backend/.env)

```
FLASK_ENV=development
SECRET_KEY=...
JWT_SECRET_KEY=...
DB_SERVER=localhost
DB_NAME=inmobiliaria_db
DB_USER=sa
DB_PASSWORD=...
DB_DRIVER=ODBC Driver 17 for SQL Server
```

## Variables de entorno (frontend/.env)

```
VITE_API_URL=http://localhost:5000/api
```
