# -*- coding: utf-8 -*-
"""
Genera el documento 'Justificacion de precios.docx' para el marco metodologico.

Consolida la cuantificacion de costos, la justificacion de precios de los planes
(Bronce, Plata, Oro) y el punto de equilibrio basico del modelo de negocio.

Mismo estilo que generar_manuales.py (Times New Roman 12, estilo tesis/APA).

Ejecutar:
    python generar_justificacion_precios.py
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

AQUI = os.path.dirname(os.path.abspath(__file__))

GRIS = RGBColor(0x55, 0x55, 0x55)
AZUL = RGBColor(0x1F, 0x49, 0x7D)


def set_base_style(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)


def parrafo(doc, texto="", italic=False, color=None, size=None, align=None,
            space_after=6):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    if size is not None:
        run.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def vinetas(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        if isinstance(it, tuple):
            fuerte, resto = it
            r = p.add_run(fuerte)
            r.bold = True
            p.add_run(resto)
        else:
            p.add_run(it)


def pasos(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Number")
        if isinstance(it, tuple):
            fuerte, resto = it
            r = p.add_run(fuerte)
            r.bold = True
            p.add_run(resto)
        else:
            p.add_run(it)


def formula(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(texto)
    r.bold = True
    r.italic = True
    r.font.color.rgb = AZUL
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)


def tabla_planes(doc):
    datos = [
        ("Plan", "Reportes", "Precio por reporte", "Precio del plan", "Margen vs. piso"),
        ("Bronce", "15", "Gs. 10.000", "Gs. 150.000", "40%"),
        ("Plata", "30", "Gs. 9.000", "Gs. 270.000", "33%"),
        ("Oro", "50", "Gs. 8.000", "Gs. 400.000", "25%"),
    ]
    tabla = doc.add_table(rows=len(datos), cols=len(datos[0]))
    tabla.style = "Light Grid Accent 1"
    for i, fila in enumerate(datos):
        for j, celda in enumerate(fila):
            c = tabla.cell(i, j)
            c.text = celda
            for par in c.paragraphs:
                for run in par.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11)
                    if i == 0:
                        run.bold = True
    doc.add_paragraph()


def portada(doc):
    for _ in range(5):
        doc.add_paragraph()
    parrafo(doc, "JUSTIFICACIÓN DE PRECIOS", align=WD_ALIGN_PARAGRAPH.CENTER,
            size=26, space_after=14)
    parrafo(doc, "Modelo de negocio del Sistema Experto Web de Scoring para el "
                 "Análisis de Riesgo de Clientes en Inmobiliarias",
            align=WD_ALIGN_PARAGRAPH.CENTER, size=14, italic=True, space_after=30)
    parrafo(doc, "Cuantificación de costos, justificación de precios y punto de "
                 "equilibrio", align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=6)
    parrafo(doc, "Asunción, Paraguay — 2026", align=WD_ALIGN_PARAGRAPH.CENTER,
            size=12, space_after=6)
    doc.add_page_break()


def generar(ruta):
    doc = Document()
    set_base_style(doc)
    portada(doc)

    doc.add_heading("Justificación de Precios", level=1)
    parrafo(doc,
            "El presente documento cuantifica los costos del modelo de negocio, "
            "justifica los precios de los planes de reportes de scoring y demuestra "
            "la sostenibilidad del sistema mediante un punto de equilibrio básico. "
            "Los montos se expresan en guaraníes (Gs.) y constituyen una hipótesis "
            "comercial sujeta a validación con proveedores y con la encuesta de "
            "disposición a pagar aplicada a inmobiliarias.")
    parrafo(doc,
            "Tipo de cambio referencial: 1 USD ≈ Gs. 7.300, deducido del costo del "
            "servicio Render (US$ 7/mes = Gs. 51.100).", italic=True, size=10,
            color=GRIS)

    # 1. Clasificacion de costos
    doc.add_heading("Clasificación de Costos", level=2)
    parrafo(doc,
            "Los costos del modelo se separan en dos tipos: la inversión inicial "
            "(costo único de desarrollo) y los costos recurrentes (operación mensual).")

    doc.add_heading("A. Inversión inicial (costo único de desarrollo)", level=3)
    parrafo(doc,
            "Esfuerzo y recursos empleados una sola vez para construir el sistema "
            "(Tablas 5, 6 y 8 del presupuesto):")
    vinetas(doc, [
        ("Recursos humanos (500 h de desarrollo): ", "Gs. 5.000.000."),
        ("Hardware (laptop y smartphone de pruebas): ", "Gs. 4.300.000."),
        ("Software y licencias del período de desarrollo: ", "Gs. 232.200."),
        ("Total inversión inicial: ", "Gs. 9.532.200 (≈ US$ 1.306)."),
    ])
    parrafo(doc,
            "Los gastos administrativos de la tesis (Tabla 7, Gs. 731.250) se "
            "consideran propios del trabajo académico y no del producto comercial, "
            "por lo que se excluyen del modelo de negocio.", italic=True, size=10,
            color=GRIS)

    doc.add_heading("B. Costos recurrentes (operación mensual)", level=3)
    parrafo(doc,
            "Costos necesarios para mantener la plataforma funcionando. Es el bloque "
            "sobre el que se concentra el Business Model Canvas:")
    vinetas(doc, [
        ("Hosting backend (Render Web Service Starter): ",
         "Gs. 51.100/mes — Gs. 613.200/año."),
        ("Base de datos PostgreSQL administrada (Render): ",
         "Gs. 51.100/mes — Gs. 613.200/año."),
        ("Frontend estático (Render, plan Free): ", "Gs. 0/mes — Gs. 0/año."),
        ("Dominio (prorrateado): ", "~Gs. 7.300/mes — ~Gs. 87.600/año."),
        ("Mantenimiento y actualización del motor de scoring: ",
         "~Gs. 40.000/mes — ~Gs. 480.000/año."),
        ("Soporte técnico, seguridad y respaldos: ",
         "~Gs. 30.000/mes — ~Gs. 360.000/año."),
        ("Subtotal fijo: ", "~Gs. 179.600/mes — ~Gs. 2.154.000/año."),
        ("Comisión de pasarela (Pagopar): ",
         "costo variable (% por transacción, proporcional a las ventas)."),
    ])

    # 2. Costo operativo por evaluacion
    doc.add_heading("Costo Operativo por Evaluación", level=2)
    parrafo(doc,
            "El costo marginal de producir una evaluación adicional es prácticamente "
            "cero, pues el sistema ya está desarrollado y en operación. El costo "
            "relevante es el costo fijo mensual repartido entre las evaluaciones "
            "vendidas en el mes:")
    formula(doc, "Costo unitario = Costo fijo mensual ÷ evaluaciones vendidas en el mes")
    vinetas(doc, [
        "30 evaluaciones/mes: 179.600 ÷ 30 = ~Gs. 6.000 por evaluación (escenario conservador).",
        "50 evaluaciones/mes: 179.600 ÷ 50 = ~Gs. 3.592 por evaluación.",
        "100 evaluaciones/mes: 179.600 ÷ 100 = ~Gs. 1.796 por evaluación.",
        "200 evaluaciones/mes: 179.600 ÷ 200 = ~Gs. 898 por evaluación.",
    ])
    parrafo(doc,
            "Se adopta Gs. 6.000 como piso de costo para no subestimar en el "
            "escenario inicial.")

    # 3. Derivacion de precios
    doc.add_heading("Derivación de los Precios", level=2)
    parrafo(doc,
            "Los precios no se fijan de forma arbitraria: se derivan combinando "
            "cuatro reglas estándar de pricing.")

    doc.add_heading("Paso 1 — Piso de costo", level=3)
    parrafo(doc, "Costo operativo por evaluación en el escenario conservador: Gs. 6.000.")

    doc.add_heading("Paso 2 — Margen sobre costo (markup)", level=3)
    formula(doc, "Precio = Costo ÷ (1 − margen deseado)")
    parrafo(doc,
            "Para servicios de software, donde el costo marginal es casi nulo, se "
            "aplica un margen alto (60-70%). Con margen 65%: 6.000 ÷ (1 − 0,65) = "
            "~Gs. 17.000. Este valor supera el techo de valor, por lo que se ajusta "
            "hacia abajo.")

    doc.add_heading("Paso 3 — Techo de valor (anclaje)", level=3)
    parrafo(doc,
            "El cliente no paga más de lo que le cuesta hacer la evaluación de forma "
            "manual. Una evaluación manual toma 20-40 min; a un costo de analista de "
            "~Gs. 30.000-50.000/hora, equivale a Gs. 10.000-15.000 por evaluación "
            "manual. Ese es el techo: el precio debe quedar por debajo para que al "
            "cliente le convenga automatizar. Rango viable: piso Gs. 6.000 → techo "
            "Gs. 10.000-15.000.")

    doc.add_heading("Paso 4 — Descuento por volumen", level=3)
    parrafo(doc,
            "A mayor volumen, menor precio unitario, lo que incentiva compras "
            "mayores sin que el costo marginal aumente. Partiendo del plan de entrada "
            "en la zona alta del rango:")
    vinetas(doc, [
        ("Bronce (entrada, sin descuento): ", "Gs. 10.000/evaluación."),
        ("Plata (−10%): ", "Gs. 9.000/evaluación."),
        ("Oro (−20%): ", "Gs. 8.000/evaluación."),
    ])

    doc.add_heading("Precio final por reporte y por plan", level=3)
    tabla_planes(doc)
    parrafo(doc,
            "Todos los precios quedan por encima del piso de costo (Gs. 6.000) y por "
            "debajo del techo de valor (Gs. 10.000-15.000), con un descuento por "
            "volumen coherente. Los precios propuestos originalmente quedan así "
            "validados por el cálculo.")

    # 4. Punto de equilibrio
    doc.add_heading("Punto de Equilibrio", level=2)
    formula(doc, "Punto de equilibrio (unidades) = Costos fijos mensuales ÷ margen de "
                 "contribución por plan")
    parrafo(doc,
            "Como el costo variable por evaluación es casi nulo, el margen de "
            "contribución ≈ precio del plan. El costo de mantener el sistema por mes "
            "es Gs. 179.600.")
    parrafo(doc, "¿Cuántos clientes de cada plan cubren ese costo mensual?")
    vinetas(doc, [
        ("Solo Bronce (Gs. 150.000 c/u): ", "179.600 ÷ 150.000 = 1,2 → 2 clientes Bronce."),
        ("Solo Plata (Gs. 270.000 c/u): ", "179.600 ÷ 270.000 = 0,67 → 1 cliente Plata."),
        ("Solo Oro (Gs. 400.000 c/u): ", "179.600 ÷ 400.000 = 0,45 → 1 cliente Oro."),
    ])
    parrafo(doc, "Combinación de ejemplo que demuestra sostenibilidad:")
    vinetas(doc, [
        "1 Bronce (Gs. 150.000) + 1 Plata (Gs. 270.000) = Gs. 420.000 de ingreso mensual.",
        "Costo fijo mensual: Gs. 179.600.",
        "Superávit mensual: ~Gs. 240.400.",
    ])
    parrafo(doc,
            "Con un solo cliente Plata u Oro al mes el modelo ya cubre "
            "infraestructura, soporte y mantenimiento. Cualquier cliente adicional "
            "genera margen para reinvertir.")

    doc.add_heading("Recuperación de la inversión inicial", level=3)
    parrafo(doc, "Si se destina el superávit a recuperar la inversión inicial "
                 "(Gs. 9.532.200):")
    vinetas(doc, [
        "Con un superávit de ~Gs. 240.400/mes: 9.532.200 ÷ 240.400 ≈ 40 meses (~3,3 años).",
        "Con 5 clientes Plata/mes (superávit ~Gs. 1.170.400): 9.532.200 ÷ 1.170.400 ≈ 8 meses.",
    ])

    # 5. Conclusion
    doc.add_heading("Conclusión", level=2)
    parrafo(doc,
            "El modelo propuesto es sostenible: basta un cliente Plata u Oro mensual "
            "para cubrir la totalidad de los costos recurrentes. Los precios de los "
            "planes (Gs. 10.000, 9.000 y 8.000 por reporte) se justifican porque:")
    vinetas(doc, [
        "superan el costo operativo por evaluación (margen positivo);",
        "quedan por debajo del costo del proceso manual (ahorro de tiempo para la inmobiliaria);",
        "aplican un descuento por volumen coherente.",
    ])
    parrafo(doc,
            "Estos precios se presentan como hipótesis comercial respaldada por el "
            "cálculo de costos y pendiente de ajuste según los resultados de la "
            "encuesta de disposición a pagar y las condiciones reales de los "
            "proveedores.")

    doc.save(ruta)
    return ruta


if __name__ == "__main__":
    salida = os.path.join(AQUI, "Justificacion_de_precios.docx")
    generar(salida)
    print(salida)
