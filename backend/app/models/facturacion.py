"""
Modelos de Facturación — Sistema Prepago por Reportes.
Tablas paramétricas: planes, empresa_planes, periodos_facturacion, consumo_reportes, pagos, historial_empresa_planes.
"""
from datetime import datetime, timezone
from app.extensions import db


class Plan(db.Model):
    """Catálogo de planes comerciales (tabla paramétrica)."""
    __tablename__ = "planes"

    id                          = db.Column(db.Integer, primary_key=True)
    nombre                      = db.Column(db.String(50), nullable=False, unique=True)
    cantidad_reportes_incluidos = db.Column(db.Integer, nullable=False)
    precio_plan                 = db.Column(db.Numeric(14, 0), nullable=False)  # Gs
    precio_reporte_incluido     = db.Column(db.Numeric(14, 0), nullable=False)  # referencia
    precio_reporte_sobre_facturado = db.Column(db.Numeric(14, 0), nullable=False)
    activo                      = db.Column(db.Boolean, default=True)
    creado_en                   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    actualizado_en              = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                            onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cantidad_reportes_incluidos": self.cantidad_reportes_incluidos,
            "precio_plan": int(self.precio_plan),
            "precio_reporte_incluido": int(self.precio_reporte_incluido),
            "precio_reporte_sobre_facturado": int(self.precio_reporte_sobre_facturado),
            "activo": self.activo,
        }


class EmpresaPlan(db.Model):
    """Plan vigente asignado a una empresa (con copia de valores al momento de contratación)."""
    __tablename__ = "empresa_planes"

    id                          = db.Column(db.Integer, primary_key=True)
    empresa_id                  = db.Column(db.Integer, nullable=False)
    plan_id                     = db.Column(db.Integer, db.ForeignKey("planes.id"), nullable=False)
    fecha_inicio                = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    fecha_fin                   = db.Column(db.DateTime, nullable=True)
    estado                      = db.Column(db.String(20), default="activo")  # activo, finalizado
    # Copia de valores al momento de contratación
    precio_plan_contratado      = db.Column(db.Numeric(14, 0), nullable=False)
    cantidad_reportes_incluidos = db.Column(db.Integer, nullable=False)
    precio_reporte_sobre_facturado = db.Column(db.Numeric(14, 0), nullable=False)
    creado_en                   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    plan = db.relationship("Plan", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "plan_id": self.plan_id,
            "plan_nombre": self.plan.nombre if self.plan else None,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "estado": self.estado,
            "precio_plan_contratado": int(self.precio_plan_contratado),
            "cantidad_reportes_incluidos": self.cantidad_reportes_incluidos,
            "precio_reporte_sobre_facturado": int(self.precio_reporte_sobre_facturado),
        }


class PeriodoFacturacion(db.Model):
    """Período mensual de facturación por empresa."""
    __tablename__ = "periodos_facturacion"

    id                        = db.Column(db.Integer, primary_key=True)
    empresa_id                = db.Column(db.Integer, nullable=False)
    empresa_plan_id           = db.Column(db.Integer, db.ForeignKey("empresa_planes.id"), nullable=False)
    anio                      = db.Column(db.Integer, nullable=False)
    mes                       = db.Column(db.Integer, nullable=False)
    fecha_inicio              = db.Column(db.DateTime, nullable=False)
    fecha_fin                 = db.Column(db.DateTime, nullable=False)
    cantidad_reportes_incluidos = db.Column(db.Integer, nullable=False)
    reportes_consumidos       = db.Column(db.Integer, default=0)
    reportes_sobre_facturados = db.Column(db.Integer, default=0)
    monto_plan                = db.Column(db.Numeric(14, 0), default=0)
    monto_sobre_facturado     = db.Column(db.Numeric(14, 0), default=0)
    monto_total               = db.Column(db.Numeric(14, 0), default=0)
    monto_pagado              = db.Column(db.Numeric(14, 0), default=0)
    saldo_pendiente           = db.Column(db.Numeric(14, 0), default=0)
    estado                    = db.Column(db.String(20), default="PENDIENTE")  # PENDIENTE, PARCIAL, PAGADO, VENCIDO, BLOQUEADO

    __table_args__ = (db.UniqueConstraint('empresa_id', 'anio', 'mes', name='uq_periodo_empresa_mes'),)

    def to_dict(self):
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "anio": self.anio,
            "mes": self.mes,
            "cantidad_reportes_incluidos": self.cantidad_reportes_incluidos,
            "reportes_consumidos": self.reportes_consumidos,
            "reportes_sobre_facturados": self.reportes_sobre_facturados,
            "monto_plan": int(self.monto_plan),
            "monto_sobre_facturado": int(self.monto_sobre_facturado),
            "monto_total": int(self.monto_total),
            "monto_pagado": int(self.monto_pagado),
            "saldo_pendiente": int(self.saldo_pendiente),
            "estado": self.estado,
        }


