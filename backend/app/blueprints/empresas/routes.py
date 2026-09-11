from flask import request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Empresa, User
from app.utils.decorators import propietario_required, get_current_user
from app.utils.responses import success, error
from app.services.auditoria_service import registrar as auditar
from . import empresas_bp


@empresas_bp.route("/", methods=["GET"])
@propietario_required
def list_empresas():
    empresas = Empresa.query.order_by(Empresa.nombre).all()
    return success(data=[e.to_dict() for e in empresas])


@empresas_bp.route("/<int:empresa_id>", methods=["GET"])
@propietario_required
def get_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    data = empresa.to_dict()
    # Incluir usuarios de la empresa
    usuarios = User.query.filter_by(id_empresa=empresa_id).order_by(User.nombre).all()
    data["usuarios"] = [u.to_dict() for u in usuarios]
    return success(data=data)


@empresas_bp.route("/", methods=["POST"])
@propietario_required
def create_empresa():
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)
    if not data.get("nombre"):
        return error("El nombre es requerido", 400)

    if data.get("ruc") and Empresa.query.filter_by(ruc=data["ruc"]).first():
        return error("Ya existe una empresa con ese RUC", 409)

    empresa = Empresa(
        nombre    = data["nombre"].strip(),
        ruc       = data.get("ruc", "").strip() or None,
        direccion = data.get("direccion", "").strip() or None,
        telefono  = data.get("telefono", "").strip() or None,
        email     = data.get("email", "").strip() or None,
    )
    db.session.add(empresa)
    db.session.commit()
    auditar("EMPRESAS", "REGISTRO_EMPRESA", usuario=get_current_user(), modulo="Empresas",
            entidad="Empresa", registro_id=empresa.id, resultado="EXITO",
            info={"nombre": empresa.nombre, "ruc": empresa.ruc})
    return success(data=empresa.to_dict(), message="Empresa registrada", status=201)


@empresas_bp.route("/<int:empresa_id>", methods=["PUT"])
@propietario_required
def update_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    data = request.get_json(silent=True) or {}

    for field in ("nombre", "ruc", "direccion", "telefono", "email"):
        if field in data:
            setattr(empresa, field, data[field].strip() or None)

    if "activo" in data:
        empresa.activo = bool(data["activo"])

    db.session.commit()
    auditar("EMPRESAS", "MODIFICACION_EMPRESA", usuario=get_current_user(), modulo="Empresas",
            entidad="Empresa", registro_id=empresa.id, resultado="EXITO",
            info={"nombre": empresa.nombre})
    return success(data=empresa.to_dict(), message="Empresa actualizada")


@empresas_bp.route("/<int:empresa_id>/toggle", methods=["PATCH"])
@propietario_required
def toggle_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    empresa.activo = not empresa.activo
    db.session.commit()
    auditar("EMPRESAS", "ACTIVAR_EMPRESA" if empresa.activo else "DESACTIVAR_EMPRESA",
            usuario=get_current_user(), modulo="Empresas", entidad="Empresa",
            registro_id=empresa.id, resultado="EXITO", info={"nombre": empresa.nombre})
    return success(data=empresa.to_dict(),
                   message=f"Empresa {'activada' if empresa.activo else 'desactivada'}")


# ══════════════════════════════════════════════════════════════
#  USUARIOS de una empresa
# ══════════════════════════════════════════════════════════════

@empresas_bp.route("/<int:empresa_id>/usuarios", methods=["GET"])
@propietario_required
def list_usuarios_empresa(empresa_id):
    Empresa.query.get_or_404(empresa_id)
    usuarios = User.query.filter_by(id_empresa=empresa_id).order_by(User.nombre).all()
    return success(data=[u.to_dict() for u in usuarios])


@empresas_bp.route("/<int:empresa_id>/usuarios", methods=["POST"])
@propietario_required
def create_usuario_empresa(empresa_id):
    Empresa.query.get_or_404(empresa_id)
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    required = ["nombre", "apellido", "email", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    if User.query.filter_by(email=data["email"].strip().lower()).first():
        return error("Ya existe un usuario con ese email", 409)

    rol = data.get("rol", "comercial")
    if rol not in ("administrador", "comercial"):
        return error("Rol debe ser 'administrador' o 'comercial'", 400)

    user = User(
        nombre     = data["nombre"].strip(),
        apellido   = data["apellido"].strip(),
        email      = data["email"].strip().lower(),
        rol        = rol,
        id_empresa = empresa_id,
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    auditar("USUARIOS", "CREACION_USUARIO", usuario=get_current_user(), modulo="Empresas",
            entidad="Usuario", registro_id=user.id, resultado="EXITO",
            info={"email": user.email, "rol": user.rol, "id_empresa": empresa_id})
    return success(data=user.to_dict(), message="Usuario creado", status=201)


@empresas_bp.route("/usuarios/<int:user_id>", methods=["PUT"])
@propietario_required
def update_usuario_empresa(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_propietario():
        return error("No se puede editar al propietario desde aquí", 403)

    data = request.get_json(silent=True) or {}

    valores_ant = {"nombre": user.nombre, "apellido": user.apellido,
                   "rol": user.rol, "activo": user.activo}
    cambio_password = bool(data.get("password"))

    for field in ("nombre", "apellido"):
        if field in data:
            setattr(user, field, data[field].strip())

    if "rol" in data and data["rol"] in ("administrador", "comercial"):
        user.rol = data["rol"]
    if "activo" in data:
        user.activo = bool(data["activo"])
    if "password" in data and data["password"]:
        user.set_password(data["password"])

    db.session.commit()

    valores_nue = {"nombre": user.nombre, "apellido": user.apellido,
                   "rol": user.rol, "activo": user.activo}
    ant_diff = {k: str(v) for k, v in valores_ant.items() if valores_ant[k] != valores_nue[k]}
    nue_diff = {k: str(valores_nue[k]) for k in ant_diff}
    info = {"cambio_password": True} if cambio_password else None
    auditar("USUARIOS", "MODIFICACION_USUARIO", usuario=get_current_user(), modulo="Empresas",
            entidad="Usuario", registro_id=user.id, resultado="EXITO",
            info=info, valores_anteriores=ant_diff or None, valores_nuevos=nue_diff or None)
    return success(data=user.to_dict(), message="Usuario actualizado")


@empresas_bp.route("/usuarios/<int:user_id>/toggle", methods=["PATCH"])
@propietario_required
def toggle_usuario(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_propietario():
        return error("No se puede desactivar al propietario", 403)
    user.activo = not user.activo
    db.session.commit()
    auditar("USUARIOS", "ACTIVAR_USUARIO" if user.activo else "DESACTIVAR_USUARIO",
            usuario=get_current_user(), modulo="Empresas", entidad="Usuario",
            registro_id=user.id, resultado="EXITO", info={"email": user.email})
    return success(data=user.to_dict(),
                   message=f"Usuario {'activado' if user.activo else 'desactivado'}")
