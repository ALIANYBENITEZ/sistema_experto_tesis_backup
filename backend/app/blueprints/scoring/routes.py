from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Client
from app.models.scoring import (
    MotorReglas, Regla, HistorialCrediticio,
    EvaluacionRiesgo, ResultadoDetalle, DetalleOperacion,
)
from app.utils.decorators import admin_required, get_current_user
from app.utils.responses import success, error
from .engine import ejecutar_motor, generar_recomendacion
from . import scoring_bp


# ══════════════════════════════════════════════════════════════
#  MOTOR DE REGLAS — CRUD (solo administrador)
# ══════════════════════════════════════════════════════════════

@scoring_bp.route("/motores", methods=["GET"])
@jwt_required()
def list_motores():
    current_user = get_current_user()
    if current_user.is_propietario():
        motores = MotorReglas.query.order_by(MotorReglas.id).all()
    else:
        motores = MotorReglas.query.filter_by(id_empresa_motor=current_user.id_empresa).order_by(MotorReglas.id).all()
    return success(data=[m.to_dict() for m in motores])


@scoring_bp.route("/motores/<int:motor_id>", methods=["GET"])
@jwt_required()
def get_motor(motor_id):
    motor = MotorReglas.query.get_or_404(motor_id)
    return success(data=motor.to_dict(include_reglas=True))


@scoring_bp.route("/motores", methods=["POST"])
@admin_required
def create_motor():
    from app.utils.decorators import get_current_user
    current_user = get_current_user()
    # Solo propietario puede crear motores
    if not current_user.is_propietario():
        return error("Solo el propietario puede crear motores de reglas", 403)

    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)
    if not data.get("nombre"):
        return error("El nombre es requerido", 400)

    user_id = int(get_jwt_identity())
    motor = MotorReglas(
        nombre           = data["nombre"].strip(),
        version          = data.get("version", "1.0").strip(),
        descripcion      = data.get("descripcion", "").strip() or None,
        id_empresa_motor = int(data.get("id_empresa_motor", 0)) or 0,
        creado_por       = user_id,
    )
    db.session.add(motor)
    db.session.commit()
    return success(data=motor.to_dict(), message="Motor creado", status=201)


@scoring_bp.route("/motores/<int:motor_id>", methods=["PUT"])
@admin_required
def update_motor(motor_id):
    from app.utils.decorators import get_current_user
    current_user = get_current_user()
    if not current_user.is_propietario():
        return error("Solo el propietario puede editar motores de reglas", 403)

    motor = MotorReglas.query.get_or_404(motor_id)
    data  = request.get_json(silent=True) or {}

    if "nombre"      in data: motor.nombre      = data["nombre"].strip()
    if "version"     in data: motor.version     = data["version"].strip()
    if "descripcion" in data: motor.descripcion = data["descripcion"].strip() or None
    if "activo"      in data: motor.activo      = bool(data["activo"])
    if "id_empresa_motor" in data: motor.id_empresa_motor = int(data["id_empresa_motor"]) or 0

    db.session.commit()
    return success(data=motor.to_dict(), message="Motor actualizado")


@scoring_bp.route("/motores/<int:motor_id>/toggle", methods=["PATCH"])
@admin_required
def toggle_motor(motor_id):
    motor = MotorReglas.query.get_or_404(motor_id)
    motor.activo = not motor.activo
    db.session.commit()
    return success(data=motor.to_dict(),
                   message=f"Motor {'activado' if motor.activo else 'desactivado'}")


# ══════════════════════════════════════════════════════════════
#  REGLAS — CRUD dentro de un motor
# ══════════════════════════════════════════════════════════════

@scoring_bp.route("/motores/<int:motor_id>/reglas", methods=["GET"])
@jwt_required()
def list_reglas(motor_id):
    MotorReglas.query.get_or_404(motor_id)
    reglas = Regla.query.filter_by(motor_id=motor_id).order_by(Regla.orden).all()
    return success(data=[r.to_dict() for r in reglas])


