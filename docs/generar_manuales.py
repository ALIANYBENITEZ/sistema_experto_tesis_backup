# -*- coding: utf-8 -*-
"""
Genera los dos entregables de la tesis en formato Word (.docx):

  1. Manual_Tecnico.docx   -> dirigido a personal de TI (cómo está construido y
                              cómo se despliega), con el stack REAL del proyecto.
  2. Manual_de_Usuario.docx -> manual de usuario final completado según la guía
                              del profesor (mapa del entorno, avisos del sistema,
                              nota de login, etc.).

Sigue la estructura de títulos de la plantilla del profesor:
  nivel 2 = Título 1 (Heading 1)
  nivel 3 = Título 2 (Heading 2)
  nivel 4 = Título 3 (Heading 3)

Ejecutar:
    python generar_manuales.py
"""
import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

AQUI = os.path.dirname(os.path.abspath(__file__))

ROJO = RGBColor(0xC0, 0x00, 0x00)
GRIS = RGBColor(0x55, 0x55, 0x55)


# ────────────────────────────────────────────────────────────────────
#  Utilidades de formato
# ────────────────────────────────────────────────────────────────────
def set_base_style(doc):
    """Fuente base tipo Times New Roman 12 (estilo APA/tesis)."""
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
    """items: lista de str o de tuplas (negrita, resto)."""
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


def codigo(doc, lineas):
    """Bloque monoespaciado para comandos / configuración."""
    for ln in lineas:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(ln)
        r.font.name = "Consolas"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)


def figura(doc, titulo, descripcion):
    """Marcador de figura con instrucción de captura (regla visual del profe)."""
    p = doc.add_paragraph()
    r = p.add_run(f"[ Insertar captura de pantalla — {titulo} ]")
    r.italic = True
    r.font.color.rgb = ROJO
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)

    p2 = doc.add_paragraph()
    r2 = p2.add_run("Nota: señale con flechas o recuadros rojos el botón o campo "
                    "donde debe hacer clic.")
    r2.italic = True
    r2.font.size = Pt(9)
    r2.font.color.rgb = ROJO

    p3 = doc.add_paragraph()
    rt = p3.add_run("Figura. ")
    rt.bold = True
    rt.font.size = Pt(10)
    rd = p3.add_run(descripcion)
    rd.italic = True
    rd.font.size = Pt(10)
    rd.font.color.rgb = GRIS
    p3.paragraph_format.space_after = Pt(10)


def portada(doc, titulo_grande, subtitulo):
    for _ in range(4):
        doc.add_paragraph()
    parrafo(doc, titulo_grande, align=WD_ALIGN_PARAGRAPH.CENTER, size=26, space_after=14)
    parrafo(doc, "Sistema Experto Web de Scoring para el Análisis de Riesgo de "
                 "Clientes en Inmobiliarias", align=WD_ALIGN_PARAGRAPH.CENTER,
            size=14, italic=True, space_after=30)
    parrafo(doc, subtitulo, align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=6)
    parrafo(doc, "Asunción, Paraguay — 2026", align=WD_ALIGN_PARAGRAPH.CENTER,
            size=12, space_after=6)
    doc.add_page_break()


