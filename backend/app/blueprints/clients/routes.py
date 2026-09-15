import re
from datetime import date
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Client, Document
from app.models.cliente_empresa import ClienteEmpresa
from app.models.location import Pais, Departamento, Ciudad
from app.utils.decorators import get_current_user
from app.utils.responses import success, error
from app.services.auditoria_service import registrar as auditar
from . import clients_bp

TIPOS_DOC_VALIDOS = ("CI", "RUC", "PAS")

# Edad mínima para registrar un cliente.
EDAD_MINIMA = 18

# El teléfono solo admite dígitos y símbolos habituales (+, espacio, guion,
# paréntesis). No se permiten letras.
_TELEFONO_RE = re.compile(r"^[0-9+\-\s()]+$")


def _calcular_edad(fecha_nac: date) -> int:
    """Edad en años cumplidos a la fecha de hoy."""
    hoy = date.today()
    return hoy.year - fecha_nac.year - (
        (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day)
    )


def _validar_fecha_nacimiento(valor: str):
    """
    Valida y parsea la fecha de nacimiento.
    Retorna (fecha, None) si es válida, o (None, mensaje_error) si no.
    Exige que el cliente sea mayor de edad (>= EDAD_MINIMA).
    """
    try:
        fecha_nac = date.fromisoformat(valor)
    except ValueError:
        return None, "fecha_nacimiento inválida. Use YYYY-MM-DD"

    if fecha_nac > date.today():
        return None, "La fecha de nacimiento no puede ser futura"

    if _calcular_edad(fecha_nac) < EDAD_MINIMA:
        return None, f"El cliente debe ser mayor de edad (mínimo {EDAD_MINIMA} años)"

    return fecha_nac, None


def _validar_telefono(valor: str):
    """
    Valida el teléfono: no se permiten letras.
    Retorna (telefono_limpio, None) si es válido, o (None, mensaje_error) si no.
    """
    telefono = (valor or "").strip()
    if not telefono:
        return None, None  # el teléfono es opcional
    if not _TELEFONO_RE.match(telefono):
        return None, "El teléfono solo puede contener números y los símbolos + - ( ) espacio"
    return telefono, None


@clients_bp.route("/", methods=["GET"])
@jwt_required()
def list_clients():
    current_user = get_current_user()
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search   = request.args.get("search", "").strip()
    num_doc  = request.args.get("num_doc", "").strip()
    nombre   = request.args.get("nombre", "").strip()
    apellido = request.args.get("apellido", "").strip()

    # Propietario ve todos, otros solo clientes vinculados a su empresa
    if current_user.is_propietario():
        query = Client.query
    else:
        # Subquery: IDs de clientes activos en la empresa del usuario
        subq = db.session.query(ClienteEmpresa.id_cliente).filter(
            ClienteEmpresa.id_empresa == current_user.id_empresa,
            ClienteEmpresa.estado == "activo"
        ).subquery()
        query = Client.query.filter(Client.id.in_(subq))

    # Búsqueda por campos individuales (AND)
    if num_doc:
        query = query.filter(Client.num_doc.ilike(f"%{num_doc}%"))
    if nombre:
        query = query.filter(Client.nombre.ilike(f"%{nombre}%"))
    if apellido:
        query = query.filter(Client.apellido.ilike(f"%{apellido}%"))

    # Búsqueda general (OR)
    if search and not (num_doc or nombre or apellido):
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Client.nombre.ilike(like),
                Client.apellido.ilike(like),
                Client.num_doc.ilike(like),
                Client.email.ilike(like),
            )
        )

    query = query.order_by(Client.creado_en.desc())
    pag   = query.paginate(page=page, per_page=per_page, error_out=False)

    return success(data={
        "items":    [c.to_dict() for c in pag.items],
        "total":    pag.total,
        "page":     pag.page,
        "pages":    pag.pages,
        "per_page": pag.per_page,
    })


@clients_bp.route("/<int:client_id>", methods=["GET"])
@jwt_required()
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    data   = client.to_dict()
    data["documentos"] = [d.to_dict() for d in client.documentos]
    return success(data=data)


