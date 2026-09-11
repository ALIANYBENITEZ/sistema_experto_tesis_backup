from app.extensions import db


class Pais(db.Model):
    __tablename__ = "paises"

    id_pais     = db.Column(db.String(10), primary_key=True)
    nombre_pais = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id_pais, "nombre": self.nombre_pais}


class Departamento(db.Model):
    """Departamentos de Paraguay."""
    __tablename__ = "departamento"

    id_departamento     = db.Column(db.Integer, primary_key=True)
    nombre_departamento = db.Column(db.String(100), nullable=False)

    ciudades = db.relationship("Ciudad", back_populates="departamento", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id_departamento, "nombre": self.nombre_departamento}


class Ciudad(db.Model):
    __tablename__ = "ciudad"

    id_ciudad        = db.Column(db.Integer, primary_key=True)
    nombre_ciudad    = db.Column(db.String(100), nullable=False)
    id_departamento  = db.Column(db.Integer, db.ForeignKey("departamento.id_departamento"), nullable=False)

    departamento = db.relationship("Departamento", back_populates="ciudades")

    def to_dict(self):
        return {
            "id": self.id_ciudad,
            "nombre": self.nombre_ciudad,
            "id_departamento": self.id_departamento,
        }
