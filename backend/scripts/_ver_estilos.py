# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
from docx import Document

path = r"C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\DICCIONARIO CORREGIDO.docx"
doc = Document(path)

for p in doc.paragraphs:
    txt = p.text.strip()
    if txt:
        print(f"[{p.style.name}] -> {txt[:60]}")