@scoring_bp.route("/motores/<int:motor_id>/reglas", methods=["POST"])
@admin_required
def create_regla(motor_id):
    from app.utils.decorators import get_current_user
    current_user = get_current_user()
    if not current_user.is_propietario():
        return error("Solo el propietario puede crear reglas", 403)

    MotorReglas.query.get_or_404(motor_id)
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    required = ["nombre", "parametro", "operador", "valor_referencia", "peso_puntos"]
    missing  = [f for f in required if data.get(f) is None]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    if data["operador"] not in Regla.OPERADORES:
        return error(f"Operador inválido. Use: {', '.join(Regla.OPERADORES)}", 400)

    try:
        peso = float(data["peso_puntos"])
        if peso <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return error("peso_puntos debe ser un número positivo", 400)

    # Detectar tipo_valor automáticamente si no se envía
    tipo_valor = data.get("tipo_valor", "numerico")
    for param, _, tipo in Regla.PARAMETROS:
        if param == data["parametro"]:
            tipo_valor = tipo
            break

    regla = Regla(
        motor_id         = motor_id,
        nombre           = data["nombre"].strip(),
        descripcion      = data.get("descripcion", "").strip() or None,
        parametro        = data["parametro"],
        operador         = data["operador"],
        valor_referencia = str(data["valor_referencia"]).strip(),
        tipo_valor       = tipo_valor,
        peso_puntos      = peso,
        es_determinante  = bool(data.get("es_determinante", False)),
        activo           = bool(data.get("activo", True)),
        orden            = int(data.get("orden", 0)),
    )
    db.session.add(regla)
    db.session.commit()
    return success(data=regla.to_dict(), message="Regla creada", status=201)


@scoring_bp.route("/reglas/<int:regla_id>", methods=["PUT"])
@admin_required
def update_regla(regla_id):
    regla = Regla.query.get_or_404(regla_id)
    data  = request.get_json(silent=True) or {}

    fields = ["nombre", "descripcion", "parametro", "operador",
              "valor_referencia", "tipo_valor", "es_determinante", "activo", "orden"]
    for f in fields:
        if f in data:
            setattr(regla, f, data[f])

    if "peso_puntos" in data:
        try:
            regla.peso_puntos = float(data["peso_puntos"])
        except (ValueError, TypeError):
            return error("peso_puntos inválido", 400)

    db.session.commit()
    return success(data=regla.to_dict(), message="Regla actualizada")


@scoring_bp.route("/reglas/<int:regla_id>/toggle", methods=["PATCH"])
@admin_required
def toggle_regla(regla_id):
    regla = Regla.query.get_or_404(regla_id)
    regla.activo = not regla.activo
    db.session.commit()
    return success(data=regla.to_dict(),
                   message=f"Regla {'activada' if regla.activo else 'desactivada'}")


@scoring_bp.route("/reglas/<int:regla_id>", methods=["DELETE"])
@admin_required
def delete_regla(regla_id):
    regla = Regla.query.get_or_404(regla_id)
    db.session.delete(regla)
    db.session.commit()
    return success(message="Regla eliminada")


# ══════════════════════════════════════════════════════════════
#  HISTORIAL CREDITICIO
# ══════════════════════════════════════════════════════════════

@scoring_bp.route("/historial/<int:cliente_id>", methods=["GET"])
@jwt_required()
def get_historial(cliente_id):
    Client.query.get_or_404(cliente_id)
    historial = HistorialCrediticio.query.filter_by(cliente_id=cliente_id).first()
    if not historial:
        return success(data=None)
    return success(data=historial.to_dict())


