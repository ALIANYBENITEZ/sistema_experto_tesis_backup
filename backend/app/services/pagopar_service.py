"""
Servicio de integración con la pasarela de pagos Pagopar (Paraguay).

Flujo oficial (https://soporte.pagopar.com/portal/es/kb/api):
  1. El comercio crea un pedido en Pagopar        -> iniciar_transaccion()
  2. Se redirige al comprador al checkout de Pagopar
  3. Pagopar notifica el resultado al comercio (webhook) -> procesar_webhook()
  4. Pagopar redirige de vuelta a la página de resultado

Autenticación: cada operación viaja con un `token` SHA1 calculado a partir de
la clave privada del comercio y datos del pedido. Las claves (public/private)
se obtienen en el panel de Pagopar: "Integrar con mi sitio web".

Moneda: guaraníes (PYG), endpoint estándar `iniciar-transaccion`.
"""
import hashlib
from datetime import datetime, timedelta, timezone

import requests
from flask import current_app

# Tiempo máximo de espera para las llamadas HTTP a Pagopar (segundos)
_TIMEOUT = 20


class PagoparError(Exception):
    """Error de negocio/comunicación con Pagopar."""


def esta_configurado() -> bool:
    """True si hay credenciales cargadas (public + private key)."""
    return bool(
        current_app.config.get("PAGOPAR_PUBLIC_KEY")
        and current_app.config.get("PAGOPAR_PRIVATE_KEY")
    )


def _private_key() -> str:
    return current_app.config.get("PAGOPAR_PRIVATE_KEY", "")


def _public_key() -> str:
    return current_app.config.get("PAGOPAR_PUBLIC_KEY", "")


def _base_url() -> str:
    return current_app.config.get("PAGOPAR_BASE_URL", "https://api.pagopar.com/api").rstrip("/")


def _sha1(texto: str) -> str:
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()


def _token_iniciar(id_pedido: str, monto_total) -> str:
    """
    Token para iniciar la transacción.
    Se calcula como SHA1(private_key + id_pedido + monto_total).
    El monto va como entero en guaraníes (sin decimales).
    """
    return _sha1(f"{_private_key()}{id_pedido}{int(monto_total)}")


def _token_consulta(hash_pedido: str) -> str:
    """Token para consultar un pedido: SHA1(private_key + hash_pedido)."""
    return _sha1(f"{_private_key()}{hash_pedido}")


def iniciar_transaccion(
    *,
    id_pedido: str,
    monto_total: int,
    descripcion: str,
    comprador: dict,
    fecha_maxima_pago: datetime | None = None,
) -> dict:
    """
    Crea un pedido en Pagopar y devuelve los datos para redirigir al checkout.

    Parámetros:
      id_pedido     Identificador único del pedido en NUESTRO sistema (string).
      monto_total   Monto total en guaraníes (entero).
      descripcion   Texto descriptivo del cobro (ej. "Facturación 07/2026").
      comprador     dict con datos del comprador (ruc, email, nombre, telefono, ...).

    Retorna un dict con al menos:
      { "hash_pedido": str, "url_checkout": str, "raw": <respuesta completa> }

    Lanza PagoparError si la integración no está configurada o Pagopar responde error.
    """
    if not esta_configurado():
        raise PagoparError("Pagopar no está configurado (faltan las credenciales).")

    if fecha_maxima_pago is None:
        fecha_maxima_pago = datetime.now(timezone.utc) + timedelta(hours=48)

    payload = {
        "token": _token_iniciar(id_pedido, monto_total),
        "comercio": _public_key(),
        "public_key": _public_key(),
        "monto_total": int(monto_total),
        "tipo_pedido": "VENTA-COMERCIO",
        "compras_items": [
            {
                "ciudad": comprador.get("ciudad", "1"),
                "nombre": descripcion,
                "cantidad": 1,
                "categoria": "909",           # categoría genérica de servicios
                "public_key": _public_key(),
                "url_imagen": "",
                "descripcion": descripcion,
                "id_producto": id_pedido,
                "precio_total": int(monto_total),
                "vendedor_telefono": comprador.get("telefono", ""),
                "vendedor_direccion": comprador.get("direccion", ""),
                "vendedor_direccion_referencia": "",
                "vendedor_direccion_coordenadas": "",
            }
        ],
        "fecha_maxima_pago": fecha_maxima_pago.strftime("%Y-%m-%d %H:%M:%S"),
        "id_pedido_comercio": id_pedido,
        "descripcion_resumen": descripcion,
        "comprador": {
            "ruc": comprador.get("ruc", ""),
            "email": comprador.get("email", ""),
            "ciudad": comprador.get("ciudad", "1"),
            "nombre": comprador.get("nombre", ""),
            "telefono": comprador.get("telefono", ""),
            "direccion": comprador.get("direccion", ""),
            "documento": comprador.get("documento", comprador.get("ruc", "")),
            "razon_social": comprador.get("nombre", ""),
            "tipo_documento": comprador.get("tipo_documento", "RUC"),
            "direccion_referencia": "",
            "coordenadas": "",
        },
    }

    url = f"{_base_url()}/comercios/2.0/iniciar-transaccion"
    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise PagoparError(f"Error de comunicación con Pagopar: {exc}") from exc
    except ValueError as exc:
        raise PagoparError("Respuesta inválida de Pagopar (no es JSON).") from exc

    # Pagopar responde { "respuesta": true/false, "resultado": [ {...} ] }
    if not data.get("respuesta"):
        raise PagoparError(f"Pagopar rechazó la solicitud: {data.get('resultado') or data}")

    resultado = data.get("resultado")
    if isinstance(resultado, list) and resultado:
        resultado = resultado[0]
    if not isinstance(resultado, dict):
        raise PagoparError("Pagopar no devolvió el detalle del pedido.")

    hash_pedido = resultado.get("data") or resultado.get("hash_pedido")
    if not hash_pedido:
        raise PagoparError("Pagopar no devolvió el hash del pedido.")

    return {
        "hash_pedido": hash_pedido,
        "url_checkout": f"https://www.pagopar.com/pagos/{hash_pedido}",
        "raw": resultado,
    }


