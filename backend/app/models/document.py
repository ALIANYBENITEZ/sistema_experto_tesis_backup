from datetime import datetime, timezone
from app.extensions import db


class Document(db.Model):
    __tablename__ = "documentos"

    id             = db.Column(db.Integer, primary_key=True)
    cliente_id     = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    tipo           = db.Column(db.String(50), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta           = db.Column(db.String(500), nullable=False)
    subido_por     = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    subido_en      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    cliente = db.relationship("Client", back_populates="documentos")

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "cliente_id":     self.cliente_id,
            "tipo":           self.tipo,
            "nombre_archivo": self.nombre_archivo,
            "subido_por":     self.subido_por,
            "subido_en":      self.subido_en.isoformat() if self.subido_en else None,
        }
