# -*- coding: utf-8 -*-
"""Codifica el .puml al formato de URL de PlantUML y genera un HTML con la imagen SVG/PNG."""
import zlib
import os

PUML = r"c:\Users\RYZEN\Documents\TESIS 2026\SISTEMA\V.0.1\diagramas\Diagrama_Componentes.puml"
HTML = r"c:\Users\RYZEN\Documents\TESIS 2026\SISTEMA\V.0.1\diagramas\diagrama_componentes.html"

with open(PUML, 'r', encoding='utf-8') as f:
    text = f.read()

# Codificacion PlantUML (deflate raw + alfabeto propio)
def encode6bit(b):
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return '-'
    if b == 1:
        return '_'
    return '?'

def append3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return encode6bit(c1 & 0x3F) + encode6bit(c2 & 0x3F) + encode6bit(c3 & 0x3F) + encode6bit(c4 & 0x3F)

def plantuml_encode(txt):
    data = txt.encode('utf-8')
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    compressed = compressor.compress(data) + compressor.flush()
    res = ''
    b = compressed
    i = 0
    while i < len(b):
        if i + 2 < len(b):
            res += append3bytes(b[i], b[i+1], b[i+2])
        elif i + 1 < len(b):
            res += append3bytes(b[i], b[i+1], 0)
        else:
            res += append3bytes(b[i], 0, 0)
        i += 3
    return res

encoded = plantuml_encode(text)
svg_url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
png_url = f"https://www.plantuml.com/plantuml/png/{encoded}"

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Diagrama de Componentes</title>
<style>
  @page {{ size: A4 landscape; margin: 1cm; }}
  body {{ font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 10px; }}
  h1 {{ font-size: 16px; margin: 6px 0; }}
  img {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
  <img src="{svg_url}" alt="Diagrama de Componentes" />
</body>
</html>"""

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML ->", HTML)
print("SVG_URL:", svg_url[:120], "...")
