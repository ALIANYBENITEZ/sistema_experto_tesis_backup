"""
Servicio de contabilización de consumo de reportes.
Se ejecuta transaccionalmente al generar una evaluación.
"""
from datetime import datetime, timezone
from calendar import monthrange
from app.extensions import db
from app.models.facturacion import EmpresaPlan, PeriodoFacturacion, ConsumoReporte
from app.models.empresa import Empresa


class ConsultasBloqueadasError(Exception):
    pass


class SinPlanError(Exception):
    pass


def verificar_habilitacion(empresa_id: int):
    """Verifica que la empresa tenga consultas habilitadas."""
    empresa = Empresa.query.get(empresa_id)
    if not empresa:
        raise Exception("Empresa no encontrada")
    if not empresa.activo:
        raise ConsultasBloqueadasError("La empresa no está activa.")
    if hasattr(empresa, 'consultas_habilitadas') and not empresa.consultas_habilitadas:
        motivo = getattr(empresa, 'motivo_bloqueo', '') or 'falta de pago'
        raise ConsultasBloqueadasError(
            f"Las consultas de esta empresa se encuentran bloqueadas por {motivo}. "
            "Regularice su saldo para continuar."
        )


def obtener_periodo_actual(empresa_id: int) -> PeriodoFacturacion:
    """Obtiene o crea el período de facturación del mes actual."""
    ahora = datetime.now(timezone.utc)
    anio = ahora.year
    mes = ahora.month

    periodo = PeriodoFacturacion.query.filter_by(
        empresa_id=empresa_id, anio=anio, mes=mes
    ).first()

    if periodo:
        return periodo

    # Crear período nuevo
    plan_vigente = EmpresaPlan.query.filter_by(
        empresa_id=empresa_id, estado="activo"
    ).first()

    if not plan_vigente:
        raise SinPlanError("La empresa no tiene un plan asignado. Contacte al administrador del sistema.")

    _, ultimo_dia = monthrange(anio, mes)
    fecha_inicio = datetime(anio, mes, 1, tzinfo=timezone.utc)
    fecha_fin = datetime(anio, mes, ultimo_dia, 23, 59, 59, tzinfo=timezone.utc)

    periodo = PeriodoFacturacion(
        empresa_id=empresa_id,
        empresa_plan_id=plan_vigente.id,
        anio=anio,
        mes=mes,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        cantidad_reportes_incluidos=plan_vigente.cantidad_reportes_incluidos,
        monto_plan=plan_vigente.precio_plan_contratado,
        monto_total=plan_vigente.precio_plan_contratado,
        saldo_pendiente=plan_vigente.precio_plan_contratado,
    )
    db.session.add(periodo)
    db.session.flush()
    return periodo


def registrar_consumo_reporte(empresa_id: int, usuario_id: int, evaluacion_id: int):
    """
    Registra el consumo de un reporte. Llamar dentro de la misma transacción
    que genera la evaluación.

    Returns:
        dict con info del consumo registrado
    """
    # 1. Verificar habilitación
    verificar_habilitacion(empresa_id)

    # 2. Obtener período actual
    periodo = obtener_periodo_actual(empresa_id)

    # 3. Verificar duplicado
    existente = ConsumoReporte.query.filter_by(
        evaluacion_id=evaluacion_id, empresa_id=empresa_id
    ).first()
    if existente:
        return {"tipo": existente.tipo_consumo, "duplicado": True}

    # 4. Obtener plan vigente para precios
    plan_vigente = EmpresaPlan.query.get(periodo.empresa_plan_id)

    # 5. Determinar si es incluido o sobre facturado
    if periodo.reportes_consumidos < periodo.cantidad_reportes_incluidos:
        tipo = "INCLUIDO"
        precio = int(plan_vigente.precio_plan_contratado) // plan_vigente.cantidad_reportes_incluidos
    else:
        tipo = "SOBRE_FACTURADO"
        precio = int(plan_vigente.precio_reporte_sobre_facturado)

    # 6. Registrar consumo
    consumo = ConsumoReporte(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        evaluacion_id=evaluacion_id,
        periodo_facturacion_id=periodo.id,
        tipo_consumo=tipo,
        precio_unitario=precio,
    )
    db.session.add(consumo)

    # 7. Actualizar período
    periodo.reportes_consumidos += 1
    if tipo == "SOBRE_FACTURADO":
        periodo.reportes_sobre_facturados += 1
        periodo.monto_sobre_facturado = int(periodo.monto_sobre_facturado or 0) + precio
        periodo.monto_total = int(periodo.monto_plan or 0) + int(periodo.monto_sobre_facturado)
        periodo.saldo_pendiente = int(periodo.monto_total) - int(periodo.monto_pagado or 0)

    # No hacemos commit aquí — se hace en la transacción que llama a este servicio
    return {
        "tipo": tipo,
        "precio": precio,
        "reportes_consumidos": periodo.reportes_consumidos,
        "reportes_incluidos": periodo.cantidad_reportes_incluidos,
        "duplicado": False,
    }
