from datetime import datetime, timezone
from app.extensions import db


class Client(db.Model):
    __tablename__ = "clientes"
    # La tabla tiene triggers de auditoría: desactivar OUTPUT implícito
    # para que el INSERT sea compatible (usa SCOPE_IDENTITY()).
    __table_args__ = {"implicit_returning": False}

    id               = db.Column(db.Integer, primary_key=True)
    tipo_doc         = db.Column(db.String(10), nullable=False)   # CI, RUC, PAS
    num_doc          = db.Column(db.String(20), unique=True, nullable=False)
    nombre           = db.Column(db.String(100), nullable=False)
    apellido         = db.Column(db.String(100))
    email            = db.Column(db.String(150))
    telefono         = db.Column(db.String(20))
    direccion        = db.Column(db.String(255))
    fecha_nacimiento = db.Column(db.Date)
    nacionalidad     = db.Column(db.String(10), db.ForeignKey("paises.id_pais"))
    id_ciudad        = db.Column(db.Integer, db.ForeignKey("ciudad.id_ciudad"))
    estado           = db.Column(db.String(20), default="activo")
    creado_por       = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    creado_en        = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relaciones
    creado_por_usuario = db.relationship("User", back_populates="clientes_creados")
    evaluaciones       = db.relationship("Evaluation", back_populates="cliente", lazy="dynamic")
    documentos         = db.relationship("Document", back_populates="cliente", lazy="dynamic")
    pais_rel           = db.relationship("Pais", foreign_keys=[nacionalidad])
    ciudad_rel         = db.relationship("Ciudad", foreign_keys=[id_ciudad])
    empresas_rel       = db.relationship("ClienteEmpresa", back_populates="cliente", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "tipo_doc":         self.tipo_doc,
            "num_doc":          self.num_doc,
            "nombre":           self.nombre,
            "apellido":         self.apellido,
            "email":            self.email,
            "telefono":         self.telefono,
            "direccion":        self.direccion,
            "fecha_nacimiento": self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            "nacionalidad":     self.nacionalidad,
            "nacionalidad_nombre": self.pais_rel.nombre_pais if self.pais_rel else None,
            "id_ciudad":        self.id_ciudad,
            "ciudad_nombre":    self.ciudad_rel.nombre_ciudad if self.ciudad_rel else None,
            "estado":           self.estado,
            "creado_por":       self.creado_por,
            "creado_en":        self.creado_en.isoformat() if self.creado_en else None,
        }

    def estado_en_empresa(self, id_empresa: int) -> str:
        """Devuelve el estado del cliente en una empresa específica."""
        for ce in self.empresas_rel:
            if ce.id_empresa == id_empresa:
                return ce.estado
        return "no_vinculado"
