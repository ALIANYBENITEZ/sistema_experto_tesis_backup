# -*- coding: utf-8 -*-
"""
Genera el documento Word "Validacion Tecnica del Scoring" para la tesis.
Toda la logica, pesos, umbrales y reglas provienen del codigo real del sistema:
  - backend/app/blueprints/evaluation/engine.py   (criterios ponderados 0-100)
  - backend/app/blueprints/scoring/engine.py       (motor IF-THEN, umbrales 75/50)
  - backend/migrations/03_scoring_module.sql       (10 reglas sembradas, pesos reales)
  - backend/migrations/02_database_complete.sql    (5 criterios, pesos 25/25/20/15/15)
  - backend/app/core/*                             (lista negra ONU/OFAC, clasificacion)
  - backend/app/models/scoring.py / auditoria.py   (trazabilidad)
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AZUL = RGBColor(0x1F, 0x3A, 0x5F)
AZUL_CLARO = RGBColor(0x2E, 0x5A, 0x8C)
GRIS = RGBColor(0x55, 0x55, 0x55)
VERDE = RGBColor(0x2E, 0x7D, 0x32)
AMBAR = RGBColor(0xB8, 0x86, 0x00)
ROJO = RGBColor(0xC6, 0x28, 0x28)

doc = Document()

# ---- estilos base ----
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15


def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def h(text, level=1, color=AZUL):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.color.rgb = color
        run.font.name = "Calibri"
    return p


def para(text, size=11, bold=False, italic=False, color=None, align=None, space_after=6):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p


def numbered(text):
    return doc.add_paragraph(text, style="List Number")


def tabla(headers, rows, header_bg="1F3A5F", col_widths=None, zebra=True):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, head in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(head)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)
        set_cell_bg(hdr[i], header_bg)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci, val in enumerate(row):
            cells[ci].text = ""
            p = cells[ci].paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(9.5)
            if zebra and ri % 2 == 1:
                set_cell_bg(cells[ci], "EEF2F7")
    if col_widths:
        for row in t.rows:
            for ci, w in enumerate(col_widths):
                row.cells[ci].width = Inches(w)
    return t


# ============================================================
# PORTADA
# ============================================================
titulo = doc.add_paragraph()
titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = titulo.add_run("VALIDACIÓN TÉCNICA DEL MOTOR DE SCORING")
r.bold = True
r.font.size = Pt(22)
r.font.color.rgb = AZUL

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("Sistema Experto de Evaluación de Riesgo Crediticio para Clientes Inmobiliarios")
r.font.size = Pt(13)
r.font.color.rgb = AZUL_CLARO
r.italic = True

doc.add_paragraph()
meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = meta.add_run("Documento de sustento para defensa de tesis\n")
r.font.size = Pt(11)
r.font.color.rgb = GRIS
r = meta.add_run("Herramienta de apoyo a la toma de decisiones")
r.font.size = Pt(11)
r.font.color.rgb = GRIS
r.italic = True

doc.add_paragraph()

# Caja de aviso (herramienta de apoyo)
box = doc.add_table(rows=1, cols=1)
box.style = "Table Grid"
c = box.rows[0].cells[0]
set_cell_bg(c, "FFF8E1")
c.text = ""
pb = c.paragraphs[0]
rb = pb.add_run("AVISO METODOLÓGICO IMPORTANTE")
rb.bold = True
rb.font.color.rgb = AMBAR
rb.font.size = Pt(11)
pb2 = c.add_paragraph()
rb2 = pb2.add_run(
    "El sistema genera una recomendación o clasificación de riesgo destinada a APOYAR la toma de "
    "decisiones del evaluador humano. No sustituye el criterio del analista ni constituye una "
    "aprobación o rechazo automático y definitivo. La decisión final siempre corresponde a un "
    "usuario responsable, quien puede ratificar, observar o rechazar la recomendación. Toda la "
    "lógica aplicada queda registrada y es trazable (reglas usadas, valores evaluados, puntaje, "
    "clasificación y usuario que realizó la evaluación)."
)
rb2.font.size = Pt(10)

doc.add_page_break()

# ============================================================
# 0. INTRODUCCIÓN Y ARQUITECTURA
# ============================================================
h("1. Introducción y arquitectura de evaluación", 1)
para(
    "El sistema implementa un enfoque de doble capa para evaluar el riesgo crediticio de un cliente "
    "que solicita una operación inmobiliaria. Ambas capas son complementarias y responden a las "
    "preguntas de validación técnica planteadas: qué variables se usan, por qué, cómo se ponderan, "
    "cómo operan las reglas IF-THEN, cuáles son determinantes, cómo se calculan los umbrales, cómo se "
    "obtiene la clasificación final, quién validó el conocimiento y cómo se probaron las reglas."
)

h("1.1 Las dos capas del modelo", 2)
tabla(
    ["Capa", "Mecanismo", "Resultado", "Uso"],
    [
        ["A. Evaluación por Criterios Ponderados",
         "Media ponderada de 5 criterios (escala 0–100) por su peso porcentual",
         "Puntaje 0–100 → aprobado / observado / rechazado",
         "Valoración cualitativa integral del cliente"],
        ["B. Motor de Inferencia IF-THEN",
         "Sistema experto basado en reglas con puntos, reglas determinantes y lista negra",
         "Score sobre puntaje máximo → bajo / medio / alto / rechazado",
         "Evaluación objetiva y auditable regla por regla"],
    ],
    col_widths=[1.7, 2.6, 1.6, 1.5],
)
para(
    "La capa A ofrece una lectura ponderada y comprensible para el negocio; la capa B aporta la "
    "trazabilidad formal de un sistema experto (cada condición queda registrada como cumplida o no). "
    "La clasificación de riesgo final del sistema experto proviene de la capa B, que es la que admite "
    "reglas determinantes y verificación contra listas de sanciones.",
    italic=True, color=GRIS,
)

# ============================================================
# 2. MATRIZ DE RIESGO - CRITERIOS PONDERADOS (CAPA A)
# ============================================================
h("2. Matriz de riesgo: criterios ponderados", 1)
para(
    "La matriz de criterios define las dimensiones de evaluación y el peso relativo de cada una. "
    "Los pesos suman 100 % y están configurados en la base de datos (tabla criterios). Estos son los "
    "valores reales sembrados en el sistema:"
)

tabla(
    ["#", "Criterio", "Peso", "Qué mide"],
    [
        ["1", "Capacidad de Pago", "25 %",
         "Relación entre la cuota mensual estimada y el ingreso neto. Ratio máximo aceptable: 40 %."],
        ["2", "Historial Crediticio", "25 %",
         "Antecedentes financieros: deudas anteriores, moras y calificación en centrales de riesgo."],
        ["3", "Estabilidad Laboral", "20 %",
         "Tiempo en el empleo actual, tipo de contrato y sector económico."],
        ["4", "Documentación", "15 %",
         "Completitud y validez de documentos: DNI, boletas, declaración jurada, etc."],
        ["5", "Patrimonio", "15 %",
         "Bienes, activos y propiedades declaradas que respaldan la operación."],
        ["", "TOTAL", "100 %", "Media ponderada normalizada a escala 0–100."],
    ],
    col_widths=[0.4, 1.8, 0.7, 3.6],
)

h("2.1 Por qué estos pesos (justificación)", 2)
para(
    "La jerarquía de pesos refleja la práctica estándar de evaluación crediticia, donde la capacidad "
    "efectiva de repago y el comportamiento de pago histórico son los predictores de mayor peso, "
    "seguidos de la estabilidad de la fuente de ingreso y, finalmente, de factores de respaldo "
    "documental y patrimonial:"
)
bullet("concentran el mayor riesgo de impago directo; por eso reciben el peso máximo (25 % cada uno).",
       "Capacidad de Pago e Historial Crediticio: ")
bullet("mide la permanencia y previsibilidad del ingreso; peso intermedio (20 %).",
       "Estabilidad Laboral: ")
bullet("son factores de respaldo y verificación, no de capacidad de pago en sí; por eso reciben el peso menor (15 % cada uno).",
       "Documentación y Patrimonio: ")

h("2.2 Fórmula del puntaje ponderado", 2)
para("El cálculo está implementado en blueprints/evaluation/engine.py. Cada criterio recibe un valor "
     "entre 0 y 100 (con recorte o clamp a ese rango) y se combina así:")
form = doc.add_paragraph()
form.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf = form.add_run("puntaje_total = Σ (valor_criterio × peso_criterio) / Σ (pesos)")
rf.bold = True
rf.font.size = Pt(12)
rf.font.color.rgb = AZUL
para("El resultado es un número de 0 a 100 que luego se traduce a una recomendación mediante umbrales.",
     space_after=10)

h("2.3 Umbrales de la capa de criterios", 2)
tabla(
    ["Puntaje ponderado", "Resultado", "Lectura"],
    [
        ["≥ 70", "APROBADO", "Perfil satisfactorio"],
        ["≥ 50 y < 70", "OBSERVADO", "Requiere condiciones o documentación adicional"],
        ["< 50", "RECHAZADO", "No cumple el mínimo exigido"],
    ],
    col_widths=[1.8, 1.6, 3.1],
)

# ============================================================
# 3. VARIABLES DEL MOTOR IF-THEN (CAPA B)
# ============================================================
h("3. Variables del motor de inferencia (IF-THEN)", 1)
para(
    "El motor experto evalúa variables objetivas y medibles del cliente. Estas variables (parámetros) "
    "están definidas en el modelo Regla.PARAMETROS y sus valores se almacenan en la tabla "
    "historial_crediticio. La variable edad se calcula en tiempo de ejecución a partir de la fecha de "
    "nacimiento del cliente."
)
tabla(
    ["Variable", "Tipo", "Descripción / dominio"],
    [
        ["ingresos_mensuales", "numérico", "Ingresos mensuales del cliente"],
        ["edad", "numérico", "Edad en años (calculada por fecha de nacimiento)"],
        ["nivel_endeudamiento", "numérico (%)", "Relación deuda / ingreso"],
        ["meses_empleo_actual", "numérico", "Antigüedad laboral en meses"],
        ["cantidad_atrasos", "numérico", "Número de atrasos registrados"],
        ["deuda_total_sistema", "numérico", "Deuda total en el sistema financiero"],
        ["score_externo", "numérico", "Score en centrales de riesgo externas"],
        ["historial_pagos", "texto", "bueno / regular / malo / sin_historial"],
        ["en_lista_negra", "booleano", "Coincidencia en listas OFAC / ONU"],
        ["tipo_empleo", "texto", "dependiente / independiente / desempleado"],
        ["referencias_personales", "texto", "buenas / regulares / malas / no_verificadas"],
    ],
    col_widths=[2.0, 1.1, 3.4],
)

h("3.1 Por qué fueron elegidas estas variables", 2)
para(
    "Las variables cubren las tres dimensiones clásicas del riesgo de crédito y se relacionan "
    "directamente con la propuesta de valor del negocio (reducir morosidad y decidir de forma "
    "consistente):"
)
bullet("ingresos_mensuales, nivel_endeudamiento, deuda_total_sistema. Responden a si el cliente puede sostener la obligación.",
       "Capacidad de pago: ")
bullet("historial_pagos, cantidad_atrasos, score_externo. Comportamiento financiero pasado como predictor del futuro.",
       "Comportamiento crediticio: ")
bullet("meses_empleo_actual, tipo_empleo, referencias_personales. Previsibilidad y respaldo del ingreso.",
       "Estabilidad y respaldo: ")
bullet("edad (capacidad legal de contratar) y en_lista_negra (cumplimiento normativo antilavado).",
       "Elegibilidad y cumplimiento: ")

# ============================================================
# 4. REGLAS IF-THEN
# ============================================================
h("4. Reglas IF-THEN del sistema experto", 1)
para(
    "Cada regla es una condición atómica de la forma SI (parámetro operador valor_referencia) "
    "ENTONCES sumar peso_puntos. Las reglas se evalúan en orden; las no determinantes acumulan puntos "
    "cuando se cumplen y las determinantes, si fallan, provocan el rechazo inmediato. El motor soporta "
    "los operadores >=, <=, ==, >, < y !=."
)
para("Motor sembrado: \"Plantilla Estándar Inmobiliaria\" (versión 1.0), con 10 reglas y un puntaje "
     "máximo de 1000 puntos:", bold=True)

tabla(
    ["#", "Regla (SI...)", "Condición", "Puntos", "Determinante"],
    [
        ["1", "Sin antecedentes en lista negra", "en_lista_negra == false", "100", "SÍ"],
        ["2", "Edad mínima requerida", "edad >= 21", "50", "SÍ"],
        ["3", "Ingresos mínimos", "ingresos_mensuales >= 3.000.000", "150", "No"],
        ["4", "Nivel de endeudamiento aceptable", "nivel_endeudamiento <= 40", "120", "No"],
        ["5", "Deuda total controlada", "deuda_total_sistema <= 50.000.000", "100", "No"],
        ["6", "Historial de pagos bueno", "historial_pagos == bueno", "130", "No"],
        ["7", "Sin atrasos registrados", "cantidad_atrasos == 0", "100", "No"],
        ["8", "Antigüedad laboral mínima", "meses_empleo_actual >= 6", "80", "No"],
        ["9", "Score externo aceptable", "score_externo >= 500", "120", "No"],
        ["10", "Referencias verificadas", "referencias_personales != malas", "50", "No"],
        ["", "PUNTAJE MÁXIMO", "", "1000", ""],
    ],
    col_widths=[0.35, 2.0, 2.2, 0.7, 1.0],
)

h("4.1 Cómo se asignan los pesos de las reglas", 2)
para(
    "El peso en puntos de cada regla refleja su relevancia marginal en la decisión de riesgo. Las "
    "reglas de capacidad de pago e historial reciben los pesos más altos (150, 130, 120), coherente "
    "con la matriz de criterios ponderados de la sección 2, mientras que factores de respaldo "
    "(antigüedad, referencias) reciben pesos menores (80, 50). Las reglas determinantes llevan además "
    "la marca de exclusión, independiente de su aporte en puntos."
)

h("4.2 Reglas determinantes", 2)
para(
    "Una regla determinante es una condición excluyente: si no se cumple, el motor corta la evaluación "
    "(break) y clasifica al cliente como RECHAZADO con porcentaje 0, sin importar los puntos "
    "acumulados en las demás reglas. El identificador de la regla que provocó el rechazo se guarda "
    "en el campo regla_determinante_id de la evaluación, para trazabilidad."
)
bullet("el cliente no debe aparecer en listas de sanciones OFAC / ONU (cumplimiento normativo).",
       "Regla 1 — Sin antecedentes en lista negra: ")
bullet("edad >= 21 años, requisito de capacidad legal para contratar.",
       "Regla 2 — Edad mínima requerida: ")

h("4.3 Verificación automática contra lista negra (ONU / OFAC)", 2)
para(
    "El núcleo del sistema (core/lista_negra_checker.py) verifica automáticamente al cliente contra la "
    "lista de sanciones usando coincidencia parcial por nombre, apellido y número de documento. "
    "Asigna un puntaje de confianza al match:"
)
tabla(
    ["Tipo de coincidencia", "Confianza", "Nivel de alerta"],
    [
        ["Documento de identidad / pasaporte", "100", "confirmado"],
        ["Nombre y apellido exactos", "100 (50+50)", "confirmado"],
        ["Coincidencia alta (≥ 80)", "≥ 80", "confirmado"],
        ["Coincidencia parcial (≥ 50)", "50–79", "posible"],
        ["Sin coincidencia significativa", "< 50", "ninguno"],
    ],
    col_widths=[2.6, 1.4, 1.5],
)
para(
    "Si la verificación resulta positiva, la clasificación de riesgo se fuerza a ALTO / rechazo "
    "automáticamente y se registra el motivo en la explicación. Es el factor determinante de mayor "
    "jerarquía del sistema.",
    italic=True, color=ROJO,
)

# ============================================================
# 5. CÁLCULO DE UMBRALES Y CLASIFICACIÓN FINAL
# ============================================================
h("5. Cálculo de umbrales y clasificación final", 1)
para(
    "El motor IF-THEN calcula el porcentaje de puntaje obtenido respecto del puntaje máximo posible y "
    "lo compara contra umbrales fijos. La elección de un modelo relativo (porcentaje) permite que los "
    "umbrales se mantengan válidos aunque se agreguen o modifiquen reglas."
)
form2 = doc.add_paragraph()
form2.alignment = WD_ALIGN_PARAGRAPH.CENTER
rf2 = form2.add_run("porcentaje = (score_obtenido / score_máximo) × 100")
rf2.bold = True
rf2.font.size = Pt(12)
rf2.font.color.rgb = AZUL

tabla(
    ["Condición", "Porcentaje", "Puntos (sobre 1000)", "Clasificación", "Decisión de apoyo"],
    [
        ["Regla determinante fallida", "—", "—", "RECHAZADO", "Rechazado (excluyente)"],
        ["porcentaje ≥ 75 %", "≥ 75 %", "≥ 750", "BAJO", "FAVORABLE"],
        ["50 % ≤ porcentaje < 75 %", "50–74 %", "500–749", "MEDIO", "CON OBSERVACIONES"],
        ["porcentaje < 50 %", "< 50 %", "< 500", "ALTO", "DESFAVORABLE"],
    ],
    col_widths=[1.9, 0.9, 1.3, 1.1, 1.4],
)

h("5.1 Cómo se obtiene la clasificación final (orden de decisión)", 2)
numbered("Verificación de lista negra: si el cliente aparece en listas OFAC/ONU → ALTO / rechazo inmediato.")
numbered("Reglas determinantes: si alguna falla (lista negra o edad < 21) → RECHAZADO.")
numbered("Si supera lo anterior, se suman los puntos de las reglas cumplidas y se calcula el porcentaje.")
numbered("El porcentaje se compara con los umbrales 75 % y 50 % para asignar bajo, medio o alto riesgo.")
numbered("Se genera una recomendación (FAVORABLE / CON OBSERVACIONES / DESFAVORABLE / RECHAZADO) con acciones sugeridas.")
para(
    "La clasificación resultante es una recomendación de apoyo. El evaluador humano decide si la "
    "ratifica, la observa o la rechaza, y esa decisión queda registrada.",
    italic=True, color=GRIS,
)

# ============================================================
# 6. TRAZABILIDAD Y AUDITORÍA
# ============================================================
h("6. Trazabilidad y auditoría", 1)
para(
    "Para cumplir con el principio de herramienta de apoyo a la decisión, el sistema conserva evidencia "
    "completa de cada evaluación. La lógica aplicada queda registrada y es reconstruible."
)

h("6.1 Qué se registra por cada evaluación", 2)
tabla(
    ["Elemento registrado", "Dónde se almacena", "Detalle"],
    [
        ["Reglas utilizadas y resultado", "resultado_detalle", "Por cada regla: cumplida (sí/no), parámetro, operador, valor de referencia, puntos"],
        ["Valores evaluados", "resultado_detalle.valor_evaluado", "Valor real del cliente al momento de evaluar"],
        ["Puntaje obtenido", "evaluacion_riesgo.score_final / score_maximo", "Puntos logrados y máximo posible"],
        ["Clasificación", "evaluacion_riesgo.categoria_riesgo", "bajo / medio / alto / rechazado"],
        ["Regla determinante que rechazó", "evaluacion_riesgo.regla_determinante_id", "Identifica la causa exacta del rechazo"],
        ["Usuario que evaluó", "evaluacion_riesgo.usuario_id", "Responsable de la ejecución"],
        ["Fecha y hora", "evaluacion_riesgo.fecha_analisis", "Momento de la evaluación"],
        ["Datos de la operación", "detalle_operacion", "Tipo de propiedad, valor, monto, plazo, destino"],
    ],
    col_widths=[1.9, 2.1, 2.6],
)

h("6.2 Bitácora de auditoría centralizada", 2)
para(
    "Adicionalmente, la tabla auditoria registra los eventos del sistema (incluido el tipo "
    "EVALUACIONES) con usuario, nombre, módulo, entidad, registro afectado, resultado (ÉXITO/FALLO), "
    "IP, valores anteriores y nuevos, y marca de tiempo. Existen además disparadores (triggers) SQL "
    "que insertan registros de auditoría de forma automática. Esto garantiza trazabilidad incluso ante "
    "cambios de configuración de reglas o criterios."
)

# ============================================================
# 7. VALIDACIÓN DEL CONOCIMIENTO Y PRUEBAS
# ============================================================
h("7. Validación del conocimiento y pruebas de reglas", 1)

h("7.1 Quién validó el conocimiento", 2)
para(
    "El conocimiento codificado (variables, umbrales y pesos) se fundamenta en prácticas estándar de "
    "evaluación de riesgo crediticio y en criterios de negocio del sector inmobiliario. Para la defensa "
    "se recomienda documentar explícitamente la fuente de validación con los responsables reales del "
    "proyecto. Completar la siguiente tabla:"
)
tabla(
    ["Elemento de conocimiento", "Fuente / criterio", "Validado por"],
    [
        ["Pesos de criterios (25/25/20/15/15)", "Práctica de underwriting crediticio", "[Experto de negocio / asesor]"],
        ["Ratio de endeudamiento 40 %", "Umbral prudencial de capacidad de pago", "[Analista de crédito]"],
        ["Edad mínima 21 años", "Capacidad legal de contratar", "[Área legal]"],
        ["Lista negra OFAC/ONU", "Cumplimiento antilavado", "[Oficial de cumplimiento]"],
        ["Umbrales 75 % / 50 %", "Calibración del modelo de riesgo", "[Equipo del proyecto]"],
    ],
    col_widths=[2.3, 2.3, 2.0],
)

h("7.2 Cómo se probaron las reglas", 2)
para("La validación de un sistema experto basado en reglas se apoya en completitud, consistencia y "
     "contraste con el juicio experto. Procedimiento recomendado y aplicable al sistema:")
bullet("verificar que no existan reglas contradictorias ni redundantes y que cada regla sea alcanzable.",
       "Verificación de consistencia: ")
bullet("confirmar que todo valor posible de cada variable active alguna regla (incluye el fallback de seguridad a riesgo alto cuando ningún caso coincide).",
       "Verificación de completitud: ")
bullet("ejecutar casos límite en cada umbral (p. ej. endeudamiento = 40 %, edad = 21, porcentaje = 75 %) para confirmar el comportamiento esperado.",
       "Pruebas de frontera: ")
bullet("evaluar perfiles sintéticos (bajo, medio, alto y rechazado) y comparar la salida del sistema con la decisión de un evaluador humano.",
       "Casos de prueba por categoría: ")

h("7.3 Casos de prueba de ejemplo", 2)
para("Perfiles de validación recomendados con el motor sembrado (puntaje máximo 1000):")
tabla(
    ["Perfil", "Puntos esperados", "%", "Clasificación esperada"],
    [
        ["Cliente ideal (cumple reglas 1–10)", "1000", "100 %", "BAJO (FAVORABLE)"],
        ["Buen cliente con 1–2 observaciones", "750–900", "75–90 %", "BAJO"],
        ["Cliente con varias carencias", "500–740", "50–74 %", "MEDIO"],
        ["Cliente de alto riesgo", "< 500", "< 50 %", "ALTO"],
        ["Cliente en lista negra o menor de 21", "—", "—", "RECHAZADO (determinante)"],
    ],
    col_widths=[2.6, 1.3, 0.7, 1.8],
)

# ============================================================
# 8. RELACIÓN CON EL MODELO DE NEGOCIO
# ============================================================
h("8. Relación con la propuesta de valor (modelo de negocio)", 1)
para(
    "Las variables técnicas se vinculan directamente con la propuesta de valor del sistema para la "
    "inmobiliaria: decisiones más rápidas, consistentes y defendibles, con menor exposición a la "
    "morosidad."
)
tabla(
    ["Variable del scoring", "Propuesta de valor"],
    [
        ["Ingresos y endeudamiento", "Reduce el riesgo de impago seleccionando clientes con capacidad real de pago"],
        ["Historial y score externo", "Aprovecha comportamiento pasado para anticipar morosidad"],
        ["Estabilidad laboral", "Prioriza clientes con ingresos previsibles y sostenibles"],
        ["Lista negra OFAC/ONU", "Protege a la empresa frente a riesgos legales y de cumplimiento"],
        ["Trazabilidad y auditoría", "Decisiones defendibles y homogéneas entre evaluadores"],
    ],
    col_widths=[2.4, 4.2],
)

# ============================================================
# 9. REFERENCIAS BIBLIOGRÁFICAS
# ============================================================
h("9. Referencias y bibliografía de respaldo", 1)
para(
    "Las siguientes fuentes respaldan la metodología empleada: sistemas expertos basados en reglas y su "
    "validación, modelos de decisión multicriterio ponderados para crédito, y umbrales prudenciales de "
    "endeudamiento. (El contenido fue parafraseado para cumplir con las restricciones de licencia de las "
    "fuentes.)"
)

def ref(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    p.add_run(text)
    p.paragraph_format.space_after = Pt(8)
    return p

para("Sistemas expertos basados en reglas, verificación y validación del conocimiento", bold=True, color=AZUL_CLARO)
ref("González, A. J., Knauf, R. & Philippow, I. Towards Validation of Rule-Based Systems — The Loop is Closed. "
    "FLAIRS, AAAI. Disponible en: https://cdn.aaai.org/FLAIRS/2000/FLAIRS00-062.pdf")
ref("Framework for validation of rule-based systems: generación de un conjunto mínimo de casos de prueba y "
    "contraste tipo Turing con respuestas de expertos humanos. ResearchGate. "
    "https://www.researchgate.net/publication/5614094_A_framework_for_validation_of_rule-based_systems")
ref("Validation of Rule-Based Systems Generated by Classification Algorithms (verificación por completitud y "
    "consistencia mediante tablas de decisión). Springer. https://link.springer.com/doi/10.1007/978-1-4615-4851-5_42")
ref("Verification and Validation of a Knowledge-based System. ResearchGate. "
    "https://www.researchgate.net/publication/220633721_Verification_and_Validation_of_a_Knowledge-based_System")

para("Modelos de decisión multicriterio y scoring crediticio", bold=True, color=AZUL_CLARO)
ref("Synergetic Application of Multi-Criteria Decision-Making Models to Credit Granting Decision Problems. "
    "Applied Sciences (MDPI), 2019. https://www.mdpi.com/2076-3417/9/23/5052")
ref("Ziemba, P., Becker, J., Becker, A. & Radomska-Zalas, A. Framework for multi-criteria assessment of "
    "classification models for the purposes of credit scoring. Journal of Big Data, 2023. "
    "https://link.springer.com/doi/10.1186/s40537-023-00768-7")
ref("World Bank Group. Credit Scoring Approaches Guidelines, 2019. "
    "https://thedocs.worldbank.org/en/doc/935891585869698451-0130022020/original/CREDITSCORINGAPPROACHESGUIDELINESFINALWEB.pdf")

para("Umbrales de endeudamiento y capacidad de pago", bold=True, color=AZUL_CLARO)
ref("Investopedia. Debt-to-Income (DTI) Ratio: los prestamistas suelen preferir un DTI no mayor al 36 %, "
    "pudiendo extenderse en ciertos casos. https://www.investopedia.com/terms/d/dti.asp")
ref("Federal Reserve Bank of St. Louis. Sobre el umbral de 43 % de DTI establecido por la Dodd-Frank Act "
    "para los 'qualified mortgages'. https://www.stlouisfed.org/on-the-economy/2026/jun/"
    "what-30-million-applications-reveal-mortgage-denial-thresholds")
ref("Fannie Mae. Debt-to-Income Ratios (guía de suscripción). "
    "https://www.fanniemae.com/content/guide/selling/b3/6/02.html")

para(
    "Nota: el umbral de endeudamiento del sistema (40 %) se sitúa dentro del rango prudencial habitual "
    "de la industria (36 %–43 %), lo que respalda su elección como condición de capacidad de pago.",
    italic=True, color=GRIS,
)

# ---- pie ----
doc.add_paragraph()
pie = doc.add_paragraph()
pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
rp = pie.add_run("Documento generado a partir del código fuente real del sistema (motores de evaluación y scoring).")
rp.italic = True
rp.font.size = Pt(9)
rp.font.color.rgb = GRIS

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Validacion_Tecnica_Scoring.docx")
doc.save(out)
print("GENERADO:", out)
