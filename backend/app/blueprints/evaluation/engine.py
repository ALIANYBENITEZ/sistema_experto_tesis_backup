"""
Motor de scoring para evaluación de clientes inmobiliarios.
Calcula un puntaje ponderado basado en los criterios configurados en BD.
"""
from app.models import Criterion


# Rangos para el resultado automático
RESULTADO_APROBADO   = "aprobado"
RESULTADO_OBSERVADO  = "observado"
RESULTADO_RECHAZADO  = "rechazado"

UMBRAL_APROBADO  = 70.0   # >= 70 → aprobado
UMBRAL_OBSERVADO = 50.0   # >= 50 → observado
                          # <  50 → rechazado


def calcular_puntaje(detalles: list[dict]) -> tuple[float, str]:
    """
    Recibe una lista de dicts: [{"criterio_id": X, "valor": Y}, ...]
    donde `valor` es el puntaje asignado (0-100) para ese criterio.

    Retorna (puntaje_total: float, resultado: str)
    puntaje_total está en escala 0-100 ponderada por el peso de cada criterio.
    """
    criterios = {c.id: c for c in Criterion.query.filter_by(activo=True).all()}

    if not criterios:
        return 0.0, RESULTADO_RECHAZADO

    peso_total   = sum(float(c.peso) for c in criterios.values())
    puntaje_sum  = 0.0

    for detalle in detalles:
        cid   = detalle.get("criterio_id")
        valor = float(detalle.get("valor", 0))
        valor = max(0.0, min(100.0, valor))  # clamp 0-100

        criterio = criterios.get(cid)
        if not criterio:
            continue

        peso        = float(criterio.peso)
        puntaje_sum += (valor * peso)

    if peso_total == 0:
        return 0.0, RESULTADO_RECHAZADO

    puntaje_total = round(puntaje_sum / peso_total, 2)

    if puntaje_total >= UMBRAL_APROBADO:
        resultado = RESULTADO_APROBADO
    elif puntaje_total >= UMBRAL_OBSERVADO:
        resultado = RESULTADO_OBSERVADO
    else:
        resultado = RESULTADO_RECHAZADO

    return puntaje_total, resultado