def consultar_pedido(hash_pedido: str) -> dict:
    """
    Consulta el estado de un pedido en Pagopar (endpoint traer-pedido).
    Útil para verificar el pago desde el backend sin depender solo del webhook.

    Retorna el dict del pedido tal como lo entrega Pagopar (incluye 'pagado').
    """
    if not esta_configurado():
        raise PagoparError("Pagopar no está configurado (faltan las credenciales).")

    payload = {
        "hash_pedido": hash_pedido,
        "token": _token_consulta(hash_pedido),
        "token_publico": _public_key(),
    }
    url = f"{_base_url()}/pedidos/1.1/traer"
    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise PagoparError(f"Error de comunicación con Pagopar: {exc}") from exc
    except ValueError as exc:
        raise PagoparError("Respuesta inválida de Pagopar (no es JSON).") from exc

    if not data.get("respuesta"):
        raise PagoparError(f"Pagopar rechazó la consulta: {data.get('resultado') or data}")

    resultado = data.get("resultado")
    if isinstance(resultado, list) and resultado:
        resultado = resultado[0]
    if not isinstance(resultado, dict):
        raise PagoparError("Pagopar no devolvió el detalle del pedido.")
    return resultado


def procesar_webhook(payload: dict) -> dict:
    """
    Valida y normaliza la notificación de pago que Pagopar envía al webhook.

    Pagopar envía el resultado del pedido junto con un 'token' de integridad
    calculado como SHA1(private_key + hash_pedido). Se recalcula y compara para
    asegurar que la notificación es auténtica.

    Retorna un dict normalizado:
      { "hash_pedido": str, "pagado": bool, "id_pedido_comercio": str,
        "monto": int|None, "forma_pago": str|None }

    Lanza PagoparError si el token no coincide o faltan datos.
    """
    resultado = payload.get("resultado")
    if isinstance(resultado, list) and resultado:
        resultado = resultado[0]
    if not isinstance(resultado, dict):
        # Algunos envíos vienen en el nivel superior
        resultado = payload

    hash_pedido = resultado.get("hash_pedido") or resultado.get("data")
    if not hash_pedido:
        raise PagoparError("El webhook no incluye hash_pedido.")

    token_recibido = resultado.get("token") or payload.get("token")
    token_esperado = _token_consulta(hash_pedido)
    if not token_recibido or token_recibido != token_esperado:
        raise PagoparError("Token del webhook inválido: la notificación no es auténtica.")

    monto = resultado.get("monto") or resultado.get("monto_total")
    try:
        monto = int(float(monto)) if monto is not None else None
    except (TypeError, ValueError):
        monto = None

    return {
        "hash_pedido": hash_pedido,
        "pagado": bool(resultado.get("pagado")),
        "id_pedido_comercio": resultado.get("numero_pedido") or resultado.get("id_pedido_comercio"),
        "monto": monto,
        "forma_pago": resultado.get("forma_pago") or resultado.get("descripcion_forma_pago"),
    }


def respuesta_webhook(hash_pedido: str) -> dict:
    """
    Cuerpo que Pagopar espera como confirmación de recepción del webhook.
    Debe reenviarse el hash junto con el token de consulta.
    """
    return {
        "respuesta": True,
        "resultado": [{"hash_pedido": hash_pedido, "token": _token_consulta(hash_pedido)}],
    }
