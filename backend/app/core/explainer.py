"""
Generador de explicaciones del Core de Scoring.
Produce explicaciones individuales por factor y una explicación global.
"""
from .schemas import NIVEL_BAJO, NIVEL_MEDIO, NIVEL_ALTO, ESTADO_EVALUADO


def generar_explicacion_global(detalles: list, clasificacion: str, score_total: float) -> str:
    """
    Genera una explicación textual del resultado global de la evaluación.
    Solo reporta como desfavorables los factores con nivel MEDIO o ALTO.
    """
    evaluados = [d for d in detalles if d["estado"] == ESTADO_EVALUADO]

    if not evaluados:
        return "No se pudieron evaluar factores suficientes para generar una clasificación confiable."

    # Solo factores con nivel medio o alto son "desfavorables" en la explicación
    desfavorables = sorted(
        [d for d in evaluados if d.get("nivel") in (NIVEL_MEDIO, NIVEL_ALTO)],
        key=lambda d: d["peso"], reverse=True
    )
    # Solo factores con peso negativo son "favorables"
    favorables = sorted(
        [d for d in evaluados if d["peso"] < 0],
        key=lambda d: d["peso"]
    )

    # Construir texto
    nivel_texto = {
        "bajo": "un nivel de riesgo BAJO",
        "medio": "un nivel de riesgo MEDIO",
        "alto": "un nivel de riesgo ALTO",
    }

    texto = f"El cliente presenta {nivel_texto.get(clasificacion, 'un nivel de riesgo indeterminado')}. "
    texto += f"Score total: {score_total:.1f} puntos. "

    if desfavorables:
        nombres = ", ".join(d["factor_nombre"] for d in desfavorables)
        texto += f"Los principales factores que incrementaron el riesgo son: {nombres}. "

    if favorables:
        nombres = ", ".join(d["factor_nombre"] for d in favorables)
        texto += f"Como factores favorables se identificaron: {nombres}. "

    sin_dato = [d for d in detalles if d["estado"] == "sin_dato"]
    if sin_dato:
        texto += f"Se identificaron {len(sin_dato)} factor(es) sin información disponible."

    return texto.strip()


def identificar_factores_impacto(detalles: list) -> dict:
    """
    Identifica los factores de mayor y menor impacto.
    Solo considera como desfavorables los que tienen nivel MEDIO o ALTO.
    """
    evaluados = [d for d in detalles if d["estado"] == ESTADO_EVALUADO]

    return {
        "desfavorables": sorted(
            [d for d in evaluados if d.get("nivel") in (NIVEL_MEDIO, NIVEL_ALTO)],
            key=lambda d: d["peso"], reverse=True
        ),
        "favorables": sorted(
            [d for d in evaluados if d["peso"] < 0],
            key=lambda d: d["peso"]
        ),
        "neutros": [d for d in evaluados if d.get("nivel") == NIVEL_BAJO and d["peso"] >= 0],
        "sin_dato": [d for d in detalles if d["estado"] != ESTADO_EVALUADO],
    }
