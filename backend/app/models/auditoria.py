"""
Modelo de Auditoría — Bitácora centralizada de eventos del sistema.
"""
from datetime import datetime, timezone
from app.extensions import db


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id                = db.Column(db.Integer, primary_key=True)
    usuario_id        = db.Column(db.Integer, nullable=True)
    usuario_nombre    = db.Column(db.String(150), nullable=True)  # snapshot del nombre
    id_empresa        = db.Column(db.Integer, nullable=True)
    tipo_evento       = db.Column(db.String(30), nullable=False)   # AUTENTICACION, SEGURIDAD, USUARIOS, CLIENTES, EVALUACIONES, REPORTES, FACTURACION
    accion            = db.Column(db.String(50), nullable=False)   # LOGIN_EXITOSO, REGISTRO_CLIENTE, etc.
    modulo            = db.Column(db.String(50))
    entidad           = db.Column(db.String(50))
    registro_id       = db.Column(db.String(50), nullable=True)    # ID del registro afectado
    resultado         = db.Column(db.String(20), default="EXITO")  # EXITO, FALLO
    ip                = db.Column(db.String(50), nullable=True)
    info_adicional    = db.Column(db.Text, nullable=True)          # JSON string
    valores_anteriores = db.Column(db.Text, nullable=True)         # JSON string
    valores_nuevos    = db.Column(db.Text, nullable=True)          # JSON string
    fecha             = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario_nombre,
            "id_empresa": self.id_empresa,
            "tipo_evento": self.tipo_evento,
            "accion": self.accion,
            "modulo": self.modulo,
            "entidad": self.entidad,
            "registro_id": self.registro_id,
            "resultado": self.resultado,
            "ip": self.ip,
            "info_adicional": self.info_adicional,
            "valores_anteriores": self.valores_anteriores,
            "valores_nuevos": self.valores_nuevos,
            "fecha": self.fecha.isoformat() if self.fecha else None,
        }
