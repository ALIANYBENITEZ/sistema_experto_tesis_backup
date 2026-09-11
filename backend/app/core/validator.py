"""
Validador de datos de entrada para el Core de Scoring.
Valida tipos, rangos, valores permitidos y campos obligatorios.
"""
from .schemas import (
    TIPO_DATO_NUMERICO, TIPO_DATO_PORCENTAJE,
    TIPO_DATO_CATALOGO, TIPO_DATO_BOOLEANO, TIPO_DATO_TEXTO,
    ESTADO_EVALUADO, ESTADO_SIN_DATO, ESTADO_INVALIDO,
)


def validar_valor(valor, factor) -> dict:
    """
    Valida el valor de un factor y lo normaliza.

    Returns:
        {
            "valido": bool,
            "valor_normalizado": any,
            "estado": str,
            "error": str | None,
        }
    """
    # Dato faltante
    if valor is None or (isinstance(valor, str) and valor.strip() == ""):
        return {
            "valido": False,
            "valor_normalizado": None,
            "estado": ESTADO_SIN_DATO,
            "error": f"El factor '{factor.nombre}' no tiene valor asignado.",
        }

    tipo = factor.tipo_dato

    if tipo in (TIPO_DATO_NUMERICO, TIPO_DATO_PORCENTAJE):
        try:
            num = float(str(valor).replace(",", ".").strip())
            if tipo == TIPO_DATO_PORCENTAJE and (num < 0 or num > 100):
                return {
                    "valido": False,
                    "valor_normalizado": num,
                    "estado": ESTADO_INVALIDO,
                    "error": f"El porcentaje debe estar entre 0 y 100. Valor recibido: {num}",
                }
            if num < 0 and tipo == TIPO_DATO_NUMERICO:
                return {
                    "valido": False,
                    "valor_normalizado": num,
                    "estado": ESTADO_INVALIDO,
                    "error": f"El valor numérico no puede ser negativo. Valor recibido: {num}",
                }
            return {"valido": True, "valor_normalizado": num, "estado": ESTADO_EVALUADO, "error": None}
        except (ValueError, TypeError):
            return {
                "valido": False,
                "valor_normalizado": None,
                "estado": ESTADO_INVALIDO,
                "error": f"El valor '{valor}' no es un número válido para '{factor.nombre}'.",
            }

    elif tipo == TIPO_DATO_BOOLEANO:
        if isinstance(valor, bool):
            return {"valido": True, "valor_normalizado": valor, "estado": ESTADO_EVALUADO, "error": None}
        v = str(valor).lower().strip()
        if v in ("true", "1", "si", "sí", "yes"):
            return {"valido": True, "valor_normalizado": True, "estado": ESTADO_EVALUADO, "error": None}
        elif v in ("false", "0", "no"):
            return {"valido": True, "valor_normalizado": False, "estado": ESTADO_EVALUADO, "error": None}
        return {
            "valido": False,
            "valor_normalizado": None,
            "estado": ESTADO_INVALIDO,
            "error": f"El valor '{valor}' no es un booleano válido para '{factor.nombre}'.",
        }

    elif tipo in (TIPO_DATO_CATALOGO, TIPO_DATO_TEXTO):
        v = str(valor).strip().lower()
        if not v:
            return {"valido": False, "valor_normalizado": None, "estado": ESTADO_SIN_DATO, "error": "Valor vacío."}
        # Si tiene catálogo, validar contra opciones
        if factor.catalogo:
            opciones = [c.valor.lower() for c in factor.catalogo]
            if v not in opciones:
                return {
                    "valido": False,
                    "valor_normalizado": v,
                    "estado": ESTADO_INVALIDO,
                    "error": f"El valor '{valor}' no es una opción válida. Opciones: {', '.join(opciones)}",
                }
        return {"valido": True, "valor_normalizado": v, "estado": ESTADO_EVALUADO, "error": None}

    # Tipo desconocido
    return {"valido": True, "valor_normalizado": str(valor).strip(), "estado": ESTADO_EVALUADO, "error": None}
