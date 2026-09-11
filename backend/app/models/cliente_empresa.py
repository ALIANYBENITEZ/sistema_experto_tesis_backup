from datetime import datetime, timezone
from app.extensions import db


class ClienteEmpresa(db.Model):
    """Relación muchos-a-muchos entre clientes y empresas."""
    __tablename__ = "cliente_empresa"

    id          = db.Column(db.Integer, primary_key=True)
    id_cliente  = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    id_empresa  = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    estado      = db.Column(db.String(20), default="activo")  # activo / inactivo
    creado_en   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    cliente = db.relationship("Client", back_populates="empresas_rel")
    empresa = db.relationship("Empresa")

    __table_args__ = (
        db.UniqueConstraint('id_cliente', 'id_empresa', name='uq_cliente_empresa'),
        # La tabla tiene triggers de auditoría: desactivar OUTPUT implícito.
        {"implicit_returning": False},
    )

    def to_dict(self):
        return {
            "id":          self.id,
            "id_cliente":  self.id_cliente,
            "id_empresa":  self.id_empresa,
            "estado":      self.estado,
            "empresa_nombre": self.empresa.nombre if self.empresa else None,
            "creado_en":   self.creado_en.isoformat() if self.creado_en else None,
        }
