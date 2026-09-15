import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Entorno actual (development / production)
_ENV = os.getenv("FLASK_ENV", "development").lower()
_IS_PROD = _ENV == "production"

# Longitud mínima aceptable para las claves secretas
_MIN_KEY_LEN = 32


def _resolver_clave(nombre: str) -> str:
    """
    Obtiene una clave secreta desde el entorno aplicando políticas de seguridad:
      - En producción es obligatoria y debe tener longitud suficiente;
        si falta o es débil, se detiene el arranque.
      - En desarrollo, si falta, se genera una temporal (válida solo mientras
        dure el proceso) para no bloquear el trabajo local.
    """
    valor = os.getenv(nombre)

    if _IS_PROD:
        if not valor:
            raise RuntimeError(
                f"La variable de entorno {nombre} es obligatoria en producción. "
                "Defínala en el archivo .env con un valor aleatorio seguro."
            )
        if len(valor) < _MIN_KEY_LEN:
            raise RuntimeError(
                f"{nombre} es demasiado corta ({len(valor)} caracteres). "
                f"Use al menos {_MIN_KEY_LEN} caracteres aleatorios."
            )
        return valor

    # Desarrollo: usa el valor del .env o genera uno temporal
    return valor or secrets.token_urlsafe(48)


class Config:
    SECRET_KEY = _resolver_clave("SECRET_KEY")
    JWT_SECRET_KEY = _resolver_clave("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Cookies/tokens: endurecimiento básico de sesión
    JWT_COOKIE_SECURE = _IS_PROD          # solo enviar por HTTPS en producción
    JWT_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _IS_PROD

    # ── Conexión PostgreSQL ──────────────────────────────────────────────
    # Prioridad 1: DATABASE_URL (usada en Render y, opcionalmente, en local).
    #   Render entrega la URL con el prefijo "postgres://", pero SQLAlchemy 2.x
    #   con el driver psycopg (v3) requiere "postgresql+psycopg://".
    # Prioridad 2 (fallback): construir la URL a partir de variables sueltas
    #   (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD) para desarrollo local.
    _database_url = os.getenv("DATABASE_URL", "").strip()

    if _database_url:
        # Normalizar el esquema al dialecto psycopg 3
        if _database_url.startswith("postgres://"):
            _database_url = _database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif _database_url.startswith("postgresql://"):
            _database_url = _database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        _conn = _database_url
    else:
        _host = os.getenv("DB_HOST", "localhost")
        _port = os.getenv("DB_PORT", "5432")
        _db   = os.getenv("DB_NAME", "inmobiliaria_db")
        _user = os.getenv("DB_USER", "inmobiliaria")
        _password = os.getenv("DB_PASSWORD", "")
        _conn = (
            f"postgresql+psycopg://{_user}:{_password}@{_host}:{_port}/{_db}"
        )

    SQLALCHEMY_DATABASE_URI = _conn
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }

    # ── Pasarela de pagos Pagopar (Paraguay) ──
    # Las claves se obtienen en el panel de Pagopar: "Integrar con mi sitio web".
    # Mientras no estén definidas, la integración queda deshabilitada y el
    # sistema sigue usando el flujo de pago TEST.
    PAGOPAR_PUBLIC_KEY  = os.getenv("PAGOPAR_PUBLIC_KEY", "")
    PAGOPAR_PRIVATE_KEY = os.getenv("PAGOPAR_PRIVATE_KEY", "")
    PAGOPAR_BASE_URL    = os.getenv("PAGOPAR_BASE_URL", "https://api.pagopar.com/api")
    # URL del frontend a la que Pagopar redirige tras el pago (página de resultado)
    PAGOPAR_URL_RETORNO = os.getenv("PAGOPAR_URL_RETORNO", "http://localhost:3000/facturacion")
    # URL pública de tu backend que Pagopar invoca para notificar el pago (webhook)
    PAGOPAR_URL_NOTIFICACION = os.getenv(
        "PAGOPAR_URL_NOTIFICACION",
        "http://localhost:5000/api/facturacion/pagopar/webhook",
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
