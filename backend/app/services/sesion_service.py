"""
Servicio de sesión única por usuario (single session).

Garantiza que un mismo usuario no pueda tener dos sesiones activas en
dispositivos distintos: cada login genera un identificador de sesión (sid) que
se incrusta en el JWT y se registra aquí como el ÚNICO válido para ese usuario.
Cuando el usuario inicia sesión en otro dispositivo, el sid anterior deja de ser
válido y las peticiones de ese dispositivo se rechazan (401).

Importante: el registro vive en memoria del proceso del backend. No crea ni
modifica tablas de la base de datos. Si el backend se reinicia, el registro se
vacía y los usuarios deberán iniciar sesión nuevamente (comportamiento aceptable
para un despliegue de un solo proceso).
"""
import threading
import uuid

# Mapa usuario_id (str) -> sid activo (str)
_sesiones_activas: dict[str, str] = {}
_lock = threading.Lock()


def nuevo_sid() -> str:
    """Genera un identificador de sesión único."""
    return uuid.uuid4().hex


def registrar_sesion(user_id, sid: str) -> None:
    """
    Registra 'sid' como la sesión activa del usuario, reemplazando cualquier
    sesión anterior (esto invalida el login previo en otro dispositivo).
    """
    with _lock:
        _sesiones_activas[str(user_id)] = sid


def es_sesion_valida(user_id, sid: str) -> bool:
    """True si 'sid' es la sesión activa registrada para el usuario."""
    if not sid:
        return False
    with _lock:
        return _sesiones_activas.get(str(user_id)) == sid


def cerrar_sesion(user_id) -> None:
    """Elimina la sesión activa del usuario (logout)."""
    with _lock:
        _sesiones_activas.pop(str(user_id), None)
