from flask import request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import User
from app.utils.decorators import admin_required
from app.utils.responses import success, error
from . import users_bp


@users_bp.route("/", methods=["GET"])
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return success(data=[u.to_dict() for u in users])


@users_bp.route("/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return success(data=user.to_dict())


@users_bp.route("/", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    required = ["nombre", "apellido", "email", "password", "rol"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    if data["rol"] not in (User.ROL_ADMIN, User.ROL_OPERADOR):
        return error("Rol inválido. Use 'administrador' u 'operador'", 400)

    if User.query.filter_by(email=data["email"].lower()).first():
        return error("El email ya está registrado", 409)

    user = User(
        nombre   = data["nombre"].strip(),
        apellido = data["apellido"].strip(),
        email    = data["email"].strip().lower(),
        rol      = data["rol"],
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return success(data=user.to_dict(), message="Usuario creado", status=201)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json(silent=True) or {}

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
    if "rol" in data:
        if data["rol"] not in (User.ROL_ADMIN, User.ROL_OPERADOR):
            return error("Rol inválido", 400)
        user.rol = data["rol"]
    if "password" in data and data["password"]:
        user.set_password(data["password"])

    db.session.commit()
    return success(data=user.to_dict(), message="Usuario actualizado")


@users_bp.route("/<int:user_id>/toggle", methods=["PATCH"])
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.activo = not user.activo
    db.session.commit()
    estado = "activado" if user.activo else "desactivado"
    return success(data=user.to_dict(), message=f"Usuario {estado}")
