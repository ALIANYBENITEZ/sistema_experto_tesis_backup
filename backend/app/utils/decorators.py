from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User


def roles_required(*roles):
    """Decorator que restringe el acceso a los roles indicados."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            if not user or not user.activo:
                return jsonify({"success": False, "message": "Usuario no autorizado"}), 403
            if user.rol not in roles:
                return jsonify({"success": False, "message": "No tienes permisos para esta acción"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Acceso para administradores de empresa y propietario."""
    return roles_required("propietario", "administrador")(fn)


def propietario_required(fn):
    """Acceso exclusivo para el propietario del sistema (id_empresa=0)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or not user.activo:
            return jsonify({"success": False, "message": "Usuario no autorizado"}), 403
        if not user.is_propietario():
            return jsonify({"success": False, "message": "Acceso exclusivo del propietario"}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Helper para obtener el usuario actual dentro de un endpoint protegido."""
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)
