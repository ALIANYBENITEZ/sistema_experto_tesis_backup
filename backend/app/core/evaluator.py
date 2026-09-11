"""
Evaluador de reglas IF-THEN por factor.
Recibe un factor, un valor validado, y determina qué regla se aplica.
"""
from .schemas import (
    TIPO_DATO_NUMERICO, TIPO_DATO_PORCENTAJE,
    TIPO_DATO_BOOLEANO, TIPO_DATO_CATALOGO, TIPO_DATO_TEXTO,
    NIVEL_ALTO,
)


def evaluar_factor(factor, valor_normalizado) -> dict:
    """
    Evalúa un valor contra las reglas del factor.

    Returns:
        {
            "regla_aplicada": str | None,
            "nivel": str,
            "peso": float,
            "explicacion": str,
        }
    """
    reglas = factor.reglas  # ya ordenadas por 'orden'

    for regla in reglas:
        if _regla_cumple(regla, valor_normalizado, factor.tipo_dato):
            return {
                "regla_aplicada": regla.nombre,
                "nivel": regla.nivel,
                "peso": float(regla.peso),
                "explicacion": regla.explicacion or f"Se aplicó la regla '{regla.nombre}'.",
            }

    # Ninguna regla coincidió — asignar nivel alto como seguridad
    return {
        "regla_aplicada": None,
        "nivel": NIVEL_ALTO,
        "peso": 0,
        "explicacion": f"No se encontró una regla aplicable para el valor '{valor_normalizado}' en '{factor.nombre}'.",
    }


def _regla_cumple(regla, valor, tipo_dato: str) -> bool:
    """Evalúa si un valor cumple la condición de una regla."""
    op = regla.operador.strip()

    # Operadores numéricos
    if tipo_dato in (TIPO_DATO_NUMERICO, TIPO_DATO_PORCENTAJE):
        try:
            v = float(valor)
        except (ValueError, TypeError):
            return False

        if op == "entre":
            # valor_min y valor_max definen el rango
            try:
                vmin = float(regla.valor_min) if regla.valor_min else None
                vmax = float(regla.valor_max) if regla.valor_max else None
            except (ValueError, TypeError):
                return False
            if vmin is not None and vmax is not None:
                return vmin <= v <= vmax
            elif vmin is not None:
                return v >= vmin
            elif vmax is not None:
                return v <= vmax
            return False

        # Operadores simples
        try:
            ref = float(regla.valor_min) if regla.valor_min else 0
        except (ValueError, TypeError):
            return False

        if op == ">=": return v >= ref
        if op == "<=": return v <= ref
        if op == ">":  return v > ref
        if op == "<":  return v < ref
        if op == "==": return v == ref
        if op == "!=": return v != ref

    # Booleanos
    elif tipo_dato == TIPO_DATO_BOOLEANO:
        ref = regla.valor_min.lower().strip() if regla.valor_min else "false"
        ref_bool = ref in ("true", "1", "si", "sí")
        if op == "==": return valor == ref_bool
        if op == "!=": return valor != ref_bool

    # Catálogo / Texto
    elif tipo_dato in (TIPO_DATO_CATALOGO, TIPO_DATO_TEXTO):
        ref = regla.valor_min.lower().strip() if regla.valor_min else ""

        if op == "==": return str(valor).lower() == ref
        if op == "!=": return str(valor).lower() != ref
        if op == "en":
            # valor_min contiene lista separada por comas
            opciones = [x.strip().lower() for x in ref.split(",")]
            return str(valor).lower() in opciones

    return False
