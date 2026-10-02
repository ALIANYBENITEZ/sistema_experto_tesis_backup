# -*- coding: utf-8 -*-
"""
Corrige el Diccionario de Datos:
- Mantiene la descripción arriba de cada tabla (ya existente).
- Agrega una nota "Nota. Elaboración propia." (estilo APA) debajo de cada tabla.
Preserva el contenido y formato original; solo inserta las notas.
"""
import sys
import copy
sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = r"C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\DICCIONARIO CORREGIR.docx"
OUT = r"C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\DICCIONARIO CORREGIDO.docx"

doc = Document(SRC)


def hacer_nota_xml():
    """Crea un elemento <w:p> con 'Nota. ' en cursiva + 'Elaboración propia.'"""
    p = OxmlElement("w:p")

    # Espaciado del párrafo
    pPr = OxmlElement("w:pPr")
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:after"), "240")  # espacio después (12pt)
    spacing.set(qn("w:before"), "40")
    pPr.append(spacing)
    p.append(pPr)

    # Run 1: "Nota. " en cursiva
    r1 = OxmlElement("w:r")
    rPr1 = OxmlElement("w:rPr")
    rFonts1 = OxmlElement("w:rFonts")
    rFonts1.set(qn("w:ascii"), "Times New Roman")
    rFonts1.set(qn("w:hAnsi"), "Times New Roman")
    rPr1.append(rFonts1)
    i1 = OxmlElement("w:i")
    rPr1.append(i1)
    sz1 = OxmlElement("w:sz")
    sz1.set(qn("w:val"), "22")  # 11pt (sz en medios puntos)
    rPr1.append(sz1)
    r1.append(rPr1)
    t1 = OxmlElement("w:t")
    t1.set(qn("xml:space"), "preserve")
    t1.text = "Nota. "
    r1.append(t1)
    p.append(r1)

    # Run 2: "Elaboración propia." normal
    r2 = OxmlElement("w:r")
    rPr2 = OxmlElement("w:rPr")
    rFonts2 = OxmlElement("w:rFonts")
    rFonts2.set(qn("w:ascii"), "Times New Roman")
    rFonts2.set(qn("w:hAnsi"), "Times New Roman")
    rPr2.append(rFonts2)
    sz2 = OxmlElement("w:sz")
    sz2.set(qn("w:val"), "22")
    rPr2.append(sz2)
    r2.append(rPr2)
    t2 = OxmlElement("w:t")
    t2.text = "Elaboración propia."
    r2.append(t2)
    p.append(r2)

    return p


# Recorremos el cuerpo; después de cada <w:tbl> insertamos la nota,
# salvo que el siguiente elemento ya sea una nota.
body = doc.element.body
tablas = body.findall(qn("w:tbl"))

notas_insertadas = 0
for tbl in tablas:
    # Verificar si el siguiente hermano ya es una nota (para no duplicar)
    siguiente = tbl.getnext()
    ya_tiene_nota = False
    if siguiente is not None and siguiente.tag == qn("w:p"):
        texto = "".join(t.text or "" for t in siguiente.findall(".//" + qn("w:t")))
        if texto.strip().lower().startswith("nota."):
            ya_tiene_nota = True

    if not ya_tiene_nota:
        nota = hacer_nota_xml()
        tbl.addnext(nota)
        notas_insertadas += 1

doc.save(OUT)
print(f"Notas insertadas: {notas_insertadas}")
print("Guardado en:", OUT)
