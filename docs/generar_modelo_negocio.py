# -*- coding: utf-8 -*-
"""
Genera el apartado "Modelo de Negocio y Logica Operativa de la Solucion"
para el libro/tesis, con la estructura de 12 puntos indicada por el tutor.

Datos de negocio tomados de documentos reales del proyecto:
  - docs/modelo_costos_precios.md               (costos, precios, planes, punto de equilibrio)
  - docs/generar_flyer_canvas_actualizado.js    (Business Model Canvas: 9 bloques)
Logica tecnica tomada del codigo real (motor de scoring IF-THEN, criterios ponderados,
lista negra ONU/OFAC, trazabilidad), consistente con docs/Validacion_Tecnica_Scoring.docx.
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AZUL = RGBColor(0x10, 0x2A, 0x47)
AZUL_CLARO = RGBColor(0x2E, 0x5A, 0x8C)
GRIS = RGBColor(0x55, 0x55, 0x55)
ORO = RGBColor(0xB8, 0x86, 0x00)
VERDE = RGBColor(0x2E, 0x7D, 0x32)
ROJO = RGBColor(0xC6, 0x28, 0x28)

doc = Document()

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


def numbered(text, bold_prefix=None):
    p = doc.add_paragraph(style="List Number")
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p


def tabla(headers, rows, header_bg="102A47", col_widths=None, zebra=True):
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
# TÍTULO DEL APARTADO
# ============================================================
titulo = doc.add_paragraph()
r = titulo.add_run("Modelo de Negocio y Lógica Operativa de la Solución")
r.bold = True
r.font.size = Pt(20)
r.font.color.rgb = AZUL

para(
    "Este apartado se incorpora dentro de \"Modelado del Sistema\", después de la Arquitectura de "
    "Solución y antes del Marco Analítico. Describe el modelo comercial de la solución, su lógica "
    "operativa y la forma en que el sistema experto de scoring soporta ese modelo. La solución se "
    "presenta como una herramienta de apoyo a la decisión: genera una recomendación o clasificación "
    "de riesgo que respalda al evaluador humano, sin sustituir su criterio.",
    italic=True, color=GRIS,
)
para(
    "Nota: los montos económicos corresponden a hipótesis comerciales sujetas a validación con "
    "proveedores y con la encuesta de disposición a pagar. Tipo de cambio referencial: 1 USD ≈ Gs. 7.300.",
    size=9.5, italic=True, color=GRIS,
)

# ------------------------------------------------------------
# 1. DESCRIPCIÓN DEL MODELO COMERCIAL
# ------------------------------------------------------------
h("1. Descripción del modelo comercial", 1)
para(
    "La solución es un sistema web de evaluación de riesgo crediticio ofrecido a inmobiliarias bajo un "
    "modelo de suscripción mensual. La inmobiliaria contrata un plan mensual (Bronce, Plata u Oro) que "
    "le habilita una cantidad de evaluaciones/reportes de scoring por mes para los clientes que "
    "solicitan una operación inmobiliaria (alquiler, venta o financiamiento)."
)
para(
    "El modelo no vende licencias perpetuas ni cobra por usuario, sino que ofrece el servicio como una "
    "suscripción mensual asociada al volumen de evaluaciones. Esto da previsibilidad de ingreso al "
    "proveedor y de costo a la inmobiliaria, y reduce la barrera de entrada frente a una licencia única."
)
tabla(
    ["Atributo del modelo", "Definición"],
    [
        ["Tipo de solución", "Software como servicio (SaaS) web de scoring crediticio"],
        ["Mecanismo de cobro", "Suscripción mensual por planes (Bronce, Plata, Oro)"],
        ["Unidad de valor", "Una evaluación de riesgo con su reporte y clasificación"],
        ["Mercado objetivo", "Inmobiliarias de Asunción (Paraguay)"],
        ["Entrega", "Plataforma web (frontend React + backend Flask)"],
    ],
    col_widths=[2.2, 4.4],
)

# ------------------------------------------------------------
# 2. ACTORES DEL MODELO
# ------------------------------------------------------------
h("2. Actores del modelo: cliente, usuario, pagador y beneficiario", 1)
para(
    "El modelo distingue cuatro roles. Es importante separarlos porque quien usa el sistema, quien lo "
    "paga y quien se beneficia no siempre son la misma persona, y el cliente evaluado es externo a la "
    "operación comercial del software."
)
tabla(
    ["Actor", "Quién es", "Rol en el modelo"],
    [
        ["Cliente (comercial)", "La inmobiliaria",
         "Contrata la suscripción mensual y consume las evaluaciones del plan"],
        ["Usuario", "Administrador y operadores de la inmobiliaria",
         "Operan el sistema: registran clientes, ejecutan evaluaciones y consultan reportes"],
        ["Pagador", "La inmobiliaria",
         "Abona la cuota mensual del plan y, de ser necesario, las evaluaciones adicionales"],
        ["Beneficiario", "La inmobiliaria y, de forma indirecta, el solicitante evaluado",
         "La inmobiliaria decide con mayor rapidez, objetividad y respaldo; el proceso es más consistente"],
        ["Sujeto evaluado", "El solicitante (persona o empresa que pide la operación)",
         "No es cliente comercial: es el individuo sobre el que se calcula el riesgo"],
    ],
    col_widths=[1.5, 2.1, 3.0],
)
para(
    "En este modelo el cliente comercial, el usuario y el pagador coinciden en la figura de la "
    "inmobiliaria, mientras que el sujeto evaluado es un actor distinto cuyos datos alimentan el "
    "scoring.",
    italic=True, color=GRIS,
)

# ------------------------------------------------------------
# 3. PROBLEMA Y PROPUESTA DE VALOR
# ------------------------------------------------------------
h("3. Problema y propuesta de valor", 1)
h("3.1 Problema", 2)
bullet("La evaluación manual de un cliente toma entre 20 y 40 minutos y depende del criterio individual del analista.")
bullet("La valoración del riesgo es subjetiva e inconsistente entre evaluadores y entre casos.")
bullet("No existe trazabilidad formal de por qué se aprobó o rechazó a un cliente.")
bullet("No se verifica de forma sistemática a los solicitantes contra listas de sanciones (riesgo de cumplimiento).")

h("3.2 Propuesta de valor", 2)
para("El sistema automatiza y estandariza la evaluación de riesgo con un motor de reglas IF-THEN "
     "parametrizadas y verificación de cumplimiento, entregando una recomendación trazable:")
bullet("usa variables objetivas (ingresos, historial de pagos, endeudamiento, estabilidad laboral, entre otras) para calcular un puntaje y clasificar el riesgo en Alto, Medio o Bajo.",
       "Scoring automatizado: ")
bullet("verificación automática contra listas negras ONU/OFAC que bloquea evaluaciones con alertas de compliance. Es un diferenciador frente a una evaluación manual.",
       "Cumplimiento integrado: ")
bullet("reduce el tiempo de evaluación estimado de 20–40 min a 5–10 min (estimación sujeta a validación).",
       "Rapidez: ")
bullet("misma lógica aplicada a todos los casos, con registro de reglas usadas, valores, puntaje, clasificación y usuario.",
       "Objetividad y trazabilidad: ")
bullet("el sistema recomienda; el evaluador humano decide. No sustituye el juicio profesional.",
       "Apoyo a la decisión: ")

# ------------------------------------------------------------
# 4. LÓGICA OPERATIVA DEL MODELO
# ------------------------------------------------------------
h("4. Lógica operativa del modelo", 1)
para("La operación del modelo sigue un ciclo repetible que conecta la contratación comercial con el "
     "uso técnico del sistema:")
numbered("La inmobiliaria contrata un plan de suscripción mensual (Bronce, Plata u Oro) a través de la pasarela de pago.")
numbered("Se habilitan los usuarios autorizados (administrador y operadores) en la plataforma.")
numbered("Ante una solicitud, el usuario registra al cliente y sus datos financieros.")
numbered("El sistema ejecuta el motor de scoring: verifica lista negra, evalúa las reglas y calcula el puntaje.")
numbered("Se genera un reporte con la clasificación de riesgo y una recomendación de apoyo.")
numbered("El evaluador humano toma la decisión final y esta queda registrada con trazabilidad completa.")
numbered("Cada evaluación descuenta un reporte del cupo mensual del plan; al agotarlo, se renueva en el siguiente ciclo o se adquieren adicionales.")
para(
    "De este modo, el consumo técnico (evaluaciones) y la suscripción mensual contratada avanzan en "
    "paralelo, lo que hace medible y previsible el modelo de ingresos recurrentes.",
    italic=True, color=GRIS,
)

# ------------------------------------------------------------
# 5. REGLAS PRINCIPALES DEL NEGOCIO
# ------------------------------------------------------------
h("5. Reglas principales del negocio", 1)
para("Las reglas de negocio gobiernan tanto la operación comercial como la lógica de evaluación. Se "
     "distinguen reglas comerciales y reglas de evaluación.")

h("5.1 Reglas comerciales", 2)
bullet("El acceso al servicio requiere una suscripción mensual vigente con cupo de reportes disponible.")
bullet("Cada evaluación ejecutada consume un (1) reporte del cupo mensual del plan.")
bullet("Si se agota el cupo del mes, pueden adquirirse evaluaciones/reportes adicionales.")
bullet("A mayor plan contratado, menor precio unitario por reporte (descuento por volumen).")

h("5.2 Reglas de evaluación (sistema experto)", 2)
para("La lógica técnica se basa en reglas IF-THEN con pesos, reglas determinantes y umbrales. Estas "
     "son las reglas de mayor jerarquía del negocio:")
bullet("si el solicitante aparece en listas de sanciones ONU/OFAC, la evaluación se clasifica como riesgo ALTO y la operación no debe aprobarse (regla determinante y excluyente).",
       "Cumplimiento: ")
bullet("el solicitante debe tener al menos 21 años (capacidad legal de contratar); de lo contrario, rechazo.",
       "Elegibilidad: ")
bullet("la relación deuda/ingreso no debe superar el 40 %, umbral prudencial de capacidad de pago.",
       "Capacidad de pago: ")
bullet("la clasificación final se obtiene del porcentaje de puntaje alcanzado: ≥ 75 % riesgo bajo, 50–74 % riesgo medio, < 50 % riesgo alto.",
       "Clasificación: ")
para("El detalle numérico de pesos, puntajes y umbrales se desarrolla en el apartado de Validación "
     "Técnica del Scoring.", size=9.5, italic=True, color=GRIS)

# ------------------------------------------------------------
# 6. FLUJO DE VALOR
# ------------------------------------------------------------
h("6. Flujo de valor", 1)
para("El flujo de valor describe cómo la solución transforma datos del solicitante en una decisión de "
     "negocio con menor riesgo:")
tabla(
    ["Etapa", "Entrada", "Transformación", "Salida de valor"],
    [
        ["1. Captura", "Datos del solicitante", "Registro estructurado en la plataforma", "Expediente digital del cliente"],
        ["2. Verificación", "Nombre, documento", "Cotejo contra listas ONU/OFAC", "Alerta de cumplimiento (si aplica)"],
        ["3. Evaluación", "Variables financieras", "Motor de reglas IF-THEN + puntaje", "Score y clasificación de riesgo"],
        ["4. Recomendación", "Clasificación", "Mapeo a decisión de apoyo", "Reporte: favorable / observado / desfavorable"],
        ["5. Decisión", "Reporte + criterio", "Juicio del evaluador humano", "Decisión registrada y trazable"],
    ],
    col_widths=[1.2, 1.5, 2.0, 1.9],
)
para(
    "El valor entregado no es solo el puntaje, sino una decisión más rápida, consistente y defendible, "
    "con evidencia completa de la lógica aplicada.",
    italic=True, color=GRIS,
)

# ------------------------------------------------------------
# 7. CÓMO EL SISTEMA SOPORTA EL MODELO DE NEGOCIO
# ------------------------------------------------------------
h("7. Cómo el sistema soporta el modelo de negocio", 1)
tabla(
    ["Capacidad del sistema", "Elemento del modelo que soporta"],
    [
        ["Motor de reglas IF-THEN parametrizable", "Permite estandarizar el criterio y adaptarlo sin reprogramar"],
        ["Criterios ponderados configurables", "Traduce la propuesta de valor en una evaluación medible"],
        ["Verificación ONU/OFAC automática", "Sostiene el diferenciador de cumplimiento del negocio"],
        ["Gestión de usuarios y roles", "Habilita a los usuarios autorizados de la inmobiliaria (admin/operador)"],
        ["Reportes y dashboard", "Entrega el producto que la inmobiliaria consume y paga"],
        ["Auditoría y trazabilidad", "Garantiza decisiones defendibles y homogéneas (apoyo a la decisión)"],
        ["Consumo por evaluación", "Habilita el cobro por suscripción mensual y la medición del uso"],
    ],
    col_widths=[2.6, 4.0],
)

# ------------------------------------------------------------
# 8. ESTRUCTURA DE COSTOS
# ------------------------------------------------------------
h("8. Estructura de costos", 1)
para("Los costos se separan en inversión inicial única y costos recurrentes de operación.")

h("8.1 Inversión inicial (costo único de desarrollo)", 2)
tabla(
    ["Concepto", "Monto (Gs.)"],
    [
        ["Recursos humanos (500 h de desarrollo)", "5.000.000"],
        ["Hardware (laptop + smartphone de pruebas)", "4.300.000"],
        ["Software y licencias del período de desarrollo", "232.200"],
        ["Total inversión inicial", "9.532.200 (≈ US$ 1.306)"],
    ],
    col_widths=[4.4, 2.2],
)
para("Los gastos administrativos de la tesis (impresión, encuadernación, viáticos: Gs. 731.250) se "
     "consideran propios del trabajo académico y se excluyen del modelo comercial.",
     size=9.5, italic=True, color=GRIS)

h("8.2 Costos recurrentes (operación mensual)", 2)
tabla(
    ["Concepto", "Mensual (Gs.)", "Anual (Gs.)"],
    [
        ["Hosting backend (Render Starter)", "51.100", "613.200"],
        ["Base de datos PostgreSQL (Render)", "51.100", "613.200"],
        ["Frontend estático (Render Free)", "0", "0"],
        ["Dominio (prorrateado)", "~7.300", "~87.600"],
        ["Mantenimiento del motor de scoring", "~40.000", "~480.000"],
        ["Soporte técnico, seguridad y respaldos", "~30.000", "~360.000"],
        ["Subtotal fijo", "~179.600", "~2.154.000"],
    ],
    col_widths=[3.6, 1.5, 1.5],
)
bullet("comisión de la pasarela (Pagopar) por transacción, proporcional a las ventas; no integra el subtotal fijo.",
       "Costo variable: ")
bullet("el costo marginal de una evaluación adicional es casi nulo; el costo relevante es el fijo mensual repartido entre las evaluaciones vendidas (~Gs. 6.000 por evaluación en el escenario conservador de 30/mes).",
       "Costo por evaluación: ")

# ------------------------------------------------------------
# 9. MODELO DE INGRESOS Y SOSTENIBILIDAD
# ------------------------------------------------------------
h("9. Modelo de ingresos y sostenibilidad", 1)
para("Los ingresos provienen de suscripciones mensuales por planes, con descuento por volumen de "
     "reportes incluidos. Al tratarse de una cuota mensual, el ingreso es recurrente.")
tabla(
    ["Plan", "Reportes/mes", "Precio por reporte", "Cuota mensual", "Margen vs. piso (Gs. 6.000)"],
    [
        ["Bronce", "15", "Gs. 10.000", "Gs. 150.000 /mes", "40 %"],
        ["Plata", "30", "Gs. 9.000", "Gs. 270.000 /mes", "33 %"],
        ["Oro", "50", "Gs. 8.000", "Gs. 400.000 /mes", "25 %"],
    ],
    col_widths=[1.1, 1.1, 1.5, 1.6, 1.8],
)
para("Los precios se derivan de forma justificada: superan el piso de costo (Gs. 6.000 por evaluación) "
     "y quedan por debajo del techo de valor (una evaluación manual cuesta ~Gs. 10.000–15.000), con "
     "descuento por volumen coherente.")

h("9.1 Punto de equilibrio y sostenibilidad", 2)
para("Costo fijo mensual a cubrir: Gs. 179.600. Como el costo variable por evaluación es casi nulo, el "
     "margen de contribución ≈ precio del plan.")
tabla(
    ["Escenario", "Ingreso mensual", "Resultado"],
    [
        ["2 suscripciones Bronce", "Gs. 300.000", "Cubre el costo fijo"],
        ["1 suscripción Plata", "Gs. 270.000", "Cubre el costo fijo"],
        ["1 suscripción Oro", "Gs. 400.000", "Cubre el costo fijo con holgura"],
        ["1 Bronce + 1 Plata", "Gs. 420.000", "Superávit de ~Gs. 240.400/mes"],
    ],
    col_widths=[2.2, 1.8, 2.6],
)
para(
    "Con una sola suscripción Plata u Oro al mes el modelo ya cubre infraestructura, soporte y "
    "mantenimiento. Al ser ingresos recurrentes, cada suscripción activa aporta todos los meses. La "
    "inversión inicial (Gs. 9.532.200) se recupera en ~40 meses con un superávit de Gs. 240.400/mes, "
    "o en ~8 meses con 5 suscripciones Plata mensuales.",
    italic=True, color=VERDE,
)

# ------------------------------------------------------------
# 10. BUSINESS MODEL CANVAS FINAL
# ------------------------------------------------------------
h("10. Business Model Canvas final", 1)
para("El Canvas sintetiza los nueve bloques del modelo. El Canvas representa la lógica del negocio; no "
     "la reemplaza.")

def canvas_block(nombre, contenido):
    tabla(
        [nombre],
        [[contenido]],
        header_bg="2E5A8C",
        col_widths=[6.6],
    )

canvas_block("1. Segmentos de clientes",
    "Cliente y pagador: inmobiliarias de Asunción. Usuarios: administradores y responsables de "
    "evaluación autorizados. Necesidad: agilizar y estandarizar el análisis de clientes y apoyar "
    "decisiones de riesgo.")
canvas_block("2. Propuesta de valor",
    "Evaluación automatizada del riesgo con variables como ingresos, historial de pagos, endeudamiento "
    "y comportamiento financiero. Reglas IF-THEN parametrizadas que entregan puntaje y clasificación "
    "Alto/Medio/Bajo. Verificación automática contra listas negras ONU/OFAC (diferenciador). Reportes "
    "de apoyo a la decisión. Objetivo: reducir el tiempo de evaluación de 20–40 a 5–10 min.")
canvas_block("3. Canales",
    "Plataforma web. Contacto comercial directo con inmobiliarias. Demostración del sistema. Canales "
    "digitales de soporte y comunicación.")
canvas_block("4. Relación con clientes",
    "Soporte técnico y asistencia durante el uso. Orientación inicial y capacitación básica a usuarios "
    "autorizados. Mantenimiento y actualizaciones. Comunicación digital.")
canvas_block("5. Fuentes de ingreso",
    "Suscripción mensual por planes: Bronce (15 reportes/mes — Gs. 150.000), Plata (30 reportes/mes — "
    "Gs. 270.000), Oro (50 reportes/mes — Gs. 400.000). Evaluaciones adicionales al superar el cupo "
    "mensual. Ingresos recurrentes mes a mes.")
canvas_block("6. Recursos clave",
    "Plataforma web React/Flask y base de datos. Motor de reglas, criterios y conocimiento del dominio. "
    "Reglas IF-THEN validadas. Infraestructura de alojamiento, seguridad, respaldos y soporte.")
canvas_block("7. Actividades clave",
    "Desarrollo y mantenimiento del sistema. Configuración y actualización de criterios y reglas "
    "IF-THEN. Procesamiento de evaluaciones y generación de reportes. Validación funcional. Soporte.")
canvas_block("8. Socios/recursos externos",
    "No se definen socios comerciales. Proveedores de tecnología (no socios): Render (infraestructura), "
    "GitHub (repositorio), Pagopar (pasarela de pagos). ONU/OFAC: fuentes externas de información.")
canvas_block("9. Estructura de costos",
    "Inversión inicial única: ~Gs. 9.532.200. Costos recurrentes fijos: ~Gs. 179.600/mes "
    "(~Gs. 2.154.000/año). Costo variable: comisión de pasarela por transacción.")

# ------------------------------------------------------------
# 11. ANÁLISIS INTEGRAL DEL CANVAS
# ------------------------------------------------------------
h("11. Análisis integral del Canvas", 1)
para("El análisis transversal muestra cómo los bloques se refuerzan entre sí y se agrupan en tres ejes:")
bullet("segmentos, canales y relación con clientes. Define a quién se sirve (inmobiliarias) y cómo se le llega (plataforma web + contacto directo).",
       "Eje de mercado: ")
bullet("recursos, actividades y socios/recursos externos. Sostiene la operación: el motor de reglas y la infraestructura permiten procesar evaluaciones de forma continua.",
       "Eje de operación: ")
bullet("la propuesta de valor conecta ambos ejes, equilibrada por la estructura de costos y las fuentes de ingreso.",
       "Eje central: ")
para("Coherencia observada:")
bullet("La propuesta de valor (evaluación objetiva y cumplimiento) responde directamente al problema del segmento (subjetividad, lentitud, riesgo de compliance).")
bullet("Las fuentes de ingreso (suscripciones mensuales recurrentes) encajan con la estructura de costos (costo marginal casi nulo), lo que da márgenes amplios y previsibilidad.")
bullet("Los recursos y actividades clave (motor de reglas, mantenimiento) son exactamente los que la propuesta de valor exige.")
bullet("El diferenciador de verificación ONU/OFAC aparece en la propuesta de valor y se apoya en un recurso externo (fuentes de información), sin generar dependencia de un socio comercial.")

# ------------------------------------------------------------
# 12. VIABILIDAD Y COHERENCIA DEL MODELO
# ------------------------------------------------------------
h("12. Viabilidad y coherencia del modelo", 1)
h("12.1 Viabilidad económica", 2)
bullet("Una sola suscripción Plata u Oro mensual cubre la totalidad de los costos recurrentes.")
bullet("Los precios quedan por encima del costo y por debajo del costo del proceso manual, lo que incentiva la adopción.")
bullet("El costo marginal casi nulo permite escalar ingresos sin aumento proporcional de costos.")

h("12.2 Viabilidad técnica", 2)
bullet("El sistema ya está desarrollado y operativo; el motor de reglas es parametrizable y la verificación de cumplimiento está integrada.")
bullet("La trazabilidad y auditoría respaldan el uso del sistema como herramienta de apoyo a la decisión.")

h("12.3 Coherencia del modelo", 2)
para(
    "El modelo es coherente de extremo a extremo: el problema del segmento justifica la propuesta de "
    "valor; la propuesta de valor se sostiene en los recursos y actividades clave; estos generan un "
    "producto (reportes) que el cliente paga mediante un esquema de ingresos alineado con una "
    "estructura de costos de margen amplio. La solución se mantiene explícitamente como apoyo a la "
    "decisión humana, con lógica registrada y trazable, lo que refuerza su aceptación y su defensa "
    "metodológica."
)

# ---- pie ----
doc.add_paragraph()
pie = doc.add_paragraph()
pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
rp = pie.add_run("Apartado elaborado a partir de los documentos de costos/precios y del Business Model "
                 "Canvas del proyecto, en coherencia con la validación técnica del scoring.")
rp.italic = True
rp.font.size = Pt(9)
rp.font.color.rgb = GRIS

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Modelo_Negocio_Logica_Operativa_v2.docx")
doc.save(out)
print("GENERADO:", out)
