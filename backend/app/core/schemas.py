"""
Constantes y tipos del Core de Scoring.
"""

# Tipos de persona
TIPO_PF = "PF"  # Persona Física
TIPO_PJ = "PJ"  # Persona Jurídica
TIPO_AMBOS = "AMBOS"

TIPOS_PERSONA = (TIPO_PF, TIPO_PJ, TIPO_AMBOS)

# Tipos de dato de un factor
TIPO_DATO_NUMERICO = "numerico"
TIPO_DATO_PORCENTAJE = "porcentaje"
TIPO_DATO_CATALOGO = "catalogo"
TIPO_DATO_BOOLEANO = "booleano"
TIPO_DATO_TEXTO = "texto"

TIPOS_DATO = (
    TIPO_DATO_NUMERICO, TIPO_DATO_PORCENTAJE,
    TIPO_DATO_CATALOGO, TIPO_DATO_BOOLEANO, TIPO_DATO_TEXTO,
)

# Niveles de riesgo por factor
NIVEL_BAJO = "bajo"
NIVEL_MEDIO = "medio"
NIVEL_ALTO = "alto"

NIVELES = (NIVEL_BAJO, NIVEL_MEDIO, NIVEL_ALTO)

# Clasificación global de riesgo
RIESGO_BAJO = "bajo"
RIESGO_MEDIO = "medio"
RIESGO_ALTO = "alto"

# Operadores para reglas
OPERADORES = (">=", "<=", "==", ">", "<", "!=", "entre", "en")

# Estado de factor en evaluación
ESTADO_EVALUADO = "evaluado"
ESTADO_SIN_DATO = "sin_dato"
ESTADO_NO_APLICA = "no_aplica"
ESTADO_INVALIDO = "invalido"
