"""
Modelos de datos del Core de Scoring.
Tablas independientes del sistema existente, prefijadas con 'scoring_'.
"""
from datetime import datetime, timezone
from app.extensions import db


class ModeloScoring(db.Model):
    """Versión del modelo de scoring. Permite versionamiento."""
    __tablename__ = "scoring_modelo"

    id           = db.Column(db.Integer, primary_key=True)
    nombre       = db.Column(db.String(100), nullable=False)
    version      = db.Column(db.String(20), nullable=False, default="1.0")
    descripcion  = db.Column(db.String(500))
    id_empresa   = db.Column(db.Integer, nullable=False, default=0)
    activo       = db.Column(db.Boolean, default=True)
    creado_en    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    factores = db.relationship("FactorScoring", back_populates="modelo",
                               lazy="dynamic", cascade="all, delete-orphan")
    umbrales = db.relationship("UmbralScoring", back_populates="modelo",
                               lazy="joined", cascade="all, delete-orphan")

    def to_dict(self, include_factores=False):
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "version": self.version,
            "descripcion": self.descripcion,
            "id_empresa": self.id_empresa,
            "activo": self.activo,
            "total_factores": self.factores.count(),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
        if include_factores:
            data["factores"] = [f.to_dict(include_reglas=True) for f in
                                self.factores.filter_by(activo=True).order_by(FactorScoring.orden)]
            data["umbrales"] = [u.to_dict() for u in self.umbrales]
        return data


class FactorScoring(db.Model):
    """Factor de evaluación configurable."""
    __tablename__ = "scoring_factor"

    id             = db.Column(db.Integer, primary_key=True)
    modelo_id      = db.Column(db.Integer, db.ForeignKey("scoring_modelo.id"), nullable=False)
    codigo         = db.Column(db.String(50), nullable=False)  # identificador único dentro del modelo
    nombre         = db.Column(db.String(100), nullable=False)
    descripcion    = db.Column(db.String(500))
    tipo_dato      = db.Column(db.String(20), nullable=False, default="numerico")
    tipo_persona   = db.Column(db.String(10), nullable=False, default="AMBOS")  # PF, PJ, AMBOS
    categoria      = db.Column(db.String(20), default="principal")  # principal / complementario
    obligatorio    = db.Column(db.Boolean, default=True)
    activo         = db.Column(db.Boolean, default=True)
    orden          = db.Column(db.Integer, default=0)

    modelo   = db.relationship("ModeloScoring", back_populates="factores")
    reglas   = db.relationship("ReglaScoring", back_populates="factor",
                               lazy="joined", cascade="all, delete-orphan",
                               order_by="ReglaScoring.orden")
    catalogo = db.relationship("CatalogoScoring", back_populates="factor",
                               lazy="joined", cascade="all, delete-orphan")

    def to_dict(self, include_reglas=False):
        data = {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "tipo_dato": self.tipo_dato,
            "tipo_persona": self.tipo_persona,
            "categoria": self.categoria,
            "obligatorio": self.obligatorio,
            "activo": self.activo,
            "orden": self.orden,
        }
        if include_reglas:
            data["reglas"] = [r.to_dict() for r in self.reglas]
            if self.catalogo:
                data["catalogo"] = [c.to_dict() for c in self.catalogo]
        return data


class CatalogoScoring(db.Model):
    """Opciones válidas para factores de tipo catálogo."""
    __tablename__ = "scoring_catalogo"

    id        = db.Column(db.Integer, primary_key=True)
    factor_id = db.Column(db.Integer, db.ForeignKey("scoring_factor.id"), nullable=False)
    valor     = db.Column(db.String(100), nullable=False)
    etiqueta  = db.Column(db.String(100), nullable=False)
    orden     = db.Column(db.Integer, default=0)

    factor = db.relationship("FactorScoring", back_populates="catalogo")

    def to_dict(self):
        return {"id": self.id, "valor": self.valor, "etiqueta": self.etiqueta, "orden": self.orden}


class ReglaScoring(db.Model):
    """Regla IF-THEN para un factor específico."""
    __tablename__ = "scoring_regla"

    id              = db.Column(db.Integer, primary_key=True)
    factor_id       = db.Column(db.Integer, db.ForeignKey("scoring_factor.id"), nullable=False)
    nombre          = db.Column(db.String(100), nullable=False)
    operador        = db.Column(db.String(10), nullable=False)   # >=, <=, ==, entre, en
    valor_min       = db.Column(db.String(100))                  # valor o límite inferior
    valor_max       = db.Column(db.String(100))                  # límite superior (para 'entre')
    nivel           = db.Column(db.String(10), nullable=False)   # bajo, medio, alto
    peso            = db.Column(db.Numeric(8, 2), nullable=False)  # positivo=desfavorable, negativo=favorable
    explicacion     = db.Column(db.String(500))                  # texto explicativo
    orden           = db.Column(db.Integer, default=0)

    factor = db.relationship("FactorScoring", back_populates="reglas")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "operador": self.operador,
            "valor_min": self.valor_min,
            "valor_max": self.valor_max,
            "nivel": self.nivel,
            "peso": float(self.peso),
            "explicacion": self.explicacion,
            "orden": self.orden,
        }


