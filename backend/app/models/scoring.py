from datetime import datetime, timezone
from app.extensions import db


class MotorReglas(db.Model):
    """Plantilla de reglas asignada a un cliente/empresa."""
    __tablename__ = "motor_reglas"

    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(100), nullable=False)
    version         = db.Column(db.String(20),  nullable=False, default="1.0")
    descripcion     = db.Column(db.String(255))
    activo          = db.Column(db.Boolean, default=True)
    creado_por      = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    id_empresa_motor = db.Column(db.Integer, default=0)  # 0 = global/propietario
    creado_en       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reglas          = db.relationship("Regla", back_populates="motor",
                                      lazy="dynamic", cascade="all, delete-orphan")
    evaluaciones    = db.relationship("EvaluacionRiesgo", back_populates="motor", lazy="dynamic")

    def to_dict(self, include_reglas=False):
        data = {
            "id":              self.id,
            "nombre":          self.nombre,
            "version":         self.version,
            "descripcion":     self.descripcion,
            "activo":          self.activo,
            "creado_por":      self.creado_por,
            "id_empresa_motor": self.id_empresa_motor,
            "creado_en":       self.creado_en.isoformat() if self.creado_en else None,
            "total_reglas":    self.reglas.count(),
        }
        if include_reglas:
            data["reglas"] = [r.to_dict() for r in self.reglas.order_by(Regla.orden)]
        return data


class Regla(db.Model):
    """Regla individual de evaluación (condición IF-THEN)."""
    __tablename__ = "reglas"

    id               = db.Column(db.Integer, primary_key=True)
    motor_id         = db.Column(db.Integer, db.ForeignKey("motor_reglas.id"), nullable=False)
    nombre           = db.Column(db.String(100), nullable=False)
    descripcion      = db.Column(db.String(255))
    parametro        = db.Column(db.String(50),  nullable=False)   # campo a evaluar
    operador         = db.Column(db.String(10),  nullable=False)   # >=, <=, ==, >, <, !=
    valor_referencia = db.Column(db.String(100), nullable=False)   # umbral (string para flexibilidad)
    tipo_valor       = db.Column(db.String(20),  nullable=False, default="numerico")  # numerico, texto, booleano
    peso_puntos      = db.Column(db.Numeric(6, 2), nullable=False) # puntos si se cumple
    es_determinante  = db.Column(db.Boolean, default=False)        # si falla → rechazo directo
    activo           = db.Column(db.Boolean, default=True)
    orden            = db.Column(db.Integer, default=0)

    motor    = db.relationship("MotorReglas", back_populates="reglas")
    detalles = db.relationship("ResultadoDetalle", back_populates="regla", lazy="dynamic")

    # Parámetros disponibles para configurar en reglas
    PARAMETROS = [
        ("ingresos_mensuales",   "Ingresos Mensuales (Gs)",       "numerico"),
        ("edad",                 "Edad (años)",                    "numerico"),
        ("nivel_endeudamiento",  "Nivel de Endeudamiento (%)",     "numerico"),
        ("meses_empleo_actual",  "Antigüedad Laboral (meses)",     "numerico"),
        ("cantidad_atrasos",     "Cantidad de Atrasos",            "numerico"),
        ("deuda_total_sistema",  "Deuda Total en Sistema (Gs)",    "numerico"),
        ("score_externo",        "Score Crediticio Externo",       "numerico"),
        ("historial_pagos",      "Historial de Pagos",             "texto"),
        ("en_lista_negra",       "En Lista Negra / OFAC",          "booleano"),
        ("tipo_empleo",          "Tipo de Empleo",                 "texto"),
        ("referencias_personales","Referencias Personales",        "texto"),
    ]

    OPERADORES = [">=", "<=", "==", ">", "<", "!="]

    def to_dict(self):
        return {
            "id":               self.id,
            "motor_id":         self.motor_id,
            "nombre":           self.nombre,
            "descripcion":      self.descripcion,
            "parametro":        self.parametro,
            "operador":         self.operador,
            "valor_referencia": self.valor_referencia,
            "tipo_valor":       self.tipo_valor,
            "peso_puntos":      float(self.peso_puntos),
            "es_determinante":  self.es_determinante,
            "activo":           self.activo,
            "orden":            self.orden,
        }


