from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Evaluation, EvaluationDetail, Criterion, Client
from app.utils.decorators import admin_required
from app.utils.responses import success, error
from .engine import calcular_puntaje
from . import evaluation_bp


# ── Criterios ─────────────────────────────────────────────────────────────────

@evaluation_bp.route("/criteria", methods=["GET"])
@jwt_required()
def list_criteria():
    criteria = Criterion.query.order_by(Criterion.id).all()
    return success(data=[c.to_dict() for c in criteria])


@evaluation_bp.route("/criteria", methods=["POST"])
@admin_required
def create_criterion():
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    required = ["nombre", "peso"]
    missing  = [f for f in required if data.get(f) is None]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    try:
        peso = float(data["peso"])
        if not (0 < peso <= 100):
            raise ValueError
    except (ValueError, TypeError):
        return error("El peso debe ser un número entre 0 y 100", 400)

    criterio = Criterion(
        nombre      = data["nombre"].strip(),
        descripcion = data.get("descripcion", "").strip() or None,
        peso        = peso,
    )
    db.session.add(criterio)
    db.session.commit()
    return success(data=criterio.to_dict(), message="Criterio creado", status=201)


@evaluation_bp.route("/criteria/<int:criterion_id>", methods=["PUT"])
@admin_required
def update_criterion(criterion_id):
    criterio = Criterion.query.get_or_404(criterion_id)
    data     = request.get_json(silent=True) or {}

    if "nombre" in data:
        criterio.nombre = data["nombre"].strip()
    if "descripcion" in data:
        criterio.descripcion = data["descripcion"].strip() or None
    if "peso" in data:
        try:
            peso = float(data["peso"])
            if not (0 < peso <= 100):
                raise ValueError
            criterio.peso = peso
        except (ValueError, TypeError):
            return error("El peso debe ser un número entre 0 y 100", 400)
    if "activo" in data:
        criterio.activo = bool(data["activo"])

    db.session.commit()
    return success(data=criterio.to_dict(), message="Criterio actualizado")


# ── Evaluaciones ──────────────────────────────────────────────────────────────

@evaluation_bp.route("/", methods=["GET"])
@jwt_required()
def list_evaluations():
    page       = request.args.get("page", 1, type=int)
    per_page   = request.args.get("per_page", 20, type=int)
    cliente_id = request.args.get("cliente_id", type=int)
    resultado  = request.args.get("resultado")

    query = Evaluation.query
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    if resultado:
        query = query.filter_by(resultado=resultado)

    query = query.order_by(Evaluation.fecha.desc())
    pag   = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        "items":    [e.to_dict() for e in pag.items],
        "total":    pag.total,
        "page":     pag.page,
        "pages":    pag.pages,
        "per_page": pag.per_page,
    })


@evaluation_bp.route("/<int:eval_id>", methods=["GET"])
@jwt_required()
def get_evaluation(eval_id):
    ev   = Evaluation.query.get_or_404(eval_id)
    data = ev.to_dict(include_detalles=True)

    # Enriquecer con datos del cliente
    client = Client.query.get(ev.cliente_id)
    if client:
        data["cliente"] = {
            "nombre":  client.nombre,
            "apellido": client.apellido,
            "num_doc": client.num_doc,
        }
    return success(data=data)


@evaluation_bp.route("/", methods=["POST"])
@jwt_required()
def create_evaluation():
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    cliente_id = data.get("cliente_id")
    detalles   = data.get("detalles", [])

    if not cliente_id:
        return error("cliente_id es requerido", 400)
    if not detalles:
        return error("Debe proporcionar al menos un criterio evaluado", 400)

    if not Client.query.get(cliente_id):
        return error("Cliente no encontrado", 404)

    # Calcular puntaje con el motor
    puntaje_total, resultado = calcular_puntaje(detalles)

    evaluacion = Evaluation(
        cliente_id    = cliente_id,
        evaluador_id  = user_id,
        puntaje_total = puntaje_total,
        resultado     = resultado,
        observaciones = data.get("observaciones", ""),
        estado        = "completado",
    )
    db.session.add(evaluacion)
    db.session.flush()  # Obtener el ID antes del commit

    for det in detalles:
        cid   = det.get("criterio_id")
        valor = float(det.get("valor", 0))
        if Criterion.query.get(cid):
            detalle = EvaluationDetail(
                evaluacion_id = evaluacion.id,
                criterio_id   = cid,
                valor         = max(0.0, min(100.0, valor)),
                comentario    = det.get("comentario", ""),
            )
            db.session.add(detalle)

    db.session.commit()
    return success(
        data=evaluacion.to_dict(include_detalles=True),
        message="Evaluación completada",
        status=201,
    )


@evaluation_bp.route("/<int:eval_id>", methods=["PUT"])
@jwt_required()
def update_evaluation(eval_id):
    evaluacion = Evaluation.query.get_or_404(eval_id)
    data       = request.get_json(silent=True) or {}

    if "observaciones" in data:
        evaluacion.observaciones = data["observaciones"]
    if "estado" in data:
        evaluacion.estado = data["estado"]

    db.session.commit()
    return success(data=evaluacion.to_dict(), message="Evaluación actualizada")
