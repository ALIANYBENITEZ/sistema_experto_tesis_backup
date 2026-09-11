"""
Motor de Inferencia IF-THEN — Sistema Experto de Scoring
=========================================================
Evalúa un conjunto de hechos del cliente contra las reglas configuradas
en un MotorReglas. Implementa lógica basada en reglas con soporte a:

  - Operadores: >=, <=, ==, >, <, !=
  - Tipos de valor: numerico, texto, booleano
  - Reglas determinantes: si fallan → resultado RECHAZADO directo
  - Puntaje ponderado: suma de puntos de reglas cumplidas
  - Clasificación automática: bajo / medio / alto / rechazado
  - Recomendaciones automatizadas según resultado

Umbrales de clasificación (sobre score_maximo):
  >= 75% → bajo riesgo
  >= 50% → medio riesgo
  <  50% → alto riesgo
  Regla determinante fallida → rechazado
"""

import operator as op
from decimal import Decimal


# Operadores soportados
OPERADORES = {
    ">=": op.ge,
    "<=": op.le,
    "==": op.eq,
    ">":  op.gt,
    "<":  op.lt,
    "!=": op.ne,
}

# Umbrales de clasificación (porcentaje sobre puntaje máximo)
UMBRAL_BAJO_RIESGO   = 75.0   # >= 75% → bajo riesgo
UMBRAL_MEDIO_RIESGO  = 50.0   # >= 50% → medio riesgo
                               # <  50% → alto riesgo


# ── Recomendaciones automatizadas ─────────────────────────────────────────
RECOMENDACIONES = {
    "bajo": {
        "decision": "FAVORABLE",
        "descripcion": (
            "El cliente presenta un perfil de riesgo bajo. Cumple con la mayoría "
            "de los criterios de evaluación de forma satisfactoria."
        ),
        "acciones": [
            "Se recomienda aprobar la operación con condiciones estándar.",
            "Proceder con la firma de contrato según términos habituales.",
            "Aplicar seguimiento periódico de rutina.",
        ],
    },
    "medio": {
        "decision": "CON OBSERVACIONES",
        "descripcion": (
            "El cliente presenta un perfil de riesgo moderado. Algunos criterios "
            "no alcanzan los niveles óptimos, lo que requiere atención adicional."
        ),
        "acciones": [
            "Se recomienda aprobar con condiciones adicionales (garantía extra, depósito mayor).",
            "Solicitar documentación complementaria que respalde su capacidad de pago.",
            "Establecer un período de seguimiento más frecuente.",
            "Considerar un plazo de contrato más corto como medida de mitigación.",
        ],
    },
    "alto": {
        "decision": "DESFAVORABLE",
        "descripcion": (
            "El cliente presenta un perfil de alto riesgo. Múltiples criterios "
            "de evaluación no fueron cumplidos satisfactoriamente."
        ),
        "acciones": [
            "Se recomienda NO aprobar la operación en las condiciones actuales.",
            "Si se decide continuar, exigir garantías adicionales significativas.",
            "Solicitar un garante con perfil de riesgo bajo como respaldo.",
            "Re-evaluar al cliente en un plazo de 3 a 6 meses.",
        ],
    },
    "rechazado": {
        "decision": "RECHAZADO",
        "descripcion": (
            "El cliente ha sido rechazado automáticamente por incumplir una regla "
            "determinante del motor de evaluación. Esta regla es de carácter "
            "excluyente y no admite excepciones."
        ),
        "acciones": [
            "La operación NO debe ser aprobada bajo ninguna condición.",
            "Registrar el motivo de rechazo para auditoría.",
            "Informar al cliente sobre los requisitos no cumplidos.",
            "El cliente podrá solicitar una nueva evaluación cuando la condición excluyente sea resuelta.",
        ],
    },
}


def generar_recomendacion(categoria_riesgo: str, porcentaje: float, regla_determinante_nombre: str = None) -> dict:
    """
    Genera una recomendación automatizada basada en la categoría de riesgo.

    Returns:
        {
            "decision":     str,
            "descripcion":  str,
            "acciones":     list[str],
            "detalle_adicional": str | None,
        }
    """
    rec = RECOMENDACIONES.get(categoria_riesgo, RECOMENDACIONES["alto"])
    resultado = {
        "decision":     rec["decision"],
        "descripcion":  rec["descripcion"],
        "acciones":     rec["acciones"],
        "detalle_adicional": None,
    }

    if categoria_riesgo == "rechazado" and regla_determinante_nombre:
        resultado["detalle_adicional"] = (
            f"Regla determinante incumplida: {regla_determinante_nombre}. "
            "Esta condición es excluyente y generó el rechazo automático."
        )
    elif categoria_riesgo == "medio":
        resultado["detalle_adicional"] = (
            f"El cliente alcanzó un {porcentaje:.1f}% del puntaje máximo. "
            f"Se requiere un mínimo de {UMBRAL_BAJO_RIESGO}% para clasificar como bajo riesgo."
        )
    elif categoria_riesgo == "alto":
        resultado["detalle_adicional"] = (
            f"El cliente solo alcanzó un {porcentaje:.1f}% del puntaje máximo. "
            "Se recomienda revisar los criterios no cumplidos antes de una nueva evaluación."
        )

    return resultado


