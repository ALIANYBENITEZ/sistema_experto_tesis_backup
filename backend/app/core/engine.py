"""
Motor de Scoring — Orquestador Principal
==========================================
Ejecuta el flujo completo de evaluación:

  1. Obtener modelo activo
  2. Determinar tipo de persona (PF/PJ)
  3. Filtrar factores aplicables
  4. Obtener valor de cada factor
  5. Validar valor
  6. Evaluar regla
  7. Determinar nivel y peso
  8. Calcular score total
  9. Clasificar riesgo
  10. Generar explicación
  11. Retornar resultado completo
"""
from .schemas import (
    TIPO_PF, TIPO_PJ, TIPO_AMBOS,
    ESTADO_EVALUADO, ESTADO_SIN_DATO, ESTADO_NO_APLICA, ESTADO_INVALIDO,
)
from .validator import validar_valor
from .evaluator import evaluar_factor
from .classifier import clasificar_riesgo
from .explainer import generar_explicacion_global, identificar_factores_impacto


def ejecutar_evaluacion(modelo, datos_cliente: dict, tipo_persona: str, cliente_obj=None) -> dict:
    """
    Ejecuta la evaluación completa de un cliente contra un modelo de scoring.

    Args:
        modelo: instancia de ModeloScoring con factores y reglas cargados.
        datos_cliente: dict con {codigo_factor: valor, ...}
        tipo_persona: "PF" o "PJ"
        cliente_obj: (opcional) instancia de Client para verificación automática de lista negra

    Returns:
        {
            "score_total": float,
            "clasificacion": str,           # bajo/medio/alto
            "explicacion": str,             # texto global
            "factores_evaluados": int,
            "factores_sin_dato": int,
            "estado": str,                  # completa/incompleta
            "detalles": [...],              # resultado por factor
            "impacto": {...},               # factores agrupados por impacto
            "modelo_version": str,
        }
    """
    # Verificación automática contra lista negra ONU
    resultado_lista_negra = None
    if cliente_obj:
        from .lista_negra_checker import verificar_lista_negra
        resultado_lista_negra = verificar_lista_negra(
            nombre=cliente_obj.nombre,
            apellido=cliente_obj.apellido,
            num_doc=cliente_obj.num_doc,
        )
        # Auto-completar el factor en_lista_negra
        if resultado_lista_negra["en_lista"]:
            datos_cliente["en_lista_negra"] = True
        else:
            datos_cliente.setdefault("en_lista_negra", False)

    # PASO 1: Obtener factores activos del modelo
    factores = modelo.factores.filter_by(activo=True).order_by("orden").all()

    if not factores:
        return {
            "score_total": 0,
            "clasificacion": "alto",
            "explicacion": "No hay factores configurados en el modelo de scoring.",
            "factores_evaluados": 0,
            "factores_sin_dato": 0,
            "estado": "incompleta",
            "detalles": [],
            "impacto": {"desfavorables": [], "favorables": [], "neutros": [], "sin_dato": []},
            "modelo_version": modelo.version,
        }

    # PASO 2: Filtrar factores según tipo de persona
    factores_aplicables = [
        f for f in factores
        if f.tipo_persona == TIPO_AMBOS or f.tipo_persona == tipo_persona
    ]

    detalles = []
    score_total = 0.0
    factores_evaluados = 0
    factores_sin_dato = 0

    # PASO 3-10: Evaluar cada factor
    for factor in factores_aplicables:
        # Obtener valor del cliente
        valor_raw = datos_cliente.get(factor.codigo)

        # Validar
        validacion = validar_valor(valor_raw, factor)

        if validacion["estado"] == ESTADO_SIN_DATO:
            # Factor sin dato
            factores_sin_dato += 1
            detalle = {
                "factor_codigo": factor.codigo,
                "factor_nombre": factor.nombre,
                "categoria": factor.categoria,
                "valor_original": None,
                "estado": ESTADO_SIN_DATO,
                "regla_aplicada": None,
                "nivel": None,
                "peso": 0,
                "explicacion": f"No se proporcionó información para '{factor.nombre}'."
                               + (" Este factor es obligatorio." if factor.obligatorio else ""),
            }
            detalles.append(detalle)
            continue

        if validacion["estado"] == ESTADO_INVALIDO:
            # Dato inválido
            detalle = {
                "factor_codigo": factor.codigo,
                "factor_nombre": factor.nombre,
                "categoria": factor.categoria,
                "valor_original": str(valor_raw),
                "estado": ESTADO_INVALIDO,
                "regla_aplicada": None,
                "nivel": None,
                "peso": 0,
                "explicacion": validacion["error"],
            }
            detalles.append(detalle)
            continue

        # Evaluar regla
        resultado_regla = evaluar_factor(factor, validacion["valor_normalizado"])

        # Acumular score
        peso = resultado_regla["peso"]
        score_total += peso
        factores_evaluados += 1

        detalle = {
            "factor_codigo": factor.codigo,
            "factor_nombre": factor.nombre,
            "categoria": factor.categoria,
            "valor_original": str(valor_raw),
            "estado": ESTADO_EVALUADO,
            "regla_aplicada": resultado_regla["regla_aplicada"],
            "nivel": resultado_regla["nivel"],
            "peso": peso,
            "explicacion": resultado_regla["explicacion"],
        }
        detalles.append(detalle)

    # PASO 11: Clasificar riesgo global
    clasificacion = clasificar_riesgo(score_total, list(modelo.umbrales))

    # FACTOR DETERMINANTE: Si está en lista negra → ALTO automáticamente
    if resultado_lista_negra and resultado_lista_negra["en_lista"]:
        clasificacion = "alto"

    # PASO 12: Generar explicación
    explicacion = generar_explicacion_global(detalles, clasificacion, score_total)

    # Si está en lista negra, agregar a la explicación
    if resultado_lista_negra and resultado_lista_negra["en_lista"]:
        explicacion = (
            "FACTOR DETERMINANTE: El cliente fue encontrado en listas de sanciones internacionales "
            "(ONU/OFAC). Esto determina automáticamente una clasificación de RIESGO ALTO "
            "independientemente del score obtenido en los demás factores. "
            "La operación NO debe ser aprobada bajo ninguna condición."
        )

    # PASO 13: Identificar factores de impacto
    impacto = identificar_factores_impacto(detalles)

    # PASO 14: Determinar estado
    obligatorios_sin_dato = sum(
        1 for d in detalles
        if d["estado"] == ESTADO_SIN_DATO and any(
            f.codigo == d["factor_codigo"] and f.obligatorio
            for f in factores_aplicables
        )
    )
    estado = "incompleta" if obligatorios_sin_dato > 0 else "completa"

    return {
        "score_total": round(score_total, 2),
        "clasificacion": clasificacion,
        "explicacion": explicacion,
        "factores_evaluados": factores_evaluados,
        "factores_sin_dato": factores_sin_dato,
        "estado": estado,
        "detalles": detalles,
        "impacto": impacto,
        "modelo_version": modelo.version,
        "lista_negra": resultado_lista_negra,
    }