@scoring_bp.route("/historial/<int:cliente_id>", methods=["PUT"])
@jwt_required()
def upsert_historial(cliente_id):
    Client.query.get_or_404(cliente_id)
    data = request.get_json(silent=True) or {}

    historial = HistorialCrediticio.query.filter_by(cliente_id=cliente_id).first()
    if not historial:
        historial = HistorialCrediticio(cliente_id=cliente_id)
        db.session.add(historial)

    campos = [
        "fuente_externa", "score_externo", "cantidad_atrasos",
        "deuda_total_sistema", "historial_pagos", "en_lista_negra",
        "nivel_endeudamiento", "meses_empleo_actual", "tipo_empleo",
        "referencias_personales",
    ]
    for campo in campos:
        if campo in data:
            setattr(historial, campo, data[campo])

    db.session.commit()
    return success(data=historial.to_dict(), message="Historial actualizado")


# ══════════════════════════════════════════════════════════════
#  EVALUACIÓN DE RIESGO — motor de inferencia
# ══════════════════════════════════════════════════════════════

@scoring_bp.route("/evaluar", methods=["POST"])
@jwt_required()
def evaluar_cliente():
    """
    Ejecuta el motor de reglas sobre un cliente.

    Body:
    {
        "cliente_id":    int,
        "motor_id":      int,
        "hechos": {
            "ingresos_mensuales": 5000000,
            "edad": 35,
            "nivel_endeudamiento": 25.5,
            ...
        },
        "observaciones": "texto opcional"
    }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    cliente_id = data.get("cliente_id")
    motor_id   = data.get("motor_id")
    hechos     = data.get("hechos", {})

    if not cliente_id:
        return error("cliente_id es requerido", 400)
    if not motor_id:
        return error("motor_id es requerido", 400)
    if not hechos:
        return error("Se requieren los hechos del cliente para evaluar", 400)

    cliente = Client.query.get(cliente_id)
    if not cliente:
        return error("Cliente no encontrado", 404)

    motor = MotorReglas.query.get(motor_id)
    if not motor:
        return error("Motor de reglas no encontrado", 404)
    if not motor.activo:
        return error("El motor de reglas no está activo", 400)

    # Enriquecer hechos con datos del cliente y su historial
    historial = HistorialCrediticio.query.filter_by(cliente_id=cliente_id).first()
    if historial:
        hist_dict = historial.to_dict()
        for k, v in hist_dict.items():
            if k not in hechos and v is not None:
                hechos[k] = v

    # Agregar edad del cliente si tiene fecha de nacimiento
    if "edad" not in hechos and cliente.fecha_nacimiento:
        from datetime import date
        hoy  = date.today()
        fnac = cliente.fecha_nacimiento
        edad = hoy.year - fnac.year - ((hoy.month, hoy.day) < (fnac.month, fnac.day))
        hechos["edad"] = edad

    # ── Ejecutar el motor de inferencia ──────────────────────
    resultado = ejecutar_motor(motor, hechos)

    # Guardar evaluación
    from app.utils.decorators import get_current_user as _get_user
    current_user = _get_user()

    evaluacion = EvaluacionRiesgo(
        cliente_id       = cliente_id,
        motor_id         = motor_id,
        usuario_id       = user_id,
        score_final      = resultado["score_final"],
        score_maximo     = resultado["score_maximo"],
        categoria_riesgo = resultado["categoria_riesgo"],
        observaciones    = data.get("observaciones", ""),
        regla_determinante_id = resultado["rechazado_por_regla"],
        id_empresa       = current_user.id_empresa or 0,
    )
    db.session.add(evaluacion)
    db.session.flush()

    # Guardar detalle por regla
    for det in resultado["detalles"]:
        detalle = ResultadoDetalle(
            evaluacion_id    = evaluacion.id,
            regla_id         = det["regla_id"],
            cumplido         = det["cumplido"],
            valor_evaluado   = det["valor_evaluado"],
            puntos_obtenidos = det["puntos_obtenidos"],
        )
        db.session.add(detalle)

    # Guardar detalle de operación inmobiliaria (si se proporcionó)
    operacion_data = data.get("operacion")
    if operacion_data and operacion_data.get("tipo_propiedad"):
        operacion = DetalleOperacion(
            evaluacion_id    = evaluacion.id,
            tipo_propiedad   = operacion_data["tipo_propiedad"],
            valor_propiedad  = float(operacion_data.get("valor_propiedad", 0)),
            monto_solicitado = float(operacion_data.get("monto_solicitado", 0)),
            plazo_meses      = int(operacion_data.get("plazo_meses", 0)),
            ubicacion        = operacion_data.get("ubicacion", "").strip() or None,
            destino          = operacion_data.get("destino", "").strip() or None,
        )
        db.session.add(operacion)

    db.session.commit()

    # Respuesta enriquecida
    resp = evaluacion.to_dict(include_detalles=True)
    resp["porcentaje"]       = resultado["porcentaje"]
    resp["cliente_nombre"]   = f"{cliente.nombre} {cliente.apellido or ''}".strip()
    resp["motor_nombre"]     = motor.nombre

    # Generar recomendación automatizada
    regla_det_nombre = None
    if resultado["rechazado_por_regla"]:
        regla_det = Regla.query.get(resultado["rechazado_por_regla"])
        if regla_det:
            regla_det_nombre = regla_det.nombre
    resp["recomendacion"] = generar_recomendacion(
        resultado["categoria_riesgo"],
        resultado["porcentaje"],
        regla_det_nombre,
    )

    return success(data=resp, message="Evaluación completada", status=201)


@scoring_bp.route("/evaluaciones", methods=["GET"])
@jwt_required()
def list_evaluaciones():
    current_user = get_current_user()
    page       = request.args.get("page", 1, type=int)
    per_page   = request.args.get("per_page", 20, type=int)
    cliente_id = request.args.get("cliente_id", type=int)
    categoria  = request.args.get("categoria")

    query = EvaluacionRiesgo.query

    # Filtrar por empresa del usuario
    if not current_user.is_propietario():
        query = query.filter_by(id_empresa=current_user.id_empresa)

    if cliente_id: query = query.filter_by(cliente_id=cliente_id)
    if categoria:  query = query.filter_by(categoria_riesgo=categoria)
    query = query.order_by(EvaluacionRiesgo.fecha_analisis.desc())

    pag = query.paginate(page=page, per_page=per_page, error_out=False)
    items = []
    for ev in pag.items:
        d = ev.to_dict()
        c = Client.query.get(ev.cliente_id)
        if c:
            d["cliente_nombre"] = f"{c.nombre} {c.apellido or ''}".strip()
            d["num_doc"]        = c.num_doc
        items.append(d)

    return success(data={
        "items":    items,
        "total":    pag.total,
        "page":     pag.page,
        "pages":    pag.pages,
        "per_page": pag.per_page,
    })


@scoring_bp.route("/evaluaciones/<int:eval_id>", methods=["GET"])
@jwt_required()
def get_evaluacion(eval_id):
    ev = EvaluacionRiesgo.query.get_or_404(eval_id)
    data = ev.to_dict(include_detalles=True)
    c = Client.query.get(ev.cliente_id)
    if c:
        data["cliente"] = {
            "nombre":   c.nombre,
            "apellido": c.apellido,
            "num_doc":  c.num_doc,
            "email":    c.email,
        }
    data["motor_nombre"] = ev.motor.nombre if ev.motor else None

    # Generar recomendación automatizada
    porcentaje = 0
    if ev.score_maximo and float(ev.score_maximo) > 0:
        porcentaje = float(ev.score_final) / float(ev.score_maximo) * 100
    regla_det_nombre = None
    if ev.regla_determinante_id:
        regla_det = Regla.query.get(ev.regla_determinante_id)
        if regla_det:
            regla_det_nombre = regla_det.nombre
    data["recomendacion"] = generar_recomendacion(
        ev.categoria_riesgo, porcentaje, regla_det_nombre
    )

    return success(data=data)


@scoring_bp.route("/parametros", methods=["GET"])
@jwt_required()
def get_parametros():
    """Devuelve la lista de parámetros disponibles para configurar reglas."""
    params = [
        {"valor": p, "label": l, "tipo": t}
        for p, l, t in Regla.PARAMETROS
    ]
    return success(data={"parametros": params, "operadores": Regla.OPERADORES})
