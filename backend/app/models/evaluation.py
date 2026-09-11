from datetime import datetime, timezone
from app.extensions import db


class Criterion(db.Model):
    __tablename__ = "criterios"

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    peso        = db.Column(db.Numeric(5, 2), nullable=False)  # % ponderación
    activo      = db.Column(db.Boolean, default=True)

    detalles = db.relationship("EvaluationDetail", back_populates="criterio", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "descripcion": self.descripcion,
            "peso":        float(self.peso),
            "activo":      self.activo,
        }


class Evaluation(db.Model):
    __tablename__ = "evaluaciones"

    id            = db.Column(db.Integer, primary_key=True)
    cliente_id    = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    evaluador_id  = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha         = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    puntaje_total = db.Column(db.Numeric(5, 2))
    resultado     = db.Column(db.String(20))   # aprobado / observado / rechazado
    observaciones = db.Column(db.Text)
    estado        = db.Column(db.String(20), default="pendiente")

    # Relaciones
    cliente   = db.relationship("Client", back_populates="evaluaciones")
    evaluador = db.relationship("User", back_populates="evaluaciones")
    detalles  = db.relationship("EvaluationDetail", back_populates="evaluacion", lazy="joined", cascade="all, delete-orphan")

    def to_dict(self, include_detalles: bool = False) -> dict:
        data = {
            "id":            self.id,
            "cliente_id":    self.cliente_id,
            "evaluador_id":  self.evaluador_id,
            "fecha":         self.fecha.isoformat() if self.fecha else None,
            "puntaje_total": float(self.puntaje_total) if self.puntaje_total else None,
            "resultado":     self.resultado,
            "observaciones": self.observaciones,
            "estado":        self.estado,
        }
        if include_detalles:
            data["detalles"] = [d.to_dict() for d in self.detalles]
        return data


class EvaluationDetail(db.Model):
    __tablename__ = "evaluacion_detalle"

    id            = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey("evaluaciones.id"), nullable=False)
    criterio_id   = db.Column(db.Integer, db.ForeignKey("criterios.id"), nullable=False)
    valor         = db.Column(db.Numeric(5, 2), nullable=False)
    comentario    = db.Column(db.String(255))

    evaluacion = db.relationship("Evaluation", back_populates="detalles")
    criterio   = db.relationship("Criterion", back_populates="detalles")

    def to_dict(self) -> dict:
        return {
            "criterio_id":   self.criterio_id,
            "criterio_nombre": self.criterio.nombre if self.criterio else None,
            "valor":         float(self.valor),
            "comentario":    self.comentario,
        }
