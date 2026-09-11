import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    _server = os.getenv("DB_SERVER", "DESKTOP-8242966\SQLEXPRESS")
    _db     = os.getenv("DB_NAME",   "inmobiliaria_db")
    _driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    _user   = os.getenv("DB_USER",   "")
    _password = os.getenv("DB_PASSWORD", "")

    # Autenticación de Windows si no hay usuario definido
    if _user:
        _conn = (
            f"mssql+pyodbc://{_user}:{_password}@{_server}/{_db}"
            f"?driver={_driver.replace(' ', '+')}"
        )
    else:
        _conn = (
            f"mssql+pyodbc://@{_server}/{_db}"
            f"?driver={_driver.replace(' ', '+')}"
            f"&trusted_connection=yes"
        )

    SQLALCHEMY_DATABASE_URI = _conn
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
