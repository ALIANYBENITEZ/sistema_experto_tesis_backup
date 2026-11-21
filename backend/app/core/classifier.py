"""
Clasificador de riesgo global.
Determina la clasificación final basándose en el score total y los umbrales configurados.
"""
from .schemas import RIESGO_BAJO, RIESGO_MEDIO, RIESGO_ALTO



def normalizar_score(score_total: float) -> float:
    """Garantiza que el score global nunca sea menor que cero."""
    try:
        return max(0.0, float(score_total or 0))
    except (TypeError, ValueError):
        return 0.0


def clasificar_riesgo(score_total: float, umbrales: list) -> str:
    """
    Clasifica el score total en un nivel de riesgo según los umbrales configurados.

    Args:
        score_total: suma de pesos de todos los factores evaluados.
        umbrales: lista de objetos UmbralScoring del modelo.

    Returns:
        "bajo", "medio" o "alto"
    """
    for umbral in sorted(umbrales, key=lambda u: float(u.score_min)):
        score_min = float(umbral.score_min)
        score_max = float(umbral.score_max)
        if score_min <= score_total <= score_max:
            return umbral.nivel

    # Si no encaja en ningún umbral, clasificar por lógica de seguridad
    if not umbrales:
        # Sin umbrales configurados — usar lógica por defecto
        if score_total <= 20:
            return RIESGO_BAJO
        elif score_total <= 50:
            return RIESGO_MEDIO
        else:
            return RIESGO_ALTO

    # Un score inferior al primer umbral representa un perfil aún más favorable.
    # No debe caer en el fallback de alto riesgo solo por ser negativo.
    primer_umbral = min(umbrales, key=lambda u: float(u.score_min))
    if score_total < float(primer_umbral.score_min):
        return primer_umbral.nivel

    # Si excede todos los umbrales → alto riesgo
    return RIESGO_ALTO


def resumen_presentacion(clasificacion: str) -> dict:
    """Expone la relación entre cumplimiento y nivel de riesgo sin cambiar el cálculo.

    El Core conserva el nivel de riesgo original en ``clasificacion``. La interfaz
    muestra además la lectura de cumplimiento: un riesgo bajo implica cumplimiento
    alto y una decisión favorable; un riesgo alto implica cumplimiento bajo.
    """
    datos = {
        RIESGO_BAJO: {
            "cumplimiento": "alto",
            "nivel_riesgo": "bajo",
            "decision": "favorable",
        },
        RIESGO_MEDIO: {
            "cumplimiento": "medio",
            "nivel_riesgo": "medio",
            "decision": "con observaciones",
        },
        RIESGO_ALTO: {
            "cumplimiento": "bajo",
            "nivel_riesgo": "alto",
            "decision": "desfavorable",
        },
    }
    return datos.get(clasificacion, datos[RIESGO_ALTO]).copy()