@clients_bp.route("/", methods=["POST"])
@jwt_required()
def create_client():
    current_user = get_current_user()
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    required = ["tipo_doc", "num_doc", "nombre"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    if data["tipo_doc"] not in TIPOS_DOC_VALIDOS:
        return error(f"tipo_doc debe ser: {', '.join(TIPOS_DOC_VALIDOS)}", 400)

    # Validar teléfono (no permite letras)
    telefono, tel_err = _validar_telefono(data.get("telefono"))
    if tel_err:
        return error(tel_err, 400)

    # Verificar si el cliente ya existe por num_doc
    existing = Client.query.filter_by(num_doc=data["num_doc"]).first()

    fecha_nac = None
    if data.get("fecha_nacimiento"):
        fecha_nac, fn_err = _validar_fecha_nacimiento(data["fecha_nacimiento"])
        if fn_err:
            return error(fn_err, 400)

    if existing:
        # El cliente ya existe — vincularlo a la empresa correspondiente
        empresa_id = None
        if current_user.is_propietario():
            if data.get("id_empresa"):
                empresa_id = int(data["id_empresa"])
        else:
            empresa_id = current_user.id_empresa

        if empresa_id:
            ya_vinculado = ClienteEmpresa.query.filter_by(
                id_cliente=existing.id, id_empresa=empresa_id
            ).first()
            if ya_vinculado:
                if ya_vinculado.estado == "inactivo":
                    ya_vinculado.estado = "activo"
                    db.session.commit()
                    return success(data=existing.to_dict(), message="Cliente reactivado en la empresa")
                return error("El cliente ya está registrado en esta empresa", 409)
            # Vincular
            ce = ClienteEmpresa(id_cliente=existing.id, id_empresa=empresa_id)
            db.session.add(ce)
            db.session.commit()
            auditar("CLIENTES", "VINCULACION_CLIENTE", usuario=current_user, modulo="Clientes",
                    entidad="Cliente", registro_id=existing.id, resultado="EXITO",
                    info={"num_doc": existing.num_doc, "id_empresa": empresa_id})
            return success(data=existing.to_dict(), message="Cliente vinculado a la empresa", status=201)
        else:
            return error("Ya existe un cliente con ese número de documento", 409)

    # Crear cliente nuevo
    client = Client(
        tipo_doc         = data["tipo_doc"],
        num_doc          = data["num_doc"].strip(),
        nombre           = data["nombre"].strip(),
        apellido         = data.get("apellido", "").strip(),
        email            = data.get("email", "").strip() or None,
        telefono         = telefono,
        direccion        = data.get("direccion", "").strip() or None,
        fecha_nacimiento = fecha_nac,
        nacionalidad     = data.get("nacionalidad") or None,
        id_ciudad        = int(data["id_ciudad"]) if data.get("id_ciudad") else None,
        creado_por       = current_user.id,
    )
    db.session.add(client)
    db.session.flush()

    # Vincular a empresa
    empresa_id = None
    if current_user.is_propietario():
        # Propietario puede indicar empresa en el body
        if data.get("id_empresa"):
            empresa_id = int(data["id_empresa"])
    else:
        empresa_id = current_user.id_empresa

    if empresa_id:
        ce = ClienteEmpresa(id_cliente=client.id, id_empresa=empresa_id)
        db.session.add(ce)

    db.session.commit()
    auditar("CLIENTES", "REGISTRO_CLIENTE", usuario=current_user, modulo="Clientes",
            entidad="Cliente", registro_id=client.id, resultado="EXITO",
            info={"num_doc": client.num_doc, "nombre": f"{client.nombre} {client.apellido}".strip(),
                  "id_empresa": empresa_id})
    return success(data=client.to_dict(), message="Cliente registrado", status=201)


@clients_bp.route("/<int:client_id>", methods=["PUT"])
@jwt_required()
def update_client(client_id):
    current_user = get_current_user()
    client = Client.query.get_or_404(client_id)
    data   = request.get_json(silent=True) or {}

    # Snapshot de valores anteriores (campos auditables)
    _campos_aud = ("nombre", "apellido", "email", "telefono", "direccion", "nacionalidad", "id_ciudad")
    valores_ant = {c: getattr(client, c) for c in _campos_aud}

    # Validar teléfono si se envía (no permite letras)
    if "telefono" in data:
        telefono, tel_err = _validar_telefono(data.get("telefono"))
        if tel_err:
            return error(tel_err, 400)

    for field in ("nombre", "apellido", "email", "telefono", "direccion"):
        if field in data:
            setattr(client, field, (data[field] or "").strip() or None)

    if "fecha_nacimiento" in data and data["fecha_nacimiento"]:
        fecha_nac, fn_err = _validar_fecha_nacimiento(data["fecha_nacimiento"])
        if fn_err:
            return error(fn_err, 400)
        client.fecha_nacimiento = fecha_nac

    if "nacionalidad" in data:
        client.nacionalidad = data["nacionalidad"] or None
    if "id_ciudad" in data:
        client.id_ciudad = int(data["id_ciudad"]) if data["id_ciudad"] else None

    db.session.commit()

    # Solo registrar campos que cambiaron
    valores_nue = {c: getattr(client, c) for c in _campos_aud}
    ant_diff = {k: str(v) for k, v in valores_ant.items() if valores_ant[k] != valores_nue[k]}
    nue_diff = {k: str(valores_nue[k]) for k in ant_diff}
    if ant_diff:
        auditar("CLIENTES", "MODIFICACION_CLIENTE", usuario=current_user, modulo="Clientes",
                entidad="Cliente", registro_id=client.id, resultado="EXITO",
                valores_anteriores=ant_diff, valores_nuevos=nue_diff)

    return success(data=client.to_dict(), message="Cliente actualizado")


@clients_bp.route("/<int:client_id>", methods=["DELETE"])
@jwt_required()
def delete_client(client_id):
    """Desvincula (inactiva) al cliente de la empresa del usuario."""
    current_user = get_current_user()
    client = Client.query.get_or_404(client_id)

    if current_user.is_propietario():
        # Propietario: inactivar el cliente globalmente
        client.estado = "inactivo"
    else:
        # Usuario empresa: solo inactivar el vínculo con su empresa
        ce = ClienteEmpresa.query.filter_by(
            id_cliente=client_id, id_empresa=current_user.id_empresa
        ).first()
        if ce:
            ce.estado = "inactivo"
        else:
            return error("Cliente no vinculado a su empresa", 404)

    db.session.commit()
    auditar("CLIENTES", "BAJA_CLIENTE", usuario=current_user, modulo="Clientes",
            entidad="Cliente", registro_id=client.id, resultado="EXITO",
            info={"num_doc": client.num_doc,
                  "ambito": "global" if current_user.is_propietario() else f"empresa {current_user.id_empresa}"})
    return success(message="Cliente desactivado")


# ══════════════════════════════════════════════════════════════
#  UBICACIÓN — Países, Departamentos, Ciudades
# ══════════════════════════════════════════════════════════════

@clients_bp.route("/paises", methods=["GET"])
@jwt_required()
def list_paises():
    paises = Pais.query.order_by(Pais.nombre_pais).all()
    return success(data=[p.to_dict() for p in paises])


@clients_bp.route("/departamentos", methods=["GET"])
@jwt_required()
def list_departamentos():
    """Lista todos los departamentos (solo Paraguay)."""
    deptos = Departamento.query.order_by(Departamento.nombre_departamento).all()
    return success(data=[d.to_dict() for d in deptos])


@clients_bp.route("/departamentos/<int:depto_id>/ciudades", methods=["GET"])
@jwt_required()
def list_ciudades(depto_id):
    ciudades = Ciudad.query.filter_by(id_departamento=depto_id).order_by(Ciudad.nombre_ciudad).all()
    return success(data=[c.to_dict() for c in ciudades])
