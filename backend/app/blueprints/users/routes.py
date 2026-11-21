from flask import request
from app.extensions import db
from app.models import Empresa, User
from app.utils.decorators import admin_required, get_current_user
from app.utils.responses import success, error
from app.services.auditoria_service import registrar as auditar
from . import users_bp

# Gestión de usuarios (multi-empresa):
#  - Propietario: gestiona los usuarios de todas las empresas.
#  - Administrador: gestiona solo los usuarios de su propia empresa (id_empresa).
#  - Nadie puede modificar al propietario desde aquí ni cambiar su propio rol
#    o desactivarse a sí mismo.
ROLES_ASIGNABLES = (User.ROL_ADMIN, User.ROL_COMERCIAL)


def _puede_gestionar(actual: User, objetivo: User) -> bool:
    if objetivo.is_propietario() and not actual.is_propietario():
        return False
    if actual.is_propietario():
        return True
    return objetivo.id_empresa == actual.id_empresa


@users_bp.route("/", methods=["GET"])
@admin_required
def list_users():
    actual = get_current_user()
    query = User.query
    if not actual.is_propietario():
        query = query.filter_by(id_empresa=actual.id_empresa)
    users = query.order_by(User.id).all()
    return success(data=[u.to_dict() for u in users])


@users_bp.route("/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    actual = get_current_user()
    user = User.query.get_or_404(user_id)
    if not _puede_gestionar(actual, user):
        return error("No puede gestionar usuarios de otra empresa", 403)
    return success(data=user.to_dict())


@users_bp.route("/", methods=["POST"])
@admin_required
def create_user():
    actual = get_current_user()
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    required = ["nombre", "apellido", "email", "password", "rol"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    if data["rol"] not in ROLES_ASIGNABLES:
        return error("Rol inválido. Use 'administrador' o 'comercial'", 400)

    if User.query.filter_by(email=data["email"].strip().lower()).first():
        return error("El email ya está registrado", 409)

    # El administrador solo crea usuarios en su propia empresa.
    # El propietario puede indicar la empresa; si no la indica, se mantiene 0.
    if actual.is_propietario():
        try:
            id_empresa = int(data.get("id_empresa") or 0)
        except (TypeError, ValueError):
            return error("id_empresa inválido", 400)
        if id_empresa and not Empresa.query.get(id_empresa):
            return error("Empresa no encontrada", 404)
    else:
        id_empresa = actual.id_empresa

    user = User(
        nombre     = data["nombre"].strip(),
        apellido   = data["apellido"].strip(),
        email      = data["email"].strip().lower(),
        rol        = data["rol"],
        id_empresa = id_empresa,
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    auditar("USUARIOS", "CREACION_USUARIO", usuario=actual, modulo="Usuarios",
            entidad="Usuario", registro_id=user.id, resultado="EXITO",
            info={"email": user.email, "rol": user.rol, "id_empresa": id_empresa})
    return success(data=user.to_dict(), message="Usuario creado", status=201)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    actual = get_current_user()
    user = User.query.get_or_404(user_id)
    if not _puede_gestionar(actual, user):
        return error("No puede gestionar usuarios de otra empresa", 403)
    data = request.get_json(silent=True) or {}

    valores_ant = {"nombre": user.nombre, "apellido": user.apellido,
                   "email": user.email, "rol": user.rol}

    if "nombre" in data:
        user.nombre = data["nombre"].strip()
    if "apellido" in data:
        user.apellido = data["apellido"].strip()
    if "email" in data:
        new_email = data["email"].strip().lower()
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user_id:
            return error("El email ya está en uso", 409)
        user.email = new_email
    if "rol" in data and data["rol"] != user.rol:
        # El rol del propietario no se cambia desde aquí: dejaría la plataforma sin propietario.
        if user.is_propietario():
            return error("No se puede cambiar el rol del propietario", 400)
        if user.id == actual.id:
            return error("No puede cambiar su propio rol", 400)
        if data["rol"] not in ROLES_ASIGNABLES:
            return error("Rol inválido. Use 'administrador' o 'comercial'", 400)
        user.rol = data["rol"]
    cambio_password = bool(data.get("password"))
    if cambio_password:
        user.set_password(data["password"])

    db.session.commit()

    valores_nue = {"nombre": user.nombre, "apellido": user.apellido,
                   "email": user.email, "rol": user.rol}
    ant_diff = {k: str(v) for k, v in valores_ant.items() if valores_ant[k] != valores_nue[k]}
    nue_diff = {k: str(valores_nue[k]) for k in ant_diff}
    auditar("USUARIOS", "MODIFICACION_USUARIO", usuario=actual, modulo="Usuarios",
            entidad="Usuario", registro_id=user.id, resultado="EXITO",
            info={"cambio_password": True} if cambio_password else None,
            valores_anteriores=ant_diff or None, valores_nuevos=nue_diff or None)
    return success(data=user.to_dict(), message="Usuario actualizado")


@users_bp.route("/<int:user_id>/toggle", methods=["PATCH"])
@admin_required
def toggle_user(user_id):
    actual = get_current_user()
    user = User.query.get_or_404(user_id)
    if not _puede_gestionar(actual, user):
        return error("No puede gestionar usuarios de otra empresa", 403)
    if user.id == actual.id:
        return error("No puede desactivar su propio usuario", 400)
    user.activo = not user.activo
    db.session.commit()
    auditar("USUARIOS", "ACTIVAR_USUARIO" if user.activo else "DESACTIVAR_USUARIO",
            usuario=actual, modulo="Usuarios", entidad="Usuario",
            registro_id=user.id, resultado="EXITO", info={"email": user.email})
    estado = "activado" if user.activo else "desactivado"
    return success(data=user.to_dict(), message=f"Usuario {estado}")