def _castear_valor(valor_str: str, tipo: str):
    """Convierte el valor de referencia o del cliente al tipo correcto."""
    tipo = tipo.lower()
    if tipo == "numerico":
        try:
            return float(str(valor_str).replace(",", ".").strip())
        except (ValueError, TypeError):
            return 0.0
    elif tipo == "booleano":
        return str(valor_str).lower() in ("true", "1", "si", "sí", "yes")
    else:
        # texto: comparación case-insensitive
        return str(valor_str).lower().strip()


def evaluar_regla(regla, hechos: dict) -> dict:
    """
    Evalúa una regla individual contra los hechos del cliente.

    Retorna:
        {
            "regla_id":        int,
            "cumplido":        bool,
            "valor_evaluado":  str,
            "puntos_obtenidos": float,
            "es_determinante": bool,
        }
    """
    parametro        = regla.parametro
    tipo_valor       = regla.tipo_valor
    operador_str     = regla.operador
    valor_referencia = _castear_valor(regla.valor_referencia, tipo_valor)
    peso             = float(regla.peso_puntos)

    # Obtener el valor del cliente en los hechos
    valor_cliente_raw = hechos.get(parametro)

    if valor_cliente_raw is None:
        # No se proporcionó el dato → regla no cumplida
        return {
            "regla_id":         regla.id,
            "cumplido":         False,
            "valor_evaluado":   "sin_dato",
            "puntos_obtenidos": 0.0,
            "es_determinante":  regla.es_determinante,
        }

    valor_cliente = _castear_valor(valor_cliente_raw, tipo_valor)
    fn_op = OPERADORES.get(operador_str)

    if fn_op is None:
        cumplido = False
    else:
        try:
            cumplido = fn_op(valor_cliente, valor_referencia)
        except TypeError:
            cumplido = False

    return {
        "regla_id":         regla.id,
        "cumplido":         cumplido,
        "valor_evaluado":   str(valor_cliente_raw),
        "puntos_obtenidos": peso if cumplido else 0.0,
        "es_determinante":  regla.es_determinante,
    }


def ejecutar_motor(motor, hechos: dict) -> dict:
    """
    Ejecuta el motor de reglas completo contra los hechos del cliente.

    Args:
        motor: instancia de MotorReglas con sus reglas cargadas
        hechos: dict con los valores del cliente {parametro: valor}

    Returns:
        {
            "score_final":       float,
            "score_maximo":      float,
            "porcentaje":        float,
            "categoria_riesgo":  str,   # bajo / medio / alto / rechazado
            "rechazado_por_regla": int | None,  # id de la regla determinante que falló
            "detalles":          list[dict],
        }
    """
    reglas_activas = motor.reglas.filter_by(activo=True).order_by("orden").all()

    if not reglas_activas:
        return {
            "score_final":           0.0,
            "score_maximo":          0.0,
            "porcentaje":            0.0,
            "categoria_riesgo":      "alto",
            "rechazado_por_regla":   None,
            "detalles":              [],
        }

    score_maximo = sum(float(r.peso_puntos) for r in reglas_activas)
    score_final  = 0.0
    detalles     = []
    rechazado_por_regla = None

    for regla in reglas_activas:
        resultado = evaluar_regla(regla, hechos)
        detalles.append(resultado)

        if resultado["cumplido"]:
            score_final += resultado["puntos_obtenidos"]
        elif resultado["es_determinante"]:
            # Regla determinante fallida → rechazo inmediato
            rechazado_por_regla = regla.id
            break  # corta la evaluación

    # Clasificar resultado
    if rechazado_por_regla is not None:
        categoria = "rechazado"
        porcentaje = 0.0
    else:
        porcentaje = (score_final / score_maximo * 100) if score_maximo > 0 else 0.0
        if porcentaje >= UMBRAL_BAJO_RIESGO:
            categoria = "bajo"
        elif porcentaje >= UMBRAL_MEDIO_RIESGO:
            categoria = "medio"
        else:
            categoria = "alto"

    return {
        "score_final":           round(score_final, 2),
        "score_maximo":          round(score_maximo, 2),
        "porcentaje":            round(porcentaje, 2),
        "categoria_riesgo":      categoria,
        "rechazado_por_regla":   rechazado_por_regla,
        "detalles":              detalles,
    }