# ════════════════════════════════════════════════════════════════════
#  1) MANUAL TÉCNICO
# ════════════════════════════════════════════════════════════════════
def generar_manual_tecnico(ruta):
    doc = Document()
    set_base_style(doc)

    portada(doc, "MANUAL TÉCNICO",
            "Dirigido al personal de Tecnologías de la Información "
            "(desarrolladores, administradores de sistemas y soporte técnico)")

    doc.add_heading("Manual Técnico", level=1)

    # Propósito
    doc.add_heading("Propósito del Documento", level=2)
    parrafo(doc,
            "El presente manual técnico está dirigido al personal de Tecnologías de "
            "la Información (desarrolladores, administradores de sistemas y soporte "
            "técnico). Su objetivo es documentar la arquitectura, el stack "
            "tecnológico y los procedimientos exactos para la configuración, "
            "instalación y despliegue del sistema en un entorno de desarrollo o "
            "producción, de modo que otro profesional pueda replicar el proyecto.")

    # Arquitectura
    doc.add_heading("Arquitectura", level=2)
    parrafo(doc,
            "El sistema fue construido bajo una arquitectura cliente-servidor "
            "separada, implementando el patrón de diseño API RESTful y una "
            "organización en capas. Además, opera bajo un modelo multi-inquilino "
            "(multi-empresa): cada empresa accede únicamente a sus propios datos.")
    vinetas(doc, [
        ("Frontend (capa de presentación): ",
         "Single Page Application (SPA) desarrollada en React que se ejecuta en el "
         "navegador del cliente. Renderiza las interfaces, gestiona el estado de la "
         "sesión y consume la API por HTTP. No accede directamente a la base de datos."),
        ("Backend (capa de lógica de negocio): ",
         "API REST en Flask, organizada en blueprints por dominio (autenticación, "
         "clientes, evaluación, scoring, reportes, facturación, empresas y "
         "auditoría). Contiene el motor de inferencia del sistema experto "
         "(reglas IF-THEN, clasificación de riesgo y verificación contra listas de "
         "sanciones)."),
        ("Capa de acceso a datos (ORM): ",
         "SQLAlchemy abstrae la comunicación con el motor de base de datos y expone "
         "los modelos de dominio, evitando el manejo manual de sentencias SQL desde "
         "la lógica de negocio."),
    ])

    # Stack
    doc.add_heading("Tecnologías y Herramientas", level=2)
    parrafo(doc,
            "Inventario exacto de las herramientas utilizadas, con sus versiones, "
            "para que otro desarrollador pueda replicar el proyecto:")
    vinetas(doc, [
        ("Lenguaje de programación: ", "Python 3.12."),
        ("Backend / API: ", "Flask 3.1.0 con el patrón Application Factory; "
         "Flask-SQLAlchemy 3.1.1 como ORM; Flask-JWT-Extended 4.6.0 para la "
         "autenticación con tokens; Flask-CORS 4.0.0; marshmallow 3.21.3 para "
         "validación."),
        ("Frontend / UI: ", "React 18.3 (JSX) con Vite 5.4 como build tool; "
         "react-router-dom 6 para el ruteo; Axios con interceptores para el consumo "
         "de la API; react-hook-form para formularios; TailwindCSS 3.4 para estilos; "
         "Recharts para gráficos; react-hot-toast para notificaciones."),
        ("Motor de base de datos: ", "PostgreSQL 15, accedido mediante el driver "
         "psycopg 3 (psycopg[binary] 3.2.3)."),
        ("Seguridad: ", "Hashing de contraseñas con scrypt (werkzeug.security); "
         "segundo factor de autenticación (2FA) con TOTP mediante pyotp 2.9.0 y "
         "qrcode 7.4.2 para el código QR."),
        ("Reportes: ", "reportlab 4.2.2 para la generación de reportes en PDF."),
        ("Servidor de producción: ", "gunicorn 23.0.0, desplegado en la nube (Render)."),
        ("Pasarela de pagos: ", "Pagopar (Paraguay), con un modo TEST cuando no está "
         "configurada."),
    ])

    # Configuración del entorno
    doc.add_heading("Configuración del Entorno", level=2)
    parrafo(doc,
            "Para desplegar la aplicación en un nuevo servidor o estación de trabajo, "
            "el equipo debe contar con el siguiente software instalado:")
    vinetas(doc, [
        "Python 3.12 o superior, con pip (gestor de paquetes).",
        "Node.js 18 o superior, con npm (para el frontend).",
        "Servidor de PostgreSQL 15 ejecutándose localmente o en red.",
        "Git, para el control de versiones y la clonación del proyecto.",
    ])

    # Instalación y despliegue
    doc.add_heading("Instalación y Plan de Despliegue", level=2)

    doc.add_heading("Paso 1: Clonación del repositorio", level=3)
    parrafo(doc, "Descargar el código fuente del sistema en el directorio local:")
    codigo(doc, ["git clone [URL_DEL_REPOSITORIO]"])

    doc.add_heading("Paso 2: Preparación de la base de datos", level=3)
    pasos(doc, [
        "Crear la base de datos en PostgreSQL (por defecto: inmobiliaria_db) y un "
        "usuario de servicio con privilegios limitados.",
        "Ejecutar los scripts SQL ubicados en la carpeta backend/migrations/ en "
        "orden numérico para construir las tablas, el módulo de scoring, los "
        "triggers de auditoría y las claves foráneas.",
    ])
    parrafo(doc, "Scripts de migración (ejecutar en este orden):")
    codigo(doc, [
        "00_script_completo_tesis.sql   (o, de forma individual, los siguientes)",
        "01_create_tables.sql",
        "02_database_complete.sql",
        "03_scoring_module.sql",
        "04_update_tipo_doc.sql",
        "05_detalle_operacion.sql",
        "06_auditoria_triggers.sql",
        "07_fk_faltantes.sql",
    ])
    parrafo(doc,
            "Nota: el proyecto no utiliza Alembic; las migraciones se gestionan "
            "mediante scripts SQL manuales.", italic=True, size=10, color=GRIS)

    doc.add_heading("Paso 3: Despliegue y configuración del Backend (API)", level=3)
    pasos(doc, [
        "Navegar a la carpeta del servidor: cd backend",
        "Crear y activar un entorno virtual, e instalar las dependencias: "
        "python -m venv venv  →  venv\\Scripts\\activate  →  pip install -r requirements.txt",
        "Crear el archivo de variables de entorno .env en la raíz del backend "
        "(puede copiar .env.example) con las credenciales de conexión y las claves "
        "secretas:",
    ])
    codigo(doc, [
        "FLASK_ENV=development",
        "SECRET_KEY=clave_aleatoria_de_al_menos_32_caracteres",
        "JWT_SECRET_KEY=otra_clave_aleatoria_distinta_de_32_caracteres",
        "DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/inmobiliaria_db",
        "FRONTEND_URL=http://localhost:3000",
        "BACKEND_URL=http://localhost:5000",
    ])
    pasos(doc, [
        "Ejecutar el seed inicial para crear el usuario administrador y los "
        "criterios por defecto: python seed.py",
        "Iniciar el servidor backend: python run.py "
        "(quedará a la escucha en el puerto 5000).",
    ])
    parrafo(doc,
            "El seed crea un usuario administrador de prueba: "
            "admin@inmobiliaria.com / Admin@2026 (cambiar en producción).",
            italic=True, size=10, color=GRIS)

    doc.add_heading("Paso 4: Despliegue del Frontend (cliente web)", level=3)
    pasos(doc, [
        "Abrir una nueva terminal y navegar a la carpeta del cliente: cd frontend",
        "Instalar las dependencias: npm install",
        "Crear el archivo .env del cliente apuntando a la API:",
    ])
    codigo(doc, ["VITE_API_URL=http://localhost:5000/api"])
    pasos(doc, [
        "Iniciar el entorno de desarrollo: npm run dev "
        "(la aplicación se abrirá en el puerto 3000, con proxy a la API en el 5000).",
        "Para generar la versión de producción: npm run build",
    ])

    # Seguridad
    doc.add_heading("Seguridad Mínima Aplicada", level=2)
    parrafo(doc,
            "El entorno de despliegue cuenta con las siguientes políticas de "
            "seguridad técnica activas:")
    vinetas(doc, [
        ("Autenticación con JWT: ",
         "las sesiones son sin estado (stateless). Tras autenticarse, el sistema "
         "emite un access token (vigencia 8 horas) y un refresh token (30 días) que "
         "el frontend adjunta en la cabecera Authorization: Bearer de cada petición. "
         "El frontend renueva el access token automáticamente mediante interceptores."),
        ("Segundo factor de autenticación (2FA): ",
         "además de usuario y contraseña, el acceso exige un código temporal (TOTP) "
         "de Google Authenticator, mitigando el riesgo de credenciales comprometidas."),
        ("Cifrado de credenciales: ",
         "las contraseñas se almacenan con el algoritmo de hashing scrypt con sal "
         "(werkzeug.security), impidiendo su lectura directa. El secreto TOTP del "
         "2FA se guarda de forma protegida."),
        ("Principio de mínimo privilegio: ",
         "la aplicación se conecta a PostgreSQL con un usuario de servicio restringido "
         "(no se usan superusuarios). Además, el control de acceso por roles "
         "(propietario, administrador, comercial) se re-verifica en el backend "
         "mediante decoradores de autorización."),
        ("Aislamiento multi-inquilino: ",
         "cada operación filtra los datos por empresa, de modo que un usuario solo "
         "accede a la información de su propia organización (salvo el propietario)."),
        ("Protección CORS: ",
         "el backend está configurado con Cross-Origin Resource Sharing para "
         "controlar los orígenes de las peticiones."),
        ("Protección de variables de entorno: ",
         "los archivos .env (cadenas de conexión y claves secretas) están excluidos "
         "del control de versiones mediante .gitignore, evitando exponer credenciales."),
        ("Trazabilidad y auditoría: ",
         "los eventos críticos (inicios de sesión, reseteos de 2FA, evaluaciones, "
         "cambios de contraseña, operaciones de facturación) se registran en una "
         "bitácora de auditoría con usuario, módulo, entidad y resultado."),
    ])
    parrafo(doc, "Credenciales de evaluación (para la defensa): "
                 "admin@inmobiliaria.com / Admin@2026.", italic=True, size=10,
            color=GRIS)

    doc.save(ruta)
    return ruta


