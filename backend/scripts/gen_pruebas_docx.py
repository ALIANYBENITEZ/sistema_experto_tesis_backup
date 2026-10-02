# -*- coding: utf-8 -*-
"""
Genera el capítulo "Pruebas y validación" en formato Word (.docx),
alineado al stack real del proyecto (Flask + React + SQL Server + PyTest + JWT + scrypt)
y siguiendo la estructura y plantilla exigida por la cátedra (estilo APA).
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "docs", "Pruebas_y_Validacion.docx",
)
OUT = os.path.abspath(OUT)


# ─────────────────────────── helpers de formato ───────────────────────────
def set_cell_bg(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def add_body(doc, text, justify=True):
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_after = Pt(0)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
    return p


def add_section_heading(doc, text, level=2):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = "Times New Roman"
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    return h


def add_table_caption(doc, numero, titulo):
    p1 = doc.add_paragraph()
    r1 = p1.add_run(f"Tabla {numero}")
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(12)
    p2 = doc.add_paragraph()
    r2 = p2.add_run(titulo)
    r2.italic = True
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    p2.paragraph_format.space_after = Pt(4)


def add_nota(doc):
    p = doc.add_paragraph()
    r = p.add_run("Nota. ")
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r2 = p.add_run("Elaboración propia.")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(12)


def add_caso_prueba(doc, numero, titulo, filas):
    """filas: lista de tuplas (elemento, descripcion)."""
    add_table_caption(doc, numero, titulo)
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_el, w_desc = Cm(4.0), Cm(12.0)

    hdr = tbl.rows[0].cells
    for i, txt in enumerate(("Elemento", "Descripción")):
        hdr[i].text = ""
        run = hdr[i].paragraphs[0].add_run(txt)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        set_cell_bg(hdr[i], "1E3A5F")
    hdr[0].width = w_el
    hdr[1].width = w_desc

    for elemento, descripcion in filas:
        row = tbl.add_row().cells
        row[0].width = w_el
        row[1].width = w_desc
        re = row[0].paragraphs[0].add_run(elemento)
        re.bold = True
        re.font.name = "Times New Roman"
        re.font.size = Pt(11)
        rd = row[1].paragraphs[0].add_run(descripcion)
        rd.font.name = "Times New Roman"
        rd.font.size = Pt(11)

    add_nota(doc)


# ─────────────────────────── documento ───────────────────────────
doc = Document()
for s in doc.sections:
    s.left_margin = Cm(2.5)
    s.right_margin = Cm(2.5)
    s.top_margin = Cm(2.5)
    s.bottom_margin = Cm(2.5)

# Estilo base
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)

# Título del capítulo
titulo = doc.add_heading("Pruebas y validación", level=1)
for r in titulo.runs:
    r.font.name = "Times New Roman"
    r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

# ── Plan de pruebas ──
add_section_heading(doc, "Plan de pruebas")
add_body(doc,
    "El presente plan de pruebas tiene como objetivo principal asegurar la calidad (QA) y el "
    "correcto funcionamiento de los módulos críticos del sistema experto de scoring de clientes, "
    "enfocándose a nivel de código y de lógica transaccional, sin requerir pruebas operativas en "
    "ambientes reales de producción. El alcance abarca la validación de las reglas de negocio del "
    "motor de inferencia, la integridad de la base de datos, la seguridad de la aplicación web y la "
    "trazabilidad de las operaciones mediante la bitácora de auditoría.")
add_body(doc,
    "El ambiente de pruebas se configuró en una estación de trabajo local con sistema operativo "
    "Windows 11, procesador AMD Ryzen y 16 GB de memoria RAM. La arquitectura evaluada "
    "corresponde a una aplicación web compuesta por una API REST desarrollada en Flask 3.1 "
    "(Python) y una interfaz de usuario tipo SPA construida con React 18 y Vite, con persistencia "
    "en SQL Server 2022 mediante el conector pyodbc.")
add_body(doc,
    "Las herramientas utilizadas incluyeron el entorno de desarrollo integrado (IDE) con su "
    "depurador para el monitoreo del flujo de ejecución (pruebas manuales sobre la interfaz y sobre "
    "los endpoints de la API). Para asegurar la solidez del código mediante pruebas automatizadas se "
    "implementó el framework PyTest, el cual permitió estructurar y ejecutar scripts de pruebas "
    "unitarias y de integración sobre la lógica de negocio (autenticación, control de roles, motor de "
    "reglas y capa de datos). La captura de excepciones esperadas se validó con el bloque "
    "pytest.raises, verificando que el sistema controla los errores sin interrumpir la ejecución. Las "
    "pruebas se ejecutaron contra una instancia de base de datos de pruebas, garantizando que el "
    "entorno de desarrollo principal no sufriera alteraciones.")

# ── Validación del Modelo de Base de Datos ──
add_section_heading(doc, "Validación del Modelo de Base de Datos")
add_body(doc,
    "La validación estructural se ejecutó mediante la inserción controlada y eliminación de registros "
    "a través de sentencias DML sobre el motor SQL Server, apoyadas por los scripts de automatización "
    "de PyTest. Se comprobó que el esquema respeta la Tercera Forma Normal (3FN) y que las "
    "restricciones de claves foráneas bloquean correctamente las eliminaciones no autorizadas de "
    "registros vinculados (integridad referencial). Por ejemplo, se validó que no es posible eliminar "
    "físicamente un cliente que ya posee evaluaciones o documentos asociados, respetando además la "
    "política de baja lógica (soft-delete) del sistema mediante el campo estado. Asimismo, se contrastó "
    "la estructura física generada contra el Diccionario de Datos, verificando la correspondencia exacta "
    "de los tipos de datos y las longitudes máximas permitidas (por ejemplo, num_doc VARCHAR(20), "
    "email VARCHAR(150)).")

# ── Validación de Seguridad ──
add_section_heading(doc, "Validación de Seguridad")
add_body(doc,
    "Se sometió la capa de seguridad a pruebas de penetración lógica controlada. Se verificó que la "
    "aplicación almacena las contraseñas aplicando el algoritmo de cifrado scrypt (a través de "
    "werkzeug.security), impidiendo su lectura en texto plano dentro de la base de datos. Las pruebas "
    "de roles confirmaron que la API y la interfaz gráfica se adaptan dinámicamente al perfil "
    "autenticado: los endpoints protegidos con el decorador roles_required deniegan el acceso "
    "(código HTTP 403) cuando un usuario con rol comercial intenta operar sobre módulos "
    "administrativos, cumpliendo con el principio de mínimo privilegio. Adicionalmente, se validó el "
    "mecanismo de doble factor de autenticación (2FA) basado en TOTP (Google Authenticator), "
    "comprobando que el sistema exige un código válido de seis dígitos antes de emitir los tokens de "
    "acceso completos (JWT).")

# ── Validación de Auditoría ──
add_section_heading(doc, "Validación de Auditoría")
add_body(doc,
    "Para garantizar la trazabilidad de las operaciones se ejecutaron ciclos de alta, baja y "
    "modificación de registros. Posteriormente se auditó la tabla auditoria, verificando que el sistema "
    "captura con precisión el identificador del usuario, el nombre, la fecha y hora exacta, el tipo de "
    "evento, la acción, el resultado (EXITO/FALLO), la dirección IP y, cuando corresponde, los valores "
    "anteriores y nuevos del registro afectado. Se comprobó que tanto los eventos de autenticación "
    "(LOGIN_EXITOSO, LOGIN_FALLIDO) como los eventos de seguridad (RESET_2FA, "
    "CAMBIO_CONTRASENA) quedan registrados de forma automática.")

# ── Resultados esperados e indicadores ──
add_section_heading(doc, "Resultados esperados e indicadores")
add_body(doc,
    "A continuación se presentan los resultados obtenidos tras la ejecución de los casos de prueba "
    "críticos, evaluando el control de errores internos y contrastando el comportamiento real de la "
    "aplicación frente a los criterios de aceptación definidos.")
doc.add_paragraph("")

# ── Casos de prueba ──
add_caso_prueba(doc, 1, "Caso de Prueba 1: Restricción de Integridad Referencial", [
    ("Identificador", "CP-01"),
    ("Nombre", "Eliminación de registro con dependencias activas"),
    ("Criterios de Aceptación",
     "El sistema debe impedir la eliminación de un cliente si este posee evaluaciones o documentos "
     "previamente registrados."),
    ("Control de Errores",
     "La capa de acceso a datos (SQLAlchemy/pyodbc) debe capturar la excepción de restricción de "
     "clave foránea y retornar un mensaje amigable a la capa de presentación (respuesta JSON con "
     "success: false) sin interrumpir el servicio de la API."),
    ("Resultado Esperado",
     'Cancelación de la eliminación y visualización del mensaje: "No se puede eliminar el registro '
     'porque tiene datos asociados".'),
    ("Resultado Obtenido",
     "El sistema bloqueó la acción correctamente, gestionó la excepción a nivel de código QA "
     "(validado mediante PyTest) y devolvió la respuesta controlada esperada. La baja se realizó de "
     "forma lógica (soft-delete) sobre el campo estado."),
    ("Evidencias",
     "Ver Figura 25 - Respuesta de la API ante integridad referencial y Figura 26 - Consola de "
     "PyTest con el test superado."),
])

add_caso_prueba(doc, 2, "Caso de Prueba 2: Verificación de Doble Factor de Autenticación (2FA)", [
    ("Identificador", "CP-02"),
    ("Nombre", "Rechazo de código OTP inválido en el login"),
    ("Criterios de Aceptación",
     "El sistema no debe emitir el token de acceso completo (JWT authenticated) si el código TOTP "
     "de seis dígitos ingresado es incorrecto."),
    ("Control de Errores",
     "El endpoint /2fa/verify debe validar el OTP contra el secreto del usuario y responder con "
     "código HTTP 401 ante un código inválido, sin conceder acceso."),
    ("Resultado Esperado",
     'Mensaje de error: "Código OTP incorrecto" y denegación del acceso.'),
    ("Resultado Obtenido",
     "La validación del OTP funcionó correctamente: ante un código inválido el sistema devolvió 401 "
     "y no emitió el token completo; ante un código válido emitió los tokens de acceso y refresco."),
    ("Evidencias",
     "Ver Figura 27 - Mensaje de OTP incorrecto y Figura 28 - Consola de PyTest mostrando el test "
     "de verificación 2FA."),
])

add_caso_prueba(doc, 3, "Caso de Prueba 3: Validación de Trazabilidad Transaccional", [
    ("Identificador", "CP-03"),
    ("Nombre", "Registro automático de eventos de auditoría"),
    ("Criterios de Aceptación",
     "Toda modificación crítica de datos (alta, baja o modificación) debe generar un registro "
     "automático en la tabla auditoria."),
    ("Control de Errores",
     "Si la operación principal se realiza pero falla el registro de auditoría, la transacción completa "
     "debe revertirse (rollback), preservando la consistencia de los datos."),
    ("Resultado Esperado",
     "Un nuevo registro en la tabla auditoria con el identificador del usuario, la acción, el módulo, "
     "el resultado y la fecha/hora del sistema."),
    ("Resultado Obtenido",
     "La operación se ejecutó correctamente y se verificó la creación del registro correspondiente en "
     "la bitácora, con la marca de tiempo exacta y los valores anteriores/nuevos cuando aplicaba."),
    ("Evidencias",
     "Ver Figura 29 - Visualización de la tabla auditoria en el motor de base de datos."),
])

add_caso_prueba(doc, 4, "Caso de Prueba 4: Manejo de Excepciones de Conectividad", [
    ("Identificador", "CP-04"),
    ("Nombre", "Pérdida de conexión con el servidor de base de datos"),
    ("Criterios de Aceptación",
     "La API no debe detener su ejecución de forma abrupta si el servidor de SQL Server se apaga o "
     "pierde conectividad durante una operación."),
    ("Control de Errores",
     "La capa de datos debe capturar la excepción de conexión (OperationalError / pyodbc) y "
     "responder con un mensaje controlado, manteniendo el servicio operativo para las siguientes "
     "solicitudes."),
    ("Resultado Esperado",
     'Respuesta con mensaje: "Error de conexión con el servidor. Intente nuevamente" y código de '
     "error apropiado."),
    ("Resultado Obtenido",
     "Al simular la caída del servicio de datos, la aplicación capturó la excepción y devolvió la "
     "respuesta controlada, sin cerrarse ni corromper el estado del servidor."),
    ("Evidencias",
     "Ver Figura 30 - Respuesta de la API ante pérdida de conexión."),
])

add_caso_prueba(doc, 5, "Caso de Prueba 5: Verificación del Principio de Mínimo Privilegio", [
    ("Identificador", "CP-05"),
    ("Nombre", "Acceso a módulos restringidos por rol"),
    ("Criterios de Aceptación",
     "Los usuarios con rol comercial no deben acceder a los módulos administrativos (gestión de "
     "usuarios, configuración de criterios y motores de reglas)."),
    ("Control de Errores",
     "El decorador roles_required debe validar el rol del token JWT y denegar la acción con código "
     "HTTP 403 ante un acceso no autorizado, tanto si se intenta desde la interfaz como directamente "
     "contra la API."),
    ("Resultado Esperado",
     'La interfaz no muestra los botones/menús administrativos al rol comercial, y la API responde '
     '403 con el mensaje "No tienes permisos para esta acción".'),
    ("Resultado Obtenido",
     "El renderizado condicional del frontend (ProtectedRoute con adminOnly) ocultó las secciones "
     "restringidas según el perfil, y la rutina de validación del backend (comprobada vía tests con "
     "PyTest) bloqueó los accesos alternativos directos a la API."),
    ("Evidencias",
     "Ver Figura 31 - Interfaz con menú restringido para el rol comercial y respuesta 403 de la API."),
])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print("WORD generado:", OUT)
