"""
Modelo para la lista de sanciones ONU.
Tabla de referencia para verificar si un cliente está en lista negra.
"""
from app.extensions import db


class ListaNegra(db.Model):
    """Registros de la lista consolidada de sanciones del Consejo de Seguridad de la ONU."""
    __tablename__ = "lista_negra_onu"

    id              = db.Column(db.Integer, primary_key=True)
    registro        = db.Column(db.String(20))       # Código de referencia (CDi.001, etc.)
    nombre          = db.Column(db.String(150))
    apellido        = db.Column(db.String(150))
    cargo           = db.Column(db.String(500))
    fecha_nacimiento = db.Column(db.String(200))
    nacionalidad    = db.Column(db.String(200))
    num_identidad   = db.Column(db.String(300))      # Número nacional de identidad
    num_pasaporte   = db.Column(db.String(500))
    otros           = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "registro": self.registro,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "cargo": self.cargo,
            "fecha_nacimiento": self.fecha_nacimiento,
            "nacionalidad": self.nacionalidad,
            "num_identidad": self.num_identidad,
            "num_pasaporte": self.num_pasaporte,
        }