# ════════════════════════════════════════════════════════════════════
#  2) MANUAL DE USUARIO (completado según la guía)
# ════════════════════════════════════════════════════════════════════
def generar_manual_usuario(ruta):
    doc = Document()
    set_base_style(doc)

    portada(doc, "MANUAL DE USUARIO",
            "Dirigido al usuario final del sistema "
            "(personal operativo, administrativo y gerencial)")

    doc.add_heading("Manual de Usuario", level=1)

    # 1. Introducción
    doc.add_heading("Introducción", level=2)
    parrafo(doc,
            "El presente manual tiene como propósito guiar al usuario final en el uso "
            "correcto del Sistema Experto Web de Scoring, una aplicación orientada a "
            "apoyar la toma de decisiones en el análisis de riesgo de clientes en "
            "inmobiliarias. El documento explica paso a paso cómo acceder al sistema, "
            "navegar por sus módulos y ejecutar las operaciones diarias de manera "
            "eficiente y segura.")
    doc.add_heading("Roles del sistema", level=3)
    vinetas(doc, [
        ("Propietario: ", "acceso total; administra las empresas clientes, los planes "
         "de facturación y la configuración general del sistema."),
        ("Administrador: ", "gestiona los usuarios, los modelos de scoring y los "
         "criterios de su propia empresa."),
        ("Comercial: ", "registra clientes, ejecuta evaluaciones y consulta reportes."),
    ])

    # 2. Requisitos
    doc.add_heading("Requisitos Básicos de Operación", level=2)
    parrafo(doc,
            "Al ser una aplicación web, el sistema no requiere instalar programas "
            "adicionales. Para operarlo de manera óptima, el usuario solo necesita:")
    vinetas(doc, [
        "Una computadora con sistema operativo Windows, macOS o Linux.",
        "Conexión estable a internet.",
        "Un navegador web moderno y actualizado (se recomienda Google Chrome, "
        "Microsoft Edge o Mozilla Firefox).",
        "Credenciales de acceso (correo y contraseña) proporcionadas por el "
        "administrador.",
        "La aplicación Google Authenticator instalada en el teléfono (para el segundo "
        "factor de autenticación).",
    ])

    # 3. Acceso al sistema
    doc.add_heading("Acceso al Sistema y Autenticación en Dos Pasos (2FA)", level=2)

    doc.add_heading("Ingresar al sistema", level=3)
    pasos(doc, [
        "Abrir el navegador e ingresar a la dirección (URL) del sistema proporcionada "
        "por el administrador.",
        "Escribir el correo electrónico y la contraseña.",
        "Hacer clic en el botón Iniciar sesión.",
    ])
    figura(doc, "Pantalla de inicio de sesión",
           "Pantalla de acceso al sistema. El usuario ingresa su correo electrónico y "
           "contraseña y presiona «Iniciar sesión». Incluye además la opción "
           "«¿Olvidó su contraseña?».")
    parrafo(doc,
            "Nota de seguridad: si el sistema indica «Credenciales incorrectas», "
            "verifique que el correo y la contraseña sean correctos. Si no recuerda su "
            "contraseña, utilice la opción «¿Olvidó su contraseña?». Si su usuario "
            "aparece desactivado, comuníquese con su administrador.",
            italic=True, size=10, color=GRIS)

    doc.add_heading("Configurar el 2FA por primera vez", level=3)
    pasos(doc, [
        "Al ingresar por primera vez, el sistema muestra un código QR.",
        "Abrir Google Authenticator en el teléfono y escanear el código QR.",
        "Ingresar el código de 6 dígitos que muestra la aplicación.",
        "Confirmar para activar el 2FA.",
    ])
    figura(doc, "Configuración del 2FA (código QR)",
           "Pantalla de configuración del segundo factor. El sistema muestra un código "
           "QR que el usuario escanea con Google Authenticator y luego ingresa el "
           "código de 6 dígitos para activarlo.")

    doc.add_heading("Ingresar el código 2FA en cada inicio de sesión", level=3)
    pasos(doc, [
        "Luego del correo y la contraseña, el sistema solicita el código de 6 dígitos.",
        "Abrir Google Authenticator y copiar el código vigente.",
        "Ingresar el código y confirmar para acceder al sistema.",
    ])
    figura(doc, "Ingreso del código 2FA",
           "El usuario copia el código vigente de Google Authenticator, lo ingresa en "
           "el campo de verificación y presiona «Verificar» para acceder al sistema.")

    # 4. Entorno de trabajo y navegación  (SECCIÓN NUEVA - pedida por el profe)
    doc.add_heading("Entorno de Trabajo y Navegación", level=2)
    parrafo(doc,
            "Una vez iniciada la sesión, el sistema muestra el Panel Principal "
            "(Dashboard). La pantalla se divide en las siguientes áreas clave:")
    vinetas(doc, [
        ("Menú lateral (navegación): ",
         "ubicado a la izquierda. Contiene los accesos a todos los módulos permitidos "
         "para su rol (Dashboard, Clientes, Evaluaciones, Scoring Riesgo, Reportes, "
         "Facturación, Seguridad, Auditoría y, para el propietario, Empresas Clientes "
         "y Usuarios)."),
        ("Área de usuario: ",
         "en la parte inferior del menú lateral se muestra el nombre del usuario, su "
         "rol y el botón «Cerrar sesión»."),
        ("Área de trabajo: ",
         "es la zona central y más amplia de la pantalla, donde se cargan los "
         "formularios, las tablas de datos y los resultados."),
    ])
    parrafo(doc,
            "Según el rol del usuario, el menú lateral oculta automáticamente los "
            "módulos a los que no tiene acceso.", italic=True, size=10, color=GRIS)
    figura(doc, "Panel principal (Dashboard) y menú lateral",
           "Pantalla de inicio que muestra un resumen del sistema (clientes activos, "
           "evaluaciones realizadas y clientes por nivel de riesgo) y, a la izquierda, "
           "el menú lateral de navegación.")

    # 5. Gestión de clientes
    doc.add_heading("Gestión de Clientes", level=2)
    doc.add_heading("Registrar un nuevo cliente", level=3)
    pasos(doc, [
        "En el menú lateral, seleccionar Clientes.",
        "Hacer clic en el botón «+ Nuevo cliente».",
        "Completar los campos del formulario: tipo y número de documento (DNI, RUC o "
        "CE), nombre, apellido, correo, teléfono, nacionalidad, dirección y fecha de "
        "nacimiento.",
        "Hacer clic en Registrar para guardar el cliente.",
    ])
    figura(doc, "Formulario de nuevo cliente",
           "Ventana «Nuevo cliente» con los campos a completar. Al seleccionar la "
           "nacionalidad se habilitan los campos de departamento y ciudad. Con "
           "«Registrar» se guarda el cliente.")

    doc.add_heading("Consultar, editar o dar de baja un cliente", level=3)
    pasos(doc, [
        "En la lista de clientes, ubicar el cliente deseado (puede usar el buscador).",
        "Usar el botón Ver para consultar o el botón de edición para modificar los "
        "datos.",
        "La baja de un cliente es lógica: queda inactivo, no se elimina físicamente.",
    ])
    figura(doc, "Listado de clientes",
           "Tabla de clientes registrados con su documento, tipo, nombre, correo, "
           "teléfono y estado, junto con el buscador y las acciones de cada fila.")

    # 6. Evaluación
    doc.add_heading("Evaluar el Riesgo de un Cliente", level=2)
    parrafo(doc,
            "Este es el proceso central del sistema. Permite calcular el puntaje "
            "(score) del cliente y obtener su clasificación de riesgo (bajo, medio, "
            "alto o rechazado).")
    pasos(doc, [
        "En el menú, seleccionar Evaluaciones y hacer clic en «+ Nueva evaluación».",
        "Seleccionar el cliente a evaluar. El sistema verifica automáticamente si "
        "aparece en las listas de sanciones internacionales (ONU/OFAC).",
        "Seleccionar el modelo de scoring y el tipo de persona.",
        "Completar los valores de los factores de evaluación (ingresos, "
        "endeudamiento, historial de pagos, antigüedad laboral, patrimonio, etc.).",
        "Hacer clic en Ejecutar evaluación.",
        "El sistema aplica las reglas y muestra el resultado con el puntaje, la "
        "clasificación de riesgo y una explicación de los factores que más influyeron.",
    ])
    parrafo(doc,
            "Si el cliente aparece en las listas de sanciones, se clasifica "
            "automáticamente como riesgo alto, independientemente del puntaje obtenido.")
    figura(doc, "Resultado de la evaluación",
           "Pantalla de resultado que muestra el cliente, el score total, la "
           "clasificación de riesgo, el análisis del sistema y el detalle de los "
           "factores favorables y desfavorables. Con «Descargar PDF» se exporta el "
           "reporte.")

    # 7. Configuración (admin)
    doc.add_heading("Configurar Modelo, Reglas y Criterios (Administrador)", level=2)
    parrafo(doc,
            "Disponible para administradores y propietario. Permite definir los "
            "factores, las reglas IF-THEN, los pesos y los umbrales que usa el motor "
            "de scoring.")
    pasos(doc, [
        "En el menú, seleccionar Scoring Riesgo.",
        "Consultar el modelo activo con «Ver factores» o crear/editar un modelo.",
        "Agregar o editar factores (por ejemplo, ingresos, historial de pagos, "
        "endeudamiento) y definir sus reglas y pesos.",
        "Establecer los umbrales de clasificación (bajo, medio, alto).",
        "Guardar los cambios.",
    ])
    figura(doc, "Detalle del modelo de scoring",
           "Vista de detalle del modelo con los umbrales de clasificación y la lista "
           "de factores, su categoría (principal o complementario) y la cantidad de "
           "reglas IF-THEN asociadas a cada uno.")

    # 8. Reportes
    doc.add_heading("Reportes", level=2)
    pasos(doc, [
        "En el menú, seleccionar Reportes.",
        "Filtrar las evaluaciones por fecha desde, fecha hasta y resultado, y "
        "presionar Buscar.",
        "Abrir una evaluación y usar la opción Exportar PDF para descargar el reporte.",
    ])
    figura(doc, "Reportes y exportación a PDF",
           "Pantalla «Reportes» con los filtros y la tabla de evaluaciones "
           "encontradas. El botón «Exportar PDF» genera el reporte.")

    # 9. Usuarios / Empresas
    doc.add_heading("Gestión de Usuarios y Empresas", level=2)
    doc.add_heading("Gestión de usuarios (Administrador / Propietario)", level=3)
    pasos(doc, [
        "En el menú, seleccionar Usuarios.",
        "Usar «Nuevo usuario» para crear una cuenta, asignándole su rol "
        "(administrador o comercial).",
        "Editar o desactivar usuarios existentes según corresponda.",
    ])
    figura(doc, "Gestión de usuarios",
           "Pantalla de usuarios con el listado de cuentas, su rol y estado, y las "
           "opciones para crear, editar o desactivar.")

    doc.add_heading("Gestión de empresas (Propietario)", level=3)
    parrafo(doc,
            "Exclusivo del propietario. Permite administrar las empresas (inmobiliarias) "
            "que utilizan el sistema. Cada empresa accede únicamente a sus propios "
            "clientes, evaluaciones y configuraciones.")
    figura(doc, "Gestión de empresas (Propietario)",
           "Pantalla «Empresas Clientes» que lista las inmobiliarias con su nombre, "
           "RUC, cantidad de usuarios y estado. Con «+ Nueva Empresa» se registra una "
           "nueva y con «Ver / Usuarios» se gestionan sus usuarios.")

    # 10. Avisos y mensajes  (SECCIÓN NUEVA - pedida por el profe)
    doc.add_heading("Avisos y Mensajes del Sistema", level=2)
    parrafo(doc,
            "Durante el uso de la plataforma, el sistema se comunica con el usuario "
            "mediante mensajes (notificaciones) para guiarlo o prevenir errores. Los "
            "más frecuentes son:")
    vinetas(doc, [
        ("Mensaje de éxito (verde): ",
         "confirma que una operación se realizó correctamente, por ejemplo «Cliente "
         "registrado» o «Evaluación ejecutada». No requiere ninguna acción."),
        ("Campos requeridos o incompletos: ",
         "aparece si intenta guardar un formulario sin completar un dato obligatorio. "
         "Solución: revise el formulario, complete los campos resaltados y vuelva a "
         "guardar."),
        ("Datos duplicados: ",
         "aparece si intenta registrar un documento, correo o RUC que ya existe. "
         "Solución: verifique el valor ingresado; si es correcto, el registro ya "
         "existe y puede buscarlo en la tabla."),
        ("Credenciales incorrectas: ",
         "aparece en el login si el correo o la contraseña no coinciden, o el código "
         "2FA es inválido. Solución: verifique sus datos y el código vigente del "
         "authenticator."),
        ("Acceso denegado o sin permisos: ",
         "aparece si intenta realizar una acción para la cual su rol no tiene "
         "autorización. Solución: solicite la tarea a un usuario con rol de "
         "administrador o propietario."),
        ("Sesión expirada: ",
         "por seguridad, la sesión caduca tras un período de inactividad. Solución: "
         "vuelva a iniciar sesión."),
    ])
    figura(doc, "Ejemplos de mensajes del sistema",
           "Ejemplos visuales de las notificaciones de éxito y de error que muestra la "
           "aplicación en la esquina de la pantalla.")

    # 11. Auditoría
    doc.add_heading("Consultar la Auditoría", level=2)
    parrafo(doc,
            "El módulo de Auditoría (disponible para administradores y propietario) "
            "muestra la bitácora de las operaciones realizadas en el sistema: quién "
            "realizó cada acción, de qué tipo, cuándo y con qué resultado. Permite "
            "filtrar los registros por fecha, tipo de evento, resultado, acción, "
            "módulo y, para el propietario, por empresa.")
    figura(doc, "Auditoría del sistema",
           "Pantalla «Auditoría» con la bitácora de operaciones y sus filtros. Cada "
           "registro indica la fecha y hora, el usuario, el tipo, la acción, la "
           "entidad, la empresa y el resultado (éxito o fallo).")

    # 12. Seguridad de la cuenta
    doc.add_heading("Seguridad de la Cuenta", level=2)
    doc.add_heading("Cambiar contraseña", level=3)
    pasos(doc, [
        "Ingresar a la sección de seguridad o perfil.",
        "Ingresar la contraseña actual y la nueva contraseña (mínimo 8 caracteres).",
        "Confirmar el cambio.",
    ])
    doc.add_heading("Recuperar contraseña", level=3)
    parrafo(doc,
            "Si olvidó su contraseña, use la opción «¿Olvidó su contraseña?» en la "
            "pantalla de inicio de sesión. Deberá ingresar su correo, el código de 6 "
            "dígitos de Google Authenticator y definir una nueva contraseña. Esta "
            "opción solo funciona si ya tiene el 2FA activado.")
    figura(doc, "Recuperar contraseña",
           "Pantalla «Recuperar contraseña». El usuario verifica su identidad "
           "ingresando su correo y el código de Google Authenticator, y luego define y "
           "confirma una nueva contraseña.")

    doc.add_heading("Cerrar sesión", level=3)
    parrafo(doc,
            "Al finalizar su trabajo, cierre la sesión para evitar que terceros "
            "accedan a la información.")
    pasos(doc, [
        "En la parte inferior del menú lateral, hacer clic en «Cerrar sesión».",
        "El sistema lo redirigirá a la pantalla de inicio, confirmando que la sesión "
        "finalizó de forma segura.",
    ])
    figura(doc, "Cerrar sesión",
           "Ubicación del botón «Cerrar sesión» en la parte inferior del menú lateral.")

    doc.save(ruta)
    return ruta


if __name__ == "__main__":
    t = generar_manual_tecnico(os.path.join(AQUI, "Manual_Tecnico.docx"))
    u = generar_manual_usuario(os.path.join(AQUI, "Manual_de_Usuario.docx"))
    print("Generado:", t)
    print("Generado:", u)
