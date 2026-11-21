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


def resumen_presentacion(clasificacion: str) -> dict:
    """Expone la relación entre cumplimiento y nivel de riesgo sin cambiar el cálculo.

    El Core conserva el valor original de ``clasificacion`` y la interfaz lo presenta
    como grado de cumplimiento. Por eso, una clasificación alta se muestra como
    riesgo bajo y una clasificación baja como riesgo alto.
    """
    datos = {
        RIESGO_BAJO: {
            "cumplimiento": "bajo",
            "nivel_riesgo": "alto",
            "decision": "desfavorable",
        },
        RIESGO_MEDIO: {
            "cumplimiento": "medio",
            "nivel_riesgo": "medio",
            "decision": "con observaciones",
        },
        RIESGO_ALTO: {
            "cumplimiento": "alto",
            "nivel_riesgo": "bajo",
            "decision": "favorable",
        },
    }
    return datos.get(clasificacion, datos[RIESGO_ALTO]).copy()
