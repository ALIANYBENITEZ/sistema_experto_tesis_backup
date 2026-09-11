"""
API de Facturación — Planes, Consumo, Pagos, Bloqueo.
"""
from datetime import datetime, timezone
from flask import request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Empresa
from app.models.facturacion import (
    Plan, EmpresaPlan, PeriodoFacturacion, ConsumoReporte, Pago, HistorialEmpresaPlan,
)
from app.utils.decorators import get_current_user, propietario_required, admin_required
from app.utils.responses import success, error
from app.services.auditoria_service import registrar as auditar
from . import facturacion_bp
import uuid


# ══════════════════════════════════════════════════════════════
#  PLANES (Paramétrica — Solo propietario puede modificar)
# ══════════════════════════════════════════════════════════════

@facturacion_bp.route("/planes", methods=["GET"])
@jwt_required()
def list_planes():
    planes = Plan.query.filter_by(activo=True).order_by(Plan.id).all()
    return success(data=[p.to_dict() for p in planes])


@facturacion_bp.route("/planes", methods=["POST"])
@propietario_required
def create_plan():
    data = request.get_json(silent=True) or {}
    required = ["nombre", "cantidad_reportes_incluidos", "precio_plan", "precio_reporte_sobre_facturado"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    plan = Plan(
        nombre=data["nombre"].strip(),
        cantidad_reportes_incluidos=int(data["cantidad_reportes_incluidos"]),
        precio_plan=int(data["precio_plan"]),
        precio_reporte_incluido=int(data.get("precio_reporte_incluido", 0)) or (int(data["precio_plan"]) // int(data["cantidad_reportes_incluidos"])),
        precio_reporte_sobre_facturado=int(data["precio_reporte_sobre_facturado"]),
    )
    db.session.add(plan)
    db.session.commit()
    return success(data=plan.to_dict(), message="Plan creado", status=201)


@facturacion_bp.route("/planes/<int:plan_id>", methods=["PUT"])
@propietario_required
def update_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json(silent=True) or {}
    for field in ("nombre", "cantidad_reportes_incluidos", "precio_plan", "precio_reporte_incluido", "precio_reporte_sobre_facturado"):
        if field in data:
            setattr(plan, field, data[field])
    if "activo" in data:
        plan.activo = bool(data["activo"])
    db.session.commit()
    return success(data=plan.to_dict(), message="Plan actualizado")


# ══════════════════════════════════════════════════════════════
#  MI FACTURACIÓN (Admin empresa)
# ══════════════════════════════════════════════════════════════

@facturacion_bp.route("/mi-plan", methods=["GET"])
@jwt_required()
def mi_plan():
    """Obtener plan y consumo actual de mi empresa."""
    current_user = get_current_user()
    if not current_user.id_empresa or current_user.id_empresa == 0:
        return error("No aplica para el propietario del sistema", 400)

    plan_vigente = EmpresaPlan.query.filter_by(
        empresa_id=current_user.id_empresa, estado="activo"
    ).first()

    if not plan_vigente:
        return success(data={"plan": None, "periodo": None})

    # Período actual
    ahora = datetime.now(timezone.utc)
    periodo = PeriodoFacturacion.query.filter_by(
        empresa_id=current_user.id_empresa, anio=ahora.year, mes=ahora.month
    ).first()

    return success(data={
        "plan": plan_vigente.to_dict(),
        "periodo": periodo.to_dict() if periodo else None,
        "reportes_restantes": max(0, plan_vigente.cantidad_reportes_incluidos - (periodo.reportes_consumidos if periodo else 0)),
    })


@facturacion_bp.route("/mi-historial", methods=["GET"])
@jwt_required()
def mi_historial():
    """Historial de períodos de facturación de mi empresa."""
    current_user = get_current_user()
    if not current_user.id_empresa:
        return error("No aplica", 400)

    periodos = PeriodoFacturacion.query.filter_by(
        empresa_id=current_user.id_empresa
    ).order_by(PeriodoFacturacion.anio.desc(), PeriodoFacturacion.mes.desc()).all()

    return success(data=[p.to_dict() for p in periodos])


# ══════════════════════════════════════════════════════════════
#  PAGOS
# ══════════════════════════════════════════════════════════════

@facturacion_bp.route("/pagos", methods=["POST"])
@jwt_required()
def crear_pago():
    """Crear una transacción de pago (modo TEST)."""
    current_user = get_current_user()
    data = request.get_json(silent=True) or {}

    periodo_id = data.get("periodo_facturacion_id")
    if not periodo_id:
        return error("periodo_facturacion_id requerido", 400)

    periodo = PeriodoFacturacion.query.get_or_404(periodo_id)

    # Validar que sea de su empresa (o propietario)
    if not current_user.is_propietario() and periodo.empresa_id != current_user.id_empresa:
        return error("No tiene permisos", 403)

    monto = int(data.get("monto", periodo.saldo_pendiente))

    pago = Pago(
        empresa_id=periodo.empresa_id,
        periodo_facturacion_id=periodo_id,
        monto=monto,
        proveedor="TEST",
        referencia_externa=f"TEST-{uuid.uuid4().hex[:8].upper()}",
        metodo_pago="test_simulado",
    )
    db.session.add(pago)
    db.session.commit()

    return success(data=pago.to_dict(), message="Pago creado (pendiente de confirmación)", status=201)


@facturacion_bp.route("/pagos/<int:pago_id>/test-aprobar", methods=["POST"])
@jwt_required()
def test_aprobar_pago(pago_id):
    """Simular aprobación de pago (modo TEST)."""
    pago = Pago.query.get_or_404(pago_id)
    if pago.estado != "PENDIENTE":
        return error("El pago ya fue procesado", 400)

    pago.estado = "APROBADO"
    pago.fecha_confirmacion = datetime.now(timezone.utc)

    # Actualizar período
    periodo = PeriodoFacturacion.query.get(pago.periodo_facturacion_id)
    periodo.monto_pagado = int(periodo.monto_pagado or 0) + int(pago.monto)
    periodo.saldo_pendiente = int(periodo.monto_total) - int(periodo.monto_pagado)
    desbloqueo_auto = False
    if periodo.saldo_pendiente <= 0:
        periodo.estado = "PAGADO"
        # Desbloqueo automático si estaba bloqueada por deuda
        empresa = Empresa.query.get(periodo.empresa_id)
        if empresa and not empresa.consultas_habilitadas and empresa.motivo_bloqueo == "BLOQUEADO_DEUDA":
            empresa.consultas_habilitadas = True
            empresa.motivo_bloqueo = None
            empresa.fecha_desbloqueo = datetime.now(timezone.utc)
            desbloqueo_auto = True
    else:
        periodo.estado = "PARCIAL"

    db.session.commit()
    auditar("FACTURACION", "PAGO_APROBADO", usuario=get_current_user(), modulo="Facturacion",
            entidad="Pago", registro_id=pago.id, resultado="EXITO",
            info={"empresa_id": pago.empresa_id, "monto": int(pago.monto),
                  "referencia": pago.referencia_externa, "estado_periodo": periodo.estado,
                  "desbloqueo_automatico": desbloqueo_auto})
    return success(data=pago.to_dict(), message="Pago aprobado")


@facturacion_bp.route("/pagos/<int:pago_id>/test-rechazar", methods=["POST"])
@jwt_required()
def test_rechazar_pago(pago_id):
    """Simular rechazo de pago (modo TEST)."""
    pago = Pago.query.get_or_404(pago_id)
    if pago.estado != "PENDIENTE":
        return error("El pago ya fue procesado", 400)
    pago.estado = "RECHAZADO"
    pago.fecha_confirmacion = datetime.now(timezone.utc)
    db.session.commit()
    auditar("FACTURACION", "PAGO_RECHAZADO", usuario=get_current_user(), modulo="Facturacion",
            entidad="Pago", registro_id=pago.id, resultado="FALLO",
            info={"empresa_id": pago.empresa_id, "monto": int(pago.monto),
                  "referencia": pago.referencia_externa})
    return success(data=pago.to_dict(), message="Pago rechazado")


@facturacion_bp.route("/pagos", methods=["GET"])
@jwt_required()
def list_pagos():
    current_user = get_current_user()
    if current_user.is_propietario():
        pagos = Pago.query.order_by(Pago.fecha_inicio.desc()).limit(50).all()
    else:
        pagos = Pago.query.filter_by(empresa_id=current_user.id_empresa).order_by(Pago.fecha_inicio.desc()).all()
    return success(data=[p.to_dict() for p in pagos])


# ══════════════════════════════════════════════════════════════
#  PROPIETARIO — Gestión de facturación de todas las empresas
# ══════════════════════════════════════════════════════════════

@facturacion_bp.route("/admin/empresas", methods=["GET"])
@propietario_required
def admin_facturacion_empresas():
    """Vista general de facturación de todas las empresas."""
    empresas = Empresa.query.filter(Empresa.id > 0).order_by(Empresa.nombre).all()
    ahora = datetime.now(timezone.utc)

    data = []
    for emp in empresas:
        plan = EmpresaPlan.query.filter_by(empresa_id=emp.id, estado="activo").first()
        periodo = PeriodoFacturacion.query.filter_by(
            empresa_id=emp.id, anio=ahora.year, mes=ahora.month
        ).first()

        data.append({
            "empresa_id": emp.id,
            "empresa_nombre": emp.nombre,
            "plan_nombre": plan.plan.nombre if plan and plan.plan else "Sin plan",
            "reportes_incluidos": plan.cantidad_reportes_incluidos if plan else 0,
            "reportes_consumidos": periodo.reportes_consumidos if periodo else 0,
            "sobre_facturados": periodo.reportes_sobre_facturados if periodo else 0,
            "monto_plan": int(periodo.monto_plan) if periodo else 0,
            "monto_sobre_facturado": int(periodo.monto_sobre_facturado) if periodo else 0,
            "monto_total": int(periodo.monto_total) if periodo else 0,
            "monto_pagado": int(periodo.monto_pagado) if periodo else 0,
            "saldo_pendiente": int(periodo.saldo_pendiente) if periodo else 0,
            "estado_pago": periodo.estado if periodo else "—",
            "consultas_habilitadas": emp.consultas_habilitadas,
            "activo": emp.activo,
        })

    return success(data=data)


@facturacion_bp.route("/admin/empresas/<int:empresa_id>/asignar-plan", methods=["POST"])
@propietario_required
def asignar_plan(empresa_id):
    """Asignar o cambiar el plan de una empresa."""
    current_user = get_current_user()
    Empresa.query.get_or_404(empresa_id)
    data = request.get_json(silent=True) or {}

    plan_id = data.get("plan_id")
    if not plan_id:
        return error("plan_id requerido", 400)

    plan = Plan.query.get_or_404(plan_id)

    # Finalizar plan anterior si existe
    plan_anterior = EmpresaPlan.query.filter_by(empresa_id=empresa_id, estado="activo").first()
    if plan_anterior:
        plan_anterior.estado = "finalizado"
        plan_anterior.fecha_fin = datetime.now(timezone.utc)
        # Guardar en historial
        historial = HistorialEmpresaPlan(
            empresa_id=empresa_id,
            plan_id=plan_anterior.plan_id,
            plan_nombre=plan_anterior.plan.nombre if plan_anterior.plan else "",
            precio_plan=plan_anterior.precio_plan_contratado,
            cantidad_reportes=plan_anterior.cantidad_reportes_incluidos,
            precio_sobre_fact=plan_anterior.precio_reporte_sobre_facturado,
            fecha_desde=plan_anterior.fecha_inicio,
            fecha_hasta=datetime.now(timezone.utc),
            cambiado_por=current_user.id,
        )
        db.session.add(historial)

    # Crear nueva asignación
    nuevo = EmpresaPlan(
        empresa_id=empresa_id,
        plan_id=plan_id,
        precio_plan_contratado=plan.precio_plan,
        cantidad_reportes_incluidos=plan.cantidad_reportes_incluidos,
        precio_reporte_sobre_facturado=plan.precio_reporte_sobre_facturado,
    )
    db.session.add(nuevo)
    db.session.commit()

    auditar("FACTURACION", "ASIGNACION_PLAN", usuario=current_user, modulo="Facturacion",
            entidad="EmpresaPlan", registro_id=nuevo.id, resultado="EXITO",
            info={"empresa_id": empresa_id, "plan_id": plan_id, "plan_nombre": plan.nombre})
    return success(data=nuevo.to_dict(), message="Plan asignado correctamente")


@facturacion_bp.route("/admin/empresas/<int:empresa_id>/bloquear", methods=["POST"])
@propietario_required
def bloquear_empresa(empresa_id):
    """Bloquear consultas de una empresa."""
    data = request.get_json(silent=True) or {}
    empresa = Empresa.query.get_or_404(empresa_id)
    motivo = data.get("motivo", "BLOQUEADO_MANUAL")

    empresa.consultas_habilitadas = False
    empresa.motivo_bloqueo = motivo
    empresa.fecha_bloqueo = datetime.now(timezone.utc)
    db.session.commit()

    auditar("FACTURACION", "BLOQUEO_EMPRESA", usuario=get_current_user(), modulo="Facturacion",
            entidad="Empresa", registro_id=empresa.id, resultado="EXITO",
            info={"empresa_nombre": empresa.nombre, "motivo": motivo})
    return success(message=f"Consultas bloqueadas para {empresa.nombre}")


@facturacion_bp.route("/admin/empresas/<int:empresa_id>/desbloquear", methods=["POST"])
@propietario_required
def desbloquear_empresa(empresa_id):
    """Desbloquear consultas de una empresa."""
    empresa = Empresa.query.get_or_404(empresa_id)
    empresa.consultas_habilitadas = True
    empresa.motivo_bloqueo = None
    empresa.fecha_desbloqueo = datetime.now(timezone.utc)
    db.session.commit()

    auditar("FACTURACION", "DESBLOQUEO_EMPRESA", usuario=get_current_user(), modulo="Facturacion",
            entidad="Empresa", registro_id=empresa.id, resultado="EXITO",
            info={"empresa_nombre": empresa.nombre})
    return success(message=f"Consultas desbloqueadas para {empresa.nombre}")
