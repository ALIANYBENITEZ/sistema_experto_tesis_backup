from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "usuarios"
    # La tabla tiene triggers de auditoría: desactivar OUTPUT implícito.
    __table_args__ = {"implicit_returning": False}

    id             = db.Column(db.Integer, primary_key=True)
    nombre         = db.Column(db.String(100), nullable=False)
    apellido       = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(150), unique=True, nullable=False)
    password_hash  = db.Column(db.String(255), nullable=False)
    rol            = db.Column(db.String(20), nullable=False, default="comercial")
    activo         = db.Column(db.Boolean, default=True)
    id_empresa     = db.Column(db.Integer, default=0)
    # 2FA fields
    totp_secret    = db.Column(db.String(255), nullable=True)  # Encrypted TOTP secret
    totp_estado    = db.Column(db.String(20), default="no_configurado")  # no_configurado, pendiente, activado, restablecido
    totp_fecha_config = db.Column(db.DateTime, nullable=True)
    totp_fecha_reset  = db.Column(db.DateTime, nullable=True)

    creado_en      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    actualizado_en = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relaciones
    clientes_creados = db.relationship("Client", back_populates="creado_por_usuario", lazy="dynamic")
    evaluaciones     = db.relationship("Evaluation", back_populates="evaluador", lazy="dynamic")
    empresa          = db.relationship("Empresa",
                                       primaryjoin="foreign(User.id_empresa) == Empresa.id",
                                       back_populates="usuarios", lazy="joined", viewonly=True)

    # Roles del sistema
    ROL_PROPIETARIO  = "propietario"
    ROL_ADMIN        = "administrador"
    ROL_COMERCIAL    = "comercial"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_propietario(self) -> bool:
        return self.rol == self.ROL_PROPIETARIO and self.id_empresa == 0

    def is_admin(self) -> bool:
        return self.rol in (self.ROL_PROPIETARIO, self.ROL_ADMIN)

    @property
    def tiene_2fa(self) -> bool:
        return self.totp_estado == "activado"

    @property
    def requiere_config_2fa(self) -> bool:
        return self.totp_estado in ("no_configurado", "restablecido", "pendiente", None)

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "apellido":    self.apellido,
            "email":       self.email,
            "rol":         self.rol,
            "activo":      self.activo,
            "id_empresa":  self.id_empresa,
            "empresa_nombre": self.empresa.nombre if self.empresa else ("Sistema" if self.id_empresa == 0 else None),
            "totp_estado": self.totp_estado,
            "tiene_2fa":   self.tiene_2fa,
            "creado_en":   self.creado_en.isoformat() if self.creado_en else None,
        }
