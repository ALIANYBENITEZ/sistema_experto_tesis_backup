"""
Clasificador de riesgo global.
Determina la clasificación final basándose en el score total y los umbrales configurados.
"""
from .schemas import RIESGO_BAJO, RIESGO_MEDIO, RIESGO_ALTO


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

    # Si excede todos los umbrales → alto riesgo
    return RIESGO_ALTO
