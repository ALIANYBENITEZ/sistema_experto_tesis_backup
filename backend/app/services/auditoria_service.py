"""
Servicio de Auditoría.
Registra eventos del sistema sin romper el flujo normal si falla.
"""
import json
from flask import request, has_request_context
from app.extensions import db
from app.models.auditoria import Auditoria


def _get_ip():
    """Obtiene la IP del cliente de forma segura."""
    if not has_request_context():
        return None
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def registrar(tipo_evento, accion, *, usuario=None, modulo=None, entidad=None,
              registro_id=None, resultado="EXITO", info=None,
              valores_anteriores=None, valores_nuevos=None):
    """
    Registra un evento de auditoría.

    No propaga errores para no romper la operación principal.
    NO almacena contraseñas, tokens ni secretos.
    """
    try:
        aud = Auditoria(
            usuario_id=usuario.id if usuario else None,
            usuario_nombre=f"{usuario.nombre} {usuario.apellido}" if usuario else None,
            id_empresa=usuario.id_empresa if usuario else None,
            tipo_evento=tipo_evento,
            accion=accion,
            modulo=modulo,
            entidad=entidad,
            registro_id=str(registro_id) if registro_id is not None else None,
            resultado=resultado,
            ip=_get_ip(),
            info_adicional=json.dumps(info, ensure_ascii=False) if info else None,
            valores_anteriores=json.dumps(valores_anteriores, ensure_ascii=False) if valores_anteriores else None,
            valores_nuevos=json.dumps(valores_nuevos, ensure_ascii=False) if valores_nuevos else None,
        )
        db.session.add(aud)
        db.session.commit()
    except Exception:
        # La auditoría no debe romper la operación principal
        try:
            db.session.rollback()
        except Exception:
            pass
