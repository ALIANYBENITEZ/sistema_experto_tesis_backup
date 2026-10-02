# -*- coding: utf-8 -*-
"""
Genera el documento Word "Script SQL y Migraciones" para la tesis.
Incluye el párrafo introductorio + el DDL completo de PostgreSQL
(CREATE TABLE con PK/FK/UNIQUE/CHECK, índices y triggers de auditoría)
con formato de código (fuente monoespaciada).
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SALIDA = r"C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\Script_SQL_y_Migraciones.docx"

INTRO = (
    "El presente apartado contiene el código fuente (sentencias DDL) utilizado para "
    "generar la base de datos del sistema. El script evidencia la creación de las tablas, "
    "la aplicación de restricciones físicas (claves primarias, foráneas y únicas) que "
    "garantizan la integridad referencial y las reglas de negocio, y los triggers "
    "implementados para la auditoría automática de cambios sobre la base de datos."
)

# Rutas de los scripts SQL reales de PostgreSQL
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
SCRIPTS = [
    ("CREACIÓN DE TABLAS, RESTRICCIONES E ÍNDICES", os.path.join(BASE, "01_schema.sql")),
    ("FUNCIONES Y TRIGGERS DE AUDITORÍA", os.path.join(BASE, "02_functions_triggers.sql")),
    ("VISTAS", os.path.join(BASE, "03_views.sql")),
]


def add_code_block(doc, texto):
    """Agrega el texto como bloque de código monoespaciado, línea por línea."""
    for linea in texto.splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(linea if linea else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        # Forzar fuente monoespaciada también para caracteres no latinos
        rpr = run._element.get_or_add_rPr()
        rfonts = rpr.find(qn('w:rFonts'))
        if rfonts is None:
            rfonts = OxmlElement('w:rFonts')
            rpr.append(rfonts)
        rfonts.set(qn('w:ascii'), 'Consolas')
        rfonts.set(qn('w:hAnsi'), 'Consolas')


def main():
    doc = Document()
    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(11)

    doc.add_heading('Script SQL y Migraciones', level=1)

    p = doc.add_paragraph(INTRO)
    p.paragraph_format.line_spacing = 1.5

    doc.add_paragraph()

    # Cabecera tipo la de la imagen
    cab = [
        "SCRIPT SQL COMPLETO - Sistema Experto de Scoring Comercial",
        "-- Base de datos: inmobiliaria_db  |  Motor: PostgreSQL",
        "-- Contiene: CREATE TABLE, PK, UNIQUE, FOREIGN KEY, CHECK, INDICES, VISTAS y TRIGGERS",
        "-- ============================================================",
    ]
    add_code_block(doc, "\n".join(cab))
    doc.add_paragraph()

    for titulo, ruta in SCRIPTS:
        doc.add_heading(titulo, level=2)
        try:
            with open(ruta, "r", encoding="utf-8") as fh:
                contenido = fh.read()
        except FileNotFoundError:
            contenido = f"-- (No se encontró el archivo: {ruta})"
        add_code_block(doc, contenido)
        doc.add_paragraph()

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    doc.save(SALIDA)
    print("Documento generado:", SALIDA)


if __name__ == "__main__":
    main()
