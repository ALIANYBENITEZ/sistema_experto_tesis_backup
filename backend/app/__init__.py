import os
from flask import Flask
from app.config import config
from app.extensions import db, jwt, cors


def create_app(env: str | None = None) -> Flask:
    env = env or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config.get(env, config["default"]))

    # ── Inicializar extensiones ───────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # ── Marcar las conexiones de la app con CONTEXT_INFO = 'APP' ──────────────
    # Permite que los triggers de auditoría a nivel BD distingan operaciones
    # hechas por la aplicación (ya auditadas por el servicio) de las hechas
    # directamente sobre la base de datos (SSMS, scripts, etc.).
    from sqlalchemy import event

    with app.app_context():
        engine = db.engine

        @event.listens_for(engine, "checkout")
        def _marcar_conexion_app(dbapi_conn, connection_record, connection_proxy):
            try:
                cursor = dbapi_conn.cursor()
                # 0x415050... => 'APP' en los primeros bytes de CONTEXT_INFO
                cursor.execute("SET CONTEXT_INFO 0x415050")
                cursor.close()
            except Exception:
                # No romper la conexión si el motor no soporta CONTEXT_INFO
                pass

    # ── Registrar blueprints ──────────────────────────────────────────────────
    from app.blueprints.auth       import auth_bp
    from app.blueprints.users      import users_bp
    from app.blueprints.clients    import clients_bp
    from app.blueprints.evaluation import evaluation_bp
    from app.blueprints.reports    import reports_bp
    from app.blueprints.scoring    import scoring_bp
    from app.blueprints.empresas   import empresas_bp
    from app.blueprints.facturacion import facturacion_bp
    from app.blueprints.auditoria  import auditoria_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(evaluation_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(scoring_bp)
    app.register_blueprint(empresas_bp)
    app.register_blueprint(facturacion_bp)
    app.register_blueprint(auditoria_bp)

    # Core de Scoring
    from app.core.routes import core_bp
    app.register_blueprint(core_bp)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return {"status": "ok", "env": env}

    # ── Manejo de errores globales ────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return {"success": False, "message": "Recurso no encontrado"}, 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return {"success": False, "message": "Método no permitido"}, 405

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return {"success": False, "message": "Error interno del servidor"}, 500

    return app