class UmbralScoring(db.Model):
    """Umbrales de clasificación global del score."""
    __tablename__ = "scoring_umbral"

    id          = db.Column(db.Integer, primary_key=True)
    modelo_id   = db.Column(db.Integer, db.ForeignKey("scoring_modelo.id"), nullable=False)
    nivel       = db.Column(db.String(10), nullable=False)  # bajo, medio, alto
    score_min   = db.Column(db.Numeric(8, 2), nullable=False)
    score_max   = db.Column(db.Numeric(8, 2), nullable=False)
    descripcion = db.Column(db.String(200))

    modelo = db.relationship("ModeloScoring", back_populates="umbrales")

    def to_dict(self):
        return {
            "id": self.id,
            "nivel": self.nivel,
            "score_min": float(self.score_min),
            "score_max": float(self.score_max),
            "descripcion": self.descripcion,
        }


class EvaluacionScoring(db.Model):
    """Resultado completo de una evaluación del Core."""
    __tablename__ = "scoring_evaluacion"

    id               = db.Column(db.Integer, primary_key=True)
    cliente_id       = db.Column(db.Integer, nullable=False)
    modelo_id        = db.Column(db.Integer, db.ForeignKey("scoring_modelo.id"), nullable=False)
    modelo_version   = db.Column(db.String(20), nullable=False)
    usuario_id       = db.Column(db.Integer, nullable=False)
    id_empresa       = db.Column(db.Integer, nullable=False, default=0)
    tipo_persona     = db.Column(db.String(10), nullable=False)
    fecha            = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    score_total      = db.Column(db.Numeric(8, 2), nullable=False)
    clasificacion    = db.Column(db.String(10), nullable=False)  # bajo, medio, alto
    explicacion      = db.Column(db.Text)
    factores_evaluados   = db.Column(db.Integer, default=0)
    factores_sin_dato    = db.Column(db.Integer, default=0)
    estado           = db.Column(db.String(20), default="completa")  # completa, incompleta

    detalles = db.relationship("DetalleEvaluacionScoring", back_populates="evaluacion",
                               lazy="joined", cascade="all, delete-orphan")

    def to_dict(self, include_detalles=False):
        data = {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "modelo_id": self.modelo_id,
            "modelo_version": self.modelo_version,
            "usuario_id": self.usuario_id,
            "id_empresa": self.id_empresa,
            "tipo_persona": self.tipo_persona,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "score_total": float(self.score_total),
            "clasificacion": self.clasificacion,
            "explicacion": self.explicacion,
            "factores_evaluados": self.factores_evaluados,
            "factores_sin_dato": self.factores_sin_dato,
            "estado": self.estado,
        }
        if include_detalles:
            data["detalles"] = [d.to_dict() for d in self.detalles]
        return data


class DetalleEvaluacionScoring(db.Model):
    """Resultado individual por factor de una evaluación."""
    __tablename__ = "scoring_detalle"

    id              = db.Column(db.Integer, primary_key=True)
    evaluacion_id   = db.Column(db.Integer, db.ForeignKey("scoring_evaluacion.id"), nullable=False)
    factor_codigo   = db.Column(db.String(50), nullable=False)
    factor_nombre   = db.Column(db.String(100), nullable=False)
    categoria       = db.Column(db.String(20))  # principal / complementario
    valor_original  = db.Column(db.String(200))  # valor que tenía el cliente
    estado          = db.Column(db.String(20), nullable=False)  # evaluado, sin_dato, no_aplica, invalido
    regla_aplicada  = db.Column(db.String(100))  # nombre de la regla que se aplicó
    nivel           = db.Column(db.String(10))   # bajo, medio, alto
    peso            = db.Column(db.Numeric(8, 2), default=0)
    explicacion     = db.Column(db.String(500))

    evaluacion = db.relationship("EvaluacionScoring", back_populates="detalles")

    def to_dict(self):
        return {
            "factor_codigo": self.factor_codigo,
            "factor_nombre": self.factor_nombre,
            "categoria": self.categoria,
            "valor_original": self.valor_original,
            "estado": self.estado,
            "regla_aplicada": self.regla_aplicada,
            "nivel": self.nivel,
            "peso": float(self.peso) if self.peso else 0,
            "explicacion": self.explicacion,
        }
