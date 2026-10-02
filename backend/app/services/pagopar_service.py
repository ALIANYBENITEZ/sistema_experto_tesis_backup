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


def _forma_pago() -> int:
    """
    Forma de pago a enviar en el pedido. La API la exige (sin ella rechaza el
    pedido). 26 es el valor usado en los ejemplos oficiales. Configurable con
    PAGOPAR_FORMA_PAGO por si cambia.
    """
    try:
        return int(current_app.config.get("PAGOPAR_FORMA_PAGO", 26))
    except (TypeError, ValueError):
        return 26


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


def _resolver_documento(comprador: dict) -> str:
    """
    Devuelve el documento identificador del comprador.

    La API de Pagopar solo acepta tipo_documento="CI" y el valor del documento
    puede llevar guion (ej. "80012345-1"). Usamos el RUC/identificador de la
    empresa tal cual viene (con su dígito verificador). Si viniera un campo
    `documento` explícito, tiene prioridad.
    """
    return (comprador.get("documento") or comprador.get("ruc") or "").strip()


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

    # Pagopar rechaza el pedido si el comprador no tiene documento.
    documento = _resolver_documento(comprador)
    if not documento:
        raise PagoparError(
            "La empresa no tiene documento (RUC/CI) cargado. "
            "Registre el RUC de la empresa antes de pagar."
        )
    if not (comprador.get("nombre") or "").strip():
        raise PagoparError("El comprador no tiene nombre/razón social.")
    if not (comprador.get("email") or "").strip():
        raise PagoparError("El comprador no tiene email.")

    payload = {
        "token": _token_iniciar(id_pedido, monto_total),
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
        # forma_pago es OBLIGATORIO para esta versión de la API: sin él, Pagopar
        # rechaza el pedido con un mensaje engañoso ("El documento debe estar
        # presente"). Se toma de la config (PAGOPAR_FORMA_PAGO) con 26 por defecto.
        "forma_pago": _forma_pago(),
        # El objeto comprador debe tener EXACTAMENTE estos 11 campos y en este
        # formato (confirmado contra la API de Pagopar):
        #   - tipo_documento SOLO acepta "CI".
        #   - documento es el identificador del comprador (admite guion).
        #   - ruc puede ir vacío si el comprador no tiene identificación fiscal.
        #   - ciudad y direccion_referencia van como null.
        #   - coordenadas NO puede ir vacío.
        "comprador": {
            "ruc": comprador.get("ruc", "") or "",
            "email": comprador.get("email", ""),
            "ciudad": None,
            "nombre": comprador.get("nombre", ""),
            "telefono": comprador.get("telefono", ""),
            "direccion": comprador.get("direccion", "") or "",
            "documento": documento,
            "coordenadas": comprador.get("coordenadas") or "0",
            "razon_social": comprador.get("nombre", ""),
            "tipo_documento": "CI",
            "direccion_referencia": None,
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