class HistorialCrediticio(db.Model):
    """Datos financieros e histórico del cliente para evaluación."""
    __tablename__ = "historial_crediticio"

    id                   = db.Column(db.Integer, primary_key=True)
    cliente_id           = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, unique=True)
    fuente_externa       = db.Column(db.String(100))
    score_externo        = db.Column(db.Numeric(6, 2))
    cantidad_atrasos     = db.Column(db.Integer, default=0)
    deuda_total_sistema  = db.Column(db.Numeric(14, 2), default=0)
    historial_pagos      = db.Column(db.String(20), default="sin_historial")  # bueno/regular/malo/sin_historial
    en_lista_negra       = db.Column(db.Boolean, default=False)
    nivel_endeudamiento  = db.Column(db.Numeric(5, 2), default=0)  # porcentaje
    meses_empleo_actual  = db.Column(db.Integer, default=0)
    tipo_empleo          = db.Column(db.String(50))  # dependiente/independiente/desempleado
    referencias_personales = db.Column(db.String(20), default="no_verificadas")  # buenas/regulares/malas
    fecha_consulta       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    actualizado_en       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                     onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id":                    self.id,
            "cliente_id":            self.cliente_id,
            "fuente_externa":        self.fuente_externa,
            "score_externo":         float(self.score_externo) if self.score_externo else None,
            "cantidad_atrasos":      self.cantidad_atrasos,
            "deuda_total_sistema":   float(self.deuda_total_sistema) if self.deuda_total_sistema else 0,
            "historial_pagos":       self.historial_pagos,
            "en_lista_negra":        self.en_lista_negra,
            "nivel_endeudamiento":   float(self.nivel_endeudamiento) if self.nivel_endeudamiento else 0,
            "meses_empleo_actual":   self.meses_empleo_actual,
            "tipo_empleo":           self.tipo_empleo,
            "referencias_personales": self.referencias_personales,
            "fecha_consulta":        self.fecha_consulta.isoformat() if self.fecha_consulta else None,
        }


class EvaluacionRiesgo(db.Model):
    """Resultado de una evaluación de riesgo de un cliente."""
    __tablename__ = "evaluacion_riesgo"

    id               = db.Column(db.Integer, primary_key=True)
    cliente_id       = db.Column(db.Integer, db.ForeignKey("clientes.id"),      nullable=False)
    motor_id         = db.Column(db.Integer, db.ForeignKey("motor_reglas.id"),  nullable=False)
    usuario_id       = db.Column(db.Integer, db.ForeignKey("usuarios.id"),      nullable=False)
    fecha_analisis   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    score_final      = db.Column(db.Numeric(6, 2))
    score_maximo     = db.Column(db.Numeric(6, 2))
    categoria_riesgo = db.Column(db.String(20))   # bajo / medio / alto / rechazado
    estado           = db.Column(db.String(20), default="completado")
    observaciones    = db.Column(db.Text)
    regla_determinante_id = db.Column(db.Integer, db.ForeignKey("reglas.id"), nullable=True)
    id_empresa       = db.Column(db.Integer, default=0)

    motor    = db.relationship("MotorReglas",  back_populates="evaluaciones")
    detalles = db.relationship("ResultadoDetalle", back_populates="evaluacion",
                               lazy="joined", cascade="all, delete-orphan")
    operacion = db.relationship("DetalleOperacion", back_populates="evaluacion",
                                uselist=False, cascade="all, delete-orphan")

    def to_dict(self, include_detalles=False):
        data = {
            "id":               self.id,
            "cliente_id":       self.cliente_id,
            "motor_id":         self.motor_id,
            "usuario_id":       self.usuario_id,
            "fecha_analisis":   self.fecha_analisis.isoformat() if self.fecha_analisis else None,
            "score_final":      float(self.score_final) if self.score_final else 0,
            "score_maximo":     float(self.score_maximo) if self.score_maximo else 0,
            "categoria_riesgo": self.categoria_riesgo,
            "estado":           self.estado,
            "observaciones":    self.observaciones,
            "regla_determinante_id": self.regla_determinante_id,
        }
        if self.operacion:
            data["operacion"] = self.operacion.to_dict()
        if include_detalles:
            data["detalles"] = [d.to_dict() for d in self.detalles]
        return data


