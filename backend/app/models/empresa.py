from datetime import datetime, timezone
from app.extensions import db


class Empresa(db.Model):
    """Empresas clientes que contratan el uso del sistema."""
    __tablename__ = "empresas"
    # La tabla tiene triggers de auditoría: desactivar OUTPUT implícito.
    __table_args__ = {"implicit_returning": False}

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(150), nullable=False)
    ruc         = db.Column(db.String(30), unique=True)
    direccion   = db.Column(db.String(255))
    telefono    = db.Column(db.String(30))
    email       = db.Column(db.String(150))
    activo      = db.Column(db.Boolean, default=True)
    # Control de bloqueo de consultas
    consultas_habilitadas = db.Column(db.Boolean, default=True)
    motivo_bloqueo        = db.Column(db.String(50))   # BLOQUEADO_DEUDA, BLOQUEADO_MANUAL
    fecha_bloqueo         = db.Column(db.DateTime, nullable=True)
    fecha_desbloqueo      = db.Column(db.DateTime, nullable=True)

    creado_en   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    usuarios = db.relationship("User", back_populates="empresa",
                               primaryjoin="Empresa.id == foreign(User.id_empresa)",
                               lazy="dynamic", viewonly=True)

    def to_dict(self):
        return {
            "id":        self.id,
            "nombre":    self.nombre,
            "ruc":       self.ruc,
            "direccion": self.direccion,
            "telefono":  self.telefono,
            "email":     self.email,
            "activo":    self.activo,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "total_usuarios": self.usuarios.count(),
        }
