"""
Servicio de 2FA con PyOTP + Google Authenticator.
Genera secretos, URIs y valida códigos OTP.
"""
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timezone

APP_NAME = "ScoringComercial"


def generar_secreto() -> str:
    """Genera un secreto TOTP criptográficamente seguro."""
    return pyotp.random_base32()


def generar_uri(secreto: str, email: str, empresa_nombre: str = None) -> str:
    """Genera la URI otpauth:// compatible con Google Authenticator."""
    issuer = f"{APP_NAME}"
    if empresa_nombre:
        issuer = f"{APP_NAME} ({empresa_nombre})"
    totp = pyotp.TOTP(secreto)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generar_qr_base64(uri: str) -> str:
    """Genera un código QR como imagen base64 (PNG)."""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def validar_otp(secreto: str, codigo: str) -> bool:
    """
    Valida un código OTP contra el secreto.
    Usa tolerancia de 1 ventana (30 segundos antes/después).
    """
    if not secreto or not codigo:
        return False
    totp = pyotp.TOTP(secreto)
    return totp.verify(codigo, valid_window=1)
