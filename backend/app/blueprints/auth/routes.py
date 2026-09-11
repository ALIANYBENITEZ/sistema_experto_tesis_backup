from datetime import datetime, timezone
from flask import request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
from app.extensions import db
from app.models import User
from app.utils.responses import success, error
from app.services.totp_service import generar_secreto, generar_uri, generar_qr_base64, validar_otp
from app.services.auditoria_service import registrar as auditar
from . import auth_bp


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login con soporte 2FA.
    Retorna estados:
      - 2fa_setup_required: debe configurar 2FA (nuevo QR)
      - 2fa_required: debe ingresar OTP
      - authenticated: acceso completo (solo si no tiene 2FA o lo completó)
    """
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return error("Email y contraseña son requeridos", 400)

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        auditar("AUTENTICACION", "LOGIN_FALLIDO", usuario=user, modulo="Login",
                entidad="Usuario", resultado="FALLO", info={"email": email})
        return error("Credenciales incorrectas", 401)

    if not user.activo:
        auditar("AUTENTICACION", "LOGIN_FALLIDO", usuario=user, modulo="Login",
                entidad="Usuario", resultado="FALLO", info={"motivo": "usuario desactivado"})
        return error("Usuario desactivado. Contacte al administrador", 403)

    auditar("AUTENTICACION", "LOGIN_EXITOSO", usuario=user, modulo="Login",
            entidad="Usuario", registro_id=user.id, resultado="EXITO")

    # Verificar estado de 2FA
    if user.requiere_config_2fa:
        # Si ya tiene un secreto pendiente, reutilizarlo. Si no, generar uno nuevo.
        if not user.totp_secret or user.totp_estado in ("no_configurado", "restablecido", None):
            secreto = generar_secreto()
            user.totp_secret = secreto
            user.totp_estado = "pendiente"
            db.session.commit()
        else:
            secreto = user.totp_secret

        uri = generar_uri(secreto, user.email, user.empresa.nombre if user.empresa else None)
        qr_base64 = generar_qr_base64(uri)

        # Token parcial (solo para completar 2FA setup)
        partial_token = create_access_token(
            identity=str(user.id),
            additional_claims={"auth_state": "2fa_setup", "2fa": False}
        )

        return success(data={
            "auth_state": "2fa_setup_required",
            "partial_token": partial_token,
            "qr_code": qr_base64,
            "user": {"id": user.id, "nombre": user.nombre, "email": user.email},
        }, message="Configuración de 2FA requerida")

    elif user.tiene_2fa:
        # Token parcial (solo para verificar OTP)
        partial_token = create_access_token(
            identity=str(user.id),
            additional_claims={"auth_state": "2fa_pending", "2fa": False}
        )

        return success(data={
            "auth_state": "2fa_required",
            "partial_token": partial_token,
            "user": {"id": user.id, "nombre": user.nombre, "email": user.email},
        }, message="Ingrese el código de Google Authenticator")

    else:
        # Estado desconocido — forzar configuración de 2FA por seguridad
        secreto = generar_secreto()
        user.totp_secret = secreto
        user.totp_estado = "pendiente"
        db.session.commit()

        uri = generar_uri(secreto, user.email, user.empresa.nombre if user.empresa else None)
        qr_base64 = generar_qr_base64(uri)

        partial_token = create_access_token(
            identity=str(user.id),
            additional_claims={"auth_state": "2fa_setup", "2fa": False}
        )

        return success(data={
            "auth_state": "2fa_setup_required",
            "partial_token": partial_token,
            "qr_code": qr_base64,
            "user": {"id": user.id, "nombre": user.nombre, "email": user.email},
        }, message="Configuración de 2FA requerida")


@auth_bp.route("/2fa/setup", methods=["POST"])
@jwt_required()
def setup_2fa():
    """
    Valida el primer OTP durante la configuración del 2FA.
    Requiere el partial_token del login.
    """
    claims = get_jwt()
    if claims.get("auth_state") != "2fa_setup":
        return error("Token no válido para esta operación", 403)

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error("Usuario no encontrado", 404)

    data = request.get_json(silent=True) or {}
    codigo = data.get("codigo", "").strip()

    if not codigo or len(codigo) != 6:
        return error("Ingrese un código de 6 dígitos", 400)

    if not validar_otp(user.totp_secret, codigo):
        return error("Código OTP incorrecto. Verifique e intente nuevamente.", 401)

    # Activar 2FA
    user.totp_estado = "activado"
    user.totp_fecha_config = datetime.now(timezone.utc)
    db.session.commit()

    # Generar tokens completos
    access_token  = create_access_token(
        identity=str(user.id),
        additional_claims={"auth_state": "authenticated", "2fa": True}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return success(data={
        "auth_state": "authenticated",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }, message="2FA configurado exitosamente")


@auth_bp.route("/2fa/verify", methods=["POST"])
@jwt_required()
def verify_2fa():
    """
    Valida el OTP en cada login para usuarios con 2FA activado.
    """
    claims = get_jwt()
    if claims.get("auth_state") != "2fa_pending":
        return error("Token no válido para esta operación", 403)

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error("Usuario no encontrado", 404)

    data = request.get_json(silent=True) or {}
    codigo = data.get("codigo", "").strip()

    if not codigo or len(codigo) != 6:
        return error("Ingrese un código de 6 dígitos", 400)

    if not validar_otp(user.totp_secret, codigo):
        return error("Código OTP incorrecto", 401)

    # Generar tokens completos
    access_token  = create_access_token(
        identity=str(user.id),
        additional_claims={"auth_state": "authenticated", "2fa": True}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return success(data={
        "auth_state": "authenticated",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }, message="Autenticación completa")


@auth_bp.route("/2fa/reset/<int:user_id>", methods=["POST"])
@jwt_required()
def reset_2fa(user_id):
    """Restablecer 2FA de un usuario. Solo admin de su empresa o propietario."""
    from app.utils.decorators import get_current_user
    current_user = get_current_user()

    target_user = User.query.get_or_404(user_id)

    # Validar permisos multi-tenant
    if not current_user.is_propietario():
        if not current_user.is_admin():
            return error("No tiene permisos para esta acción", 403)
        if current_user.id_empresa != target_user.id_empresa:
            return error("No puede gestionar usuarios de otra empresa", 403)

    if target_user.is_propietario() and not current_user.is_propietario():
        return error("No puede restablecer el 2FA del propietario", 403)

    # Restablecer
    target_user.totp_secret = None
    target_user.totp_estado = "restablecido"
    target_user.totp_fecha_reset = datetime.now(timezone.utc)
    db.session.commit()

    auditar("SEGURIDAD", "RESET_2FA", usuario=current_user, modulo="Seguridad",
            entidad="Usuario", registro_id=target_user.id, resultado="EXITO",
            info={"usuario_afectado": f"{target_user.nombre} {target_user.apellido}",
                  "email_afectado": target_user.email})

    return success(message=f"2FA restablecido para {target_user.nombre} {target_user.apellido}")


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario actual."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error("Usuario no encontrado", 404)

    data = request.get_json(silent=True) or {}
    current_pwd = data.get("current_password", "")
    new_pwd = data.get("new_password", "")
    confirm_pwd = data.get("confirm_password", "")

    if not current_pwd or not new_pwd:
        return error("Contraseña actual y nueva son requeridas", 400)
    if new_pwd != confirm_pwd:
        return error("La nueva contraseña y su confirmación no coinciden", 400)
    if len(new_pwd) < 8:
        return error("La contraseña debe tener al menos 8 caracteres", 400)
    if not user.check_password(current_pwd):
        return error("Contraseña actual incorrecta", 401)

    user.set_password(new_pwd)
    db.session.commit()

    auditar("SEGURIDAD", "CAMBIO_CONTRASENA", usuario=user, modulo="Seguridad",
            entidad="Usuario", registro_id=user.id, resultado="EXITO")

    return success(message="Contraseña actualizada correctamente")


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Recuperación de contraseña mediante OTP de Google Authenticator.
    No requiere sesión: el usuario prueba su identidad con el código de su
    authenticator (2FA ya activado) y establece una nueva contraseña.

    Body: { email, codigo (6 dígitos), new_password, confirm_password }
    """
    data = request.get_json(silent=True) or {}
    email       = data.get("email", "").strip().lower()
    codigo      = data.get("codigo", "").strip()
    new_pwd     = data.get("new_password", "")
    confirm_pwd = data.get("confirm_password", "")

    if not email or not codigo:
        return error("Email y código son requeridos", 400)
    if not new_pwd:
        return error("La nueva contraseña es requerida", 400)
    if new_pwd != confirm_pwd:
        return error("La nueva contraseña y su confirmación no coinciden", 400)
    if len(new_pwd) < 8:
        return error("La contraseña debe tener al menos 8 caracteres", 400)
    if len(codigo) != 6:
        return error("Ingrese un código de 6 dígitos", 400)

    user = User.query.filter_by(email=email).first()

    # Mensaje genérico para no revelar si el email existe o si tiene 2FA
    generic_err = ("No fue posible restablecer la contraseña. "
                   "Verifique el correo y el código, o contacte a su administrador.")

    if not user or not user.activo:
        auditar("SEGURIDAD", "RECUPERAR_CONTRASENA", usuario=user, modulo="Seguridad",
                entidad="Usuario", resultado="FALLO", info={"email": email, "motivo": "usuario inválido"})
        return error(generic_err, 400)

    # Solo se puede recuperar si el usuario tiene 2FA activado (hay un authenticator asociado)
    if not user.tiene_2fa or not user.totp_secret:
        auditar("SEGURIDAD", "RECUPERAR_CONTRASENA", usuario=user, modulo="Seguridad",
                entidad="Usuario", registro_id=user.id, resultado="FALLO",
                info={"motivo": "sin 2FA activado"})
        return error(generic_err, 400)

    if not validar_otp(user.totp_secret, codigo):
        auditar("SEGURIDAD", "RECUPERAR_CONTRASENA", usuario=user, modulo="Seguridad",
                entidad="Usuario", registro_id=user.id, resultado="FALLO",
                info={"motivo": "OTP incorrecto"})
        return error(generic_err, 400)

    user.set_password(new_pwd)
    db.session.commit()

    auditar("SEGURIDAD", "RECUPERAR_CONTRASENA", usuario=user, modulo="Seguridad",
            entidad="Usuario", registro_id=user.id, resultado="EXITO")

    return success(message="Contraseña restablecida correctamente. Ya puede iniciar sesión.")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.activo:
        return error("Usuario no válido", 401)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"auth_state": "authenticated", "2fa": True}
    )
    return success(data={"access_token": access_token})


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    # Verificar que el token sea de autenticación completa
    claims = get_jwt()
    if claims.get("auth_state") != "authenticated":
        return error("Autenticación incompleta", 401)

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error("Usuario no encontrado", 404)
    return success(data=user.to_dict())


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    from app.utils.decorators import get_current_user
    user = get_current_user()
    auditar("AUTENTICACION", "LOGOUT", usuario=user, modulo="Login",
            entidad="Usuario", registro_id=user.id if user else None, resultado="EXITO")
    return success(message="Sesión cerrada correctamente")


# ── Endpoint de seguridad: listar usuarios con estado 2FA ──
@auth_bp.route("/security/users", methods=["GET"])
@jwt_required()
def security_users():
    """Lista usuarios con su estado de 2FA. Admin ve su empresa, propietario ve todo."""
    from app.utils.decorators import get_current_user
    current_user = get_current_user()

    if not current_user.is_admin():
        return error("No tiene permisos", 403)

    if current_user.is_propietario():
        users = User.query.order_by(User.id_empresa, User.nombre).all()
    else:
        users = User.query.filter_by(id_empresa=current_user.id_empresa).order_by(User.nombre).all()

    data = []
    for u in users:
        data.append({
            "id": u.id,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "email": u.email,
            "rol": u.rol,
            "activo": u.activo,
            "id_empresa": u.id_empresa,
            "empresa_nombre": u.empresa.nombre if u.empresa else "Sistema",
            "totp_estado": u.totp_estado,
            "tiene_2fa": u.tiene_2fa,
            "totp_fecha_config": u.totp_fecha_config.isoformat() if u.totp_fecha_config else None,
            "totp_fecha_reset": u.totp_fecha_reset.isoformat() if u.totp_fecha_reset else None,
        })

    return success(data=data)