class ConsumoReporte(db.Model):
    """Registro individual de cada reporte consumido."""
    __tablename__ = "consumo_reportes"

    id                      = db.Column(db.Integer, primary_key=True)
    empresa_id              = db.Column(db.Integer, nullable=False)
    usuario_id              = db.Column(db.Integer, nullable=False)
    evaluacion_id           = db.Column(db.Integer, nullable=False)
    periodo_facturacion_id  = db.Column(db.Integer, db.ForeignKey("periodos_facturacion.id"), nullable=False)
    tipo_consumo            = db.Column(db.String(20), nullable=False)  # INCLUIDO, SOBRE_FACTURADO
    precio_unitario         = db.Column(db.Numeric(14, 0), nullable=False)
    fecha_consumo           = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('evaluacion_id', 'empresa_id', name='uq_consumo_evaluacion'),)

    def to_dict(self):
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "usuario_id": self.usuario_id,
            "evaluacion_id": self.evaluacion_id,
            "tipo_consumo": self.tipo_consumo,
            "precio_unitario": int(self.precio_unitario),
            "fecha_consumo": self.fecha_consumo.isoformat() if self.fecha_consumo else None,
        }


class Pago(db.Model):
    """Transacciones de pago."""
    __tablename__ = "pagos"

    id                      = db.Column(db.Integer, primary_key=True)
    empresa_id              = db.Column(db.Integer, nullable=False)
    periodo_facturacion_id  = db.Column(db.Integer, db.ForeignKey("periodos_facturacion.id"), nullable=False)
    monto                   = db.Column(db.Numeric(14, 0), nullable=False)
    proveedor               = db.Column(db.String(50), default="TEST")  # TEST, BANCARD, PAGOPAR
    referencia_externa      = db.Column(db.String(100))
    estado                  = db.Column(db.String(20), default="PENDIENTE")  # PENDIENTE, APROBADO, RECHAZADO, CANCELADO
    metodo_pago             = db.Column(db.String(50))
    observacion             = db.Column(db.String(255))
    fecha_inicio            = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_confirmacion      = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "periodo_facturacion_id": self.periodo_facturacion_id,
            "monto": int(self.monto),
            "proveedor": self.proveedor,
            "referencia_externa": self.referencia_externa,
            "estado": self.estado,
            "metodo_pago": self.metodo_pago,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_confirmacion": self.fecha_confirmacion.isoformat() if self.fecha_confirmacion else None,
        }


class HistorialEmpresaPlan(db.Model):
    """Historial de cambios de plan por empresa."""
    __tablename__ = "historial_empresa_planes"

    id                = db.Column(db.Integer, primary_key=True)
    empresa_id        = db.Column(db.Integer, nullable=False)
    plan_id           = db.Column(db.Integer, nullable=False)
    plan_nombre       = db.Column(db.String(50), nullable=False)
    precio_plan       = db.Column(db.Numeric(14, 0), nullable=False)
    cantidad_reportes = db.Column(db.Integer, nullable=False)
    precio_sobre_fact = db.Column(db.Numeric(14, 0), nullable=False)
    fecha_desde       = db.Column(db.DateTime, nullable=False)
    fecha_hasta       = db.Column(db.DateTime, nullable=True)
    cambiado_por      = db.Column(db.Integer, nullable=True)
    fecha_cambio      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "plan_nombre": self.plan_nombre,
            "precio_plan": int(self.precio_plan),
            "cantidad_reportes": self.cantidad_reportes,
            "precio_sobre_fact": int(self.precio_sobre_fact),
            "fecha_desde": self.fecha_desde.isoformat() if self.fecha_desde else None,
            "fecha_hasta": self.fecha_hasta.isoformat() if self.fecha_hasta else None,
        }
