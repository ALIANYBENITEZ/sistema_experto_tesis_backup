"""
API de Auditoría — Consulta de la bitácora de eventos del sistema.
Solo lectura. Acceso: propietario (todo) y administrador (su empresa).
"""
from datetime import datetime, timedelta
from flask import request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Empresa
from app.models.auditoria import Auditoria
from app.utils.decorators import get_current_user
from app.utils.responses import success, error
from . import auditoria_bp


# Catálogos para poblar los combos de filtro en el frontend
TIPOS_EVENTO = [
    "AUTENTICACION", "SEGURIDAD", "USUARIOS", "EMPRESAS",
    "CLIENTES", "EVALUACIONES", "FACTURACION",
]
RESULTADOS = ["EXITO", "FALLO"]


@auditoria_bp.route("/", methods=["GET"])
@jwt_required()
def list_auditoria():
    """
    Lista los eventos de auditoría con filtros y paginación.

    Query params:
      - page, per_page
      - fecha_from, fecha_to (YYYY-MM-DD)
      - usuario_id
      - tipo_evento
      - accion
      - modulo
      - resultado (EXITO/FALLO)
      - id_empresa (solo propietario)
      - search (texto libre sobre usuario_nombre, accion, entidad)
    """
    current_user = get_current_user()

    # Solo propietario y administrador pueden consultar
    if not current_user.is_admin():
        return error("No tiene permisos para consultar la auditoría", 403)

    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)

    query = Auditoria.query

    # ── Multi-tenant: admin de empresa solo ve su empresa ──
    if not current_user.is_propietario():
        query = query.filter(Auditoria.id_empresa == current_user.id_empresa)
    else:
        # Propietario puede filtrar por empresa opcionalmente
        id_empresa = request.args.get("id_empresa", type=int)
        if id_empresa is not None:
            query = query.filter(Auditoria.id_empresa == id_empresa)

    # ── Filtros ──
    fecha_from = request.args.get("fecha_from", "").strip()
    fecha_to   = request.args.get("fecha_to", "").strip()
    if fecha_from:
        try:
            query = query.filter(Auditoria.fecha >= datetime.fromisoformat(fecha_from))
        except ValueError:
            return error("fecha_from inválida. Use YYYY-MM-DD", 400)
    if fecha_to:
        try:
            # Incluir el día completo
            hasta = datetime.fromisoformat(fecha_to) + timedelta(days=1)
            query = query.filter(Auditoria.fecha < hasta)
        except ValueError:
            return error("fecha_to inválida. Use YYYY-MM-DD", 400)

    usuario_id = request.args.get("usuario_id", type=int)
    if usuario_id:
        query = query.filter(Auditoria.usuario_id == usuario_id)

    for campo, columna in (
        ("tipo_evento", Auditoria.tipo_evento),
        ("accion", Auditoria.accion),
        ("modulo", Auditoria.modulo),
        ("resultado", Auditoria.resultado),
    ):
        valor = request.args.get(campo, "").strip()
        if valor:
            query = query.filter(columna == valor)

    search = request.args.get("search", "").strip()
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Auditoria.usuario_nombre.ilike(like),
                Auditoria.accion.ilike(like),
                Auditoria.entidad.ilike(like),
            )
        )

    query = query.order_by(Auditoria.fecha.desc(), Auditoria.id.desc())
    pag   = query.paginate(page=page, per_page=per_page, error_out=False)

    # Enriquecer con nombre de empresa
    empresas = {e.id: e.nombre for e in Empresa.query.all()}
    items = []
    for a in pag.items:
        d = a.to_dict()
        if a.id_empresa == 0:
            d["empresa_nombre"] = "Sistema"
        else:
            d["empresa_nombre"] = empresas.get(a.id_empresa, "—")
        items.append(d)

    return success(data={
        "items":    items,
        "total":    pag.total,
        "page":     pag.page,
        "pages":    pag.pages,
        "per_page": pag.per_page,
    })


@auditoria_bp.route("/filtros", methods=["GET"])
@jwt_required()
def opciones_filtro():
    """Devuelve catálogos para poblar los combos de filtro del frontend."""
    current_user = get_current_user()
    if not current_user.is_admin():
        return error("No tiene permisos", 403)

    # Acciones y módulos distintos presentes en la bitácora (según alcance)
    query = db.session.query(Auditoria.accion).distinct()
    modulos_q = db.session.query(Auditoria.modulo).distinct()
    if not current_user.is_propietario():
        query = query.filter(Auditoria.id_empresa == current_user.id_empresa)
        modulos_q = modulos_q.filter(Auditoria.id_empresa == current_user.id_empresa)

    acciones = sorted([a[0] for a in query.all() if a[0]])
    modulos  = sorted([m[0] for m in modulos_q.all() if m[0]])

    data = {
        "tipos_evento": TIPOS_EVENTO,
        "resultados":   RESULTADOS,
        "acciones":     acciones,
        "modulos":      modulos,
    }

    # Propietario: incluir lista de empresas para filtrar
    if current_user.is_propietario():
        empresas = Empresa.query.order_by(Empresa.nombre).all()
        data["empresas"] = [{"id": 0, "nombre": "Sistema"}] + [
            {"id": e.id, "nombre": e.nombre} for e in empresas
        ]

    return success(data=data)