class ResultadoDetalle(db.Model):
    """Detalle por regla de una evaluación de riesgo."""
    __tablename__ = "resultado_detalle"

    id              = db.Column(db.Integer, primary_key=True)
    evaluacion_id   = db.Column(db.Integer, db.ForeignKey("evaluacion_riesgo.id"), nullable=False)
    regla_id        = db.Column(db.Integer, db.ForeignKey("reglas.id"),             nullable=False)
    cumplido        = db.Column(db.Boolean,        nullable=False)
    valor_evaluado  = db.Column(db.String(100))   # valor real del cliente en ese momento
    puntos_obtenidos = db.Column(db.Numeric(6, 2), default=0)

    evaluacion = db.relationship("EvaluacionRiesgo", back_populates="detalles")
    regla      = db.relationship("Regla", back_populates="detalles")

    def to_dict(self):
        return {
            "regla_id":         self.regla_id,
            "regla_nombre":     self.regla.nombre if self.regla else None,
            "parametro":        self.regla.parametro if self.regla else None,
            "operador":         self.regla.operador if self.regla else None,
            "valor_referencia": self.regla.valor_referencia if self.regla else None,
            "valor_evaluado":   self.valor_evaluado,
            "cumplido":         self.cumplido,
            "puntos_obtenidos": float(self.puntos_obtenidos),
            "peso_puntos":      float(self.regla.peso_puntos) if self.regla else 0,
            "es_determinante":  self.regla.es_determinante if self.regla else False,
        }


class DetalleOperacion(db.Model):
    """Datos de la operación inmobiliaria asociada a una evaluación de riesgo."""
    __tablename__ = "detalle_operacion"

    id              = db.Column(db.Integer, primary_key=True)
    evaluacion_id   = db.Column(db.Integer, db.ForeignKey("evaluacion_riesgo.id"), nullable=False)
    tipo_propiedad  = db.Column(db.String(50), nullable=False)   # casa, departamento, terreno, local_comercial
    valor_propiedad = db.Column(db.Numeric(14, 2), nullable=False)
    monto_solicitado = db.Column(db.Numeric(14, 2), nullable=False)
    plazo_meses     = db.Column(db.Integer, nullable=False)
    ubicacion       = db.Column(db.String(255))
    destino         = db.Column(db.String(50))  # vivienda, inversion, comercial

    evaluacion = db.relationship("EvaluacionRiesgo", back_populates="operacion")

    TIPOS_PROPIEDAD = ["casa", "departamento", "terreno", "local_comercial", "oficina"]
    DESTINOS = ["vivienda", "inversion", "comercial"]

    def to_dict(self):
        return {
            "id":               self.id,
            "evaluacion_id":    self.evaluacion_id,
            "tipo_propiedad":   self.tipo_propiedad,
            "valor_propiedad":  float(self.valor_propiedad) if self.valor_propiedad else 0,
            "monto_solicitado": float(self.monto_solicitado) if self.monto_solicitado else 0,
            "plazo_meses":      self.plazo_meses,
            "ubicacion":        self.ubicacion,
            "destino":          self.destino,
        }
