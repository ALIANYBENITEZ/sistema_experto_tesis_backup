"""
API del Core de Scoring.
Endpoints para ejecutar evaluaciones, gestionar modelos y generar reportes PDF.
"""
from io import BytesIO
from datetime import datetime
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Client
from app.utils.decorators import get_current_user, propietario_required
from app.utils.responses import success, error
from app.services.auditoria_service import registrar as auditar
from .models import (
    ModeloScoring, FactorScoring, ReglaScoring, CatalogoScoring,
    UmbralScoring, EvaluacionScoring, DetalleEvaluacionScoring,
)
from .engine import ejecutar_evaluacion

core_bp = Blueprint("core", __name__, url_prefix="/api/core")


# ══════════════════════════════════════════════════════════════
#  EJECUTAR EVALUACIÓN
# ══════════════════════════════════════════════════════════════

@core_bp.route("/evaluar", methods=["POST"])
@jwt_required()
def evaluar():
    """
    Ejecuta el Core de Scoring sobre un cliente.

    Body:
    {
        "cliente_id": int,
        "modelo_id": int,
        "tipo_persona": "PF" | "PJ",
        "datos": { "codigo_factor": valor, ... }
    }
    """
    current_user = get_current_user()
    data = request.get_json(silent=True)
    if not data:
        return error("Datos inválidos", 400)

    cliente_id = data.get("cliente_id")
    modelo_id = data.get("modelo_id")
    datos_cliente = data.get("datos", {})

    if not cliente_id:
        return error("cliente_id es requerido", 400)
    if not modelo_id:
        return error("modelo_id es requerido", 400)
    if not datos_cliente:
        return error("Se requieren datos del cliente para evaluar", 400)

    cliente = Client.query.get(cliente_id)
    if not cliente:
        return error("Cliente no encontrado", 404)

    # Determinar tipo de persona automáticamente según tipo de documento
    tipo_persona = data.get("tipo_persona", "").upper()
    if not tipo_persona:
        # Auto-detectar: CI, PAS, DNI = PF | RUC = PJ
        tipo_doc = (cliente.tipo_doc or "").upper()
        if tipo_doc in ("RUC",):
            tipo_persona = "PJ"
        else:
            tipo_persona = "PF"

    if tipo_persona not in ("PF", "PJ"):
        tipo_persona = "PF"

    modelo = ModeloScoring.query.get(modelo_id)
    if not modelo:
        return error("Modelo de scoring no encontrado", 404)
    if not modelo.activo:
        return error("El modelo de scoring no está activo", 400)

    # Ejecutar el Core
    resultado = ejecutar_evaluacion(modelo, datos_cliente, tipo_persona, cliente_obj=cliente)

    # Guardar evaluación
    evaluacion = EvaluacionScoring(
        cliente_id=cliente_id,
        modelo_id=modelo_id,
        modelo_version=resultado["modelo_version"],
        usuario_id=current_user.id,
        id_empresa=current_user.id_empresa or 0,
        tipo_persona=tipo_persona,
        score_total=resultado["score_total"],
        clasificacion=resultado["clasificacion"],
        explicacion=resultado["explicacion"],
        factores_evaluados=resultado["factores_evaluados"],
        factores_sin_dato=resultado["factores_sin_dato"],
        estado=resultado["estado"],
    )
    db.session.add(evaluacion)
    db.session.flush()

    # Guardar detalles
    for det in resultado["detalles"]:
        detalle = DetalleEvaluacionScoring(
            evaluacion_id=evaluacion.id,
            factor_codigo=det["factor_codigo"],
            factor_nombre=det["factor_nombre"],
            categoria=det["categoria"],
            valor_original=det["valor_original"],
            estado=det["estado"],
            regla_aplicada=det["regla_aplicada"],
            nivel=det["nivel"],
            peso=det["peso"],
            explicacion=det["explicacion"],
        )
        db.session.add(detalle)

    # ── Registrar consumo de reporte (facturación) ──
    info_consumo = None
    if current_user.id_empresa and current_user.id_empresa > 0:
        try:
            from app.services.consumo_service import registrar_consumo_reporte, ConsultasBloqueadasError, SinPlanError
            info_consumo = registrar_consumo_reporte(
                empresa_id=current_user.id_empresa,
                usuario_id=current_user.id,
                evaluacion_id=evaluacion.id,
            )
        except ConsultasBloqueadasError as e:
            db.session.rollback()
            return error(str(e), 403)
        except SinPlanError as e:
            # Si no tiene plan, igual permitir la evaluación (propietario puede no tener plan)
            pass
        except Exception:
            pass  # No bloquear evaluación por error de facturación

    db.session.commit()

    auditar("EVALUACIONES", "EJECUCION_EVALUACION", usuario=current_user, modulo="Evaluaciones",
            entidad="Evaluacion", registro_id=evaluacion.id, resultado="EXITO",
            info={"cliente_id": cliente_id, "cliente_num_doc": cliente.num_doc,
                  "modelo_id": modelo_id, "tipo_persona": tipo_persona,
                  "score_total": resultado["score_total"],
                  "clasificacion": resultado["clasificacion"]})

    # Respuesta
    resp = evaluacion.to_dict(include_detalles=True)
    resp["impacto"] = resultado["impacto"]
    resp["lista_negra"] = resultado.get("lista_negra")
    resp["cliente_nombre"] = f"{cliente.nombre} {cliente.apellido or ''}".strip()
    resp["cliente_num_doc"] = cliente.num_doc

    return success(data=resp, message="Evaluación completada", status=201)


@core_bp.route("/evaluaciones", methods=["GET"])
@jwt_required()
def list_evaluaciones():
    current_user = get_current_user()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    clasificacion = request.args.get("clasificacion")

    query = EvaluacionScoring.query
    if not current_user.is_propietario():
        query = query.filter_by(id_empresa=current_user.id_empresa)
    if clasificacion:
        query = query.filter_by(clasificacion=clasificacion)

    query = query.order_by(EvaluacionScoring.fecha.desc())
    pag = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for ev in pag.items:
        d = ev.to_dict()
        c = Client.query.get(ev.cliente_id)
        if c:
            d["cliente_nombre"] = f"{c.nombre} {c.apellido or ''}".strip()
            d["num_doc"] = c.num_doc
        items.append(d)

    return success(data={
        "items": items,
        "total": pag.total,
        "page": pag.page,
        "pages": pag.pages,
    })


@core_bp.route("/evaluaciones/<int:eval_id>", methods=["GET"])
@jwt_required()
def get_evaluacion(eval_id):
    ev = EvaluacionScoring.query.get_or_404(eval_id)
    data = ev.to_dict(include_detalles=True)
    c = Client.query.get(ev.cliente_id)
    if c:
        data["cliente_nombre"] = f"{c.nombre} {c.apellido or ''}".strip()
        data["cliente_num_doc"] = c.num_doc
        data["cliente_email"] = c.email
    # Recalcular impacto desde detalles
    from .explainer import identificar_factores_impacto
    data["impacto"] = identificar_factores_impacto(data["detalles"])
    return success(data=data)


# ══════════════════════════════════════════════════════════════
#  REPORTE PDF DE EVALUACIÓN
# ══════════════════════════════════════════════════════════════

@core_bp.route("/evaluaciones/<int:eval_id>/pdf", methods=["GET"])
@jwt_required()
def export_evaluacion_pdf(eval_id):
    """Genera un PDF detallado de la evaluación con diseño profesional."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
            HRFlowable, KeepTogether,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        return error("reportlab no instalado", 500)

    ev = EvaluacionScoring.query.get_or_404(eval_id)
    cliente = Client.query.get(ev.cliente_id)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()

    # Estilos personalizados
    styles.add(ParagraphStyle('TituloReporte', parent=styles['Title'], fontSize=18,
                              textColor=colors.HexColor("#1e3a5f"), spaceAfter=6))
    styles.add(ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=13,
                              textColor=colors.HexColor("#2563eb"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle('Info', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor("#555")))
    styles.add(ParagraphStyle('Explicacion', parent=styles['Normal'], fontSize=9,
                              textColor=colors.HexColor("#333"), leading=13))

    elements = []

    # ── HEADER ──
    elements.append(Paragraph("Reporte de Evaluación de Riesgo", styles['TituloReporte']))
    elements.append(Paragraph("Sistema Experto de Scoring Comercial", styles['Info']))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb")))
    elements.append(Spacer(1, 0.5*cm))

    # ── DATOS GENERALES ──
    COLORES_NIVEL = {"bajo": "#16a34a", "medio": "#ca8a04", "alto": "#dc2626"}
    color_clasif = COLORES_NIVEL.get(ev.clasificacion, "#333")

    info_data = [
        ["Evaluación N°:", str(ev.id), "Fecha:", ev.fecha.strftime("%d/%m/%Y %H:%M") if ev.fecha else ""],
        ["Cliente:", f"{cliente.nombre} {cliente.apellido or ''}" if cliente else "N/A",
         "Documento:", cliente.num_doc if cliente else ""],
        ["Tipo persona:", ev.tipo_persona, "Modelo:", f"{ev.modelo_version}"],
        ["Score total:", f"{ev.score_total:.1f} pts", "Clasificación:",
         ev.clasificacion.upper()],
    ]
    t = Table(info_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    t.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    # ── RESULTADO ──
    elements.append(Paragraph("Resultado de la Evaluación", styles['Subtitulo']))
    result_box = Table(
        [[Paragraph(f"<b>RIESGO {ev.clasificacion.upper()}</b>", styles['Normal']),
          Paragraph(f"Score: <b>{ev.score_total:.1f}</b> puntos", styles['Normal']),
          Paragraph(f"Factores evaluados: <b>{ev.factores_evaluados}</b>", styles['Normal'])]],
        colWidths=[6*cm, 5*cm, 6*cm]
    )
    result_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0f9ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#2563eb")),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(result_box)
    elements.append(Spacer(1, 0.4*cm))

    # ── EXPLICACIÓN ──
    if ev.explicacion:
        elements.append(Paragraph("Análisis del Sistema", styles['Subtitulo']))
        elements.append(Paragraph(ev.explicacion, styles['Explicacion']))
        elements.append(Spacer(1, 0.4*cm))

    # ── DETALLE POR FACTOR ──
    elements.append(Paragraph("Detalle por Factor", styles['Subtitulo']))

    headers = ["Factor", "Categoría", "Valor", "Nivel", "Peso", "Estado"]
    table_data = [headers]

    NIVEL_COLORS = {
        "bajo": colors.HexColor("#dcfce7"),
        "medio": colors.HexColor("#fef9c3"),
        "alto": colors.HexColor("#fee2e2"),
    }

    row_styles = []
    for i, det in enumerate(ev.detalles, start=1):
        peso_str = f"{det.peso:+.1f}" if det.peso else "—"
        table_data.append([
            det.factor_nombre,
            (det.categoria or "").capitalize(),
            det.valor_original or "—",
            (det.nivel or "—").upper(),
            peso_str,
            det.estado.replace("_", " ").capitalize(),
        ])
        if det.nivel and det.nivel in NIVEL_COLORS:
            row_styles.append(('BACKGROUND', (3, i), (3, i), NIVEL_COLORS[det.nivel]))

    col_widths = [5*cm, 2.5*cm, 3*cm, 2*cm, 1.8*cm, 2.5*cm]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#ddd")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ] + row_styles))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    # ── EXPLICACIONES POR FACTOR ──
    elements.append(Paragraph("Explicación por Factor", styles['Subtitulo']))
    for det in ev.detalles:
        if det.explicacion and det.estado == "evaluado":
            elements.append(Paragraph(
                f"<b>{det.factor_nombre}:</b> {det.explicacion}", styles['Explicacion']
            ))
            elements.append(Spacer(1, 2*mm))

    elements.append(Spacer(1, 1*cm))

    # ── FOOTER ──
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#ccc")))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
        f"Modelo: {ev.modelo_version} · "
        f"Evaluación #{ev.id}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7,
                       textColor=colors.HexColor("#999"), alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)

    filename = f"evaluacion_riesgo_{ev.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)


# ══════════════════════════════════════════════════════════════
#  VERIFICACIÓN LISTA NEGRA
# ══════════════════════════════════════════════════════════════

@core_bp.route("/verificar-lista-negra/<int:cliente_id>", methods=["GET"])
@jwt_required()
def verificar_cliente_lista_negra(cliente_id):
    """Verifica si un cliente está en la lista negra ONU/OFAC."""
    cliente = Client.query.get_or_404(cliente_id)
    from .lista_negra_checker import verificar_lista_negra
    resultado = verificar_lista_negra(
        nombre=cliente.nombre,
        apellido=cliente.apellido,
        num_doc=cliente.num_doc,
    )
    return success(data=resultado)


# ══════════════════════════════════════════════════════════════
#  MODELOS — CRUD (propietario)
# ══════════════════════════════════════════════════════════════

@core_bp.route("/modelos", methods=["GET"])
@jwt_required()
def list_modelos():
    current_user = get_current_user()
    if current_user.is_propietario():
        modelos = ModeloScoring.query.order_by(ModeloScoring.id).all()
    else:
        modelos = ModeloScoring.query.filter_by(id_empresa=current_user.id_empresa, activo=True).all()
    return success(data=[m.to_dict() for m in modelos])


@core_bp.route("/modelos/<int:modelo_id>", methods=["GET"])
@jwt_required()
def get_modelo(modelo_id):
    modelo = ModeloScoring.query.get_or_404(modelo_id)
    return success(data=modelo.to_dict(include_factores=True))


@core_bp.route("/modelos/<int:modelo_id>", methods=["DELETE"])
@propietario_required
def delete_modelo(modelo_id):
    """
    Elimina el modelo de scoring de una empresa (solo propietario).
    - Si el modelo NO tiene evaluaciones asociadas: borrado físico
      (factores, catálogos, reglas y umbrales caen por cascada).
    - Si tiene evaluaciones: se inactiva (soft-delete) para no romper el
      historial de evaluaciones que lo referencian.
    """
    modelo = ModeloScoring.query.get_or_404(modelo_id)

    nombre = modelo.nombre
    id_empresa = modelo.id_empresa

    tiene_evaluaciones = EvaluacionScoring.query.filter_by(modelo_id=modelo_id).count() > 0

    if tiene_evaluaciones:
        modelo.activo = False
        db.session.commit()
        auditar("EVALUACIONES", "INACTIVACION_MODELO", usuario=get_current_user(), modulo="Scoring",
                entidad="ModeloScoring", registro_id=modelo_id, resultado="EXITO",
                info={"nombre": nombre, "id_empresa": id_empresa, "motivo": "tiene evaluaciones asociadas"})
        return success(message="El modelo tiene evaluaciones asociadas: se desactivó en lugar de eliminarse")

    db.session.delete(modelo)
    db.session.commit()
    auditar("EVALUACIONES", "ELIMINACION_MODELO", usuario=get_current_user(), modulo="Scoring",
            entidad="ModeloScoring", registro_id=modelo_id, resultado="EXITO",
            info={"nombre": nombre, "id_empresa": id_empresa})
    return success(message="Modelo eliminado correctamente")


# Modelo específico que se usa como PLANTILLA BASE para los modelos nuevos.
# Es el modelo "Riesgo Comercial Inmobiliario" de la empresa 1 (id=1).
# Se puede sobreescribir en cada creación pasando "base_modelo_id" en el body.
MODELO_PLANTILLA_ID = 1


def _copiar_estructura_modelo(origen, destino):
    """
    Copia factores (con catálogos y reglas) y umbrales del modelo `origen`
    al modelo `destino`. Devuelve (total_factores, total_reglas).
    """
    total_factores = 0
    total_reglas = 0
    for f in origen.factores.order_by(FactorScoring.orden):
        nf = FactorScoring(
            modelo_id=destino.id,
            codigo=f.codigo,
            nombre=f.nombre,
            descripcion=f.descripcion,
            tipo_dato=f.tipo_dato,
            tipo_persona=f.tipo_persona,
            categoria=f.categoria,
            obligatorio=f.obligatorio,
            activo=f.activo,
            orden=f.orden,
        )
        db.session.add(nf)
        db.session.flush()
        total_factores += 1

        for c in f.catalogo:
            db.session.add(CatalogoScoring(
                factor_id=nf.id, valor=c.valor, etiqueta=c.etiqueta, orden=c.orden,
            ))

        for r in f.reglas:
            db.session.add(ReglaScoring(
                factor_id=nf.id,
                nombre=r.nombre,
                operador=r.operador,
                valor_min=r.valor_min,
                valor_max=r.valor_max,
                nivel=r.nivel,
                peso=r.peso,
                explicacion=r.explicacion,
                orden=r.orden,
            ))
            total_reglas += 1

    for u in origen.umbrales:
        db.session.add(UmbralScoring(
            modelo_id=destino.id,
            nivel=u.nivel,
            score_min=u.score_min,
            score_max=u.score_max,
            descripcion=u.descripcion,
        ))

    return total_factores, total_reglas


@core_bp.route("/modelos", methods=["POST"])
@propietario_required
def create_modelo():
    data = request.get_json(silent=True) or {}
    if not data.get("nombre"):
        return error("Nombre requerido", 400)
    if not data.get("id_empresa"):
        return error("Empresa requerida", 400)

    modelo = ModeloScoring(
        nombre=data["nombre"].strip(),
        version=data.get("version", "1.0").strip(),
        descripcion=data.get("descripcion", "").strip() or None,
        id_empresa=int(data["id_empresa"]),
    )
    db.session.add(modelo)
    db.session.flush()  # obtener modelo.id

    # Base: copiar la estructura del modelo PLANTILLA (id fijo MODELO_PLANTILLA_ID).
    # Se puede indicar otro origen con "base_modelo_id" en el body.
    total_factores = 0
    base_modelo_id = data.get("base_modelo_id") or MODELO_PLANTILLA_ID
    base = ModeloScoring.query.get(int(base_modelo_id))

    # Evitar copiar sobre sí mismo
    if base and base.id != modelo.id:
        total_factores, _ = _copiar_estructura_modelo(base, modelo)

    db.session.commit()
    auditar("EVALUACIONES", "CREACION_MODELO", usuario=get_current_user(), modulo="Scoring",
            entidad="ModeloScoring", registro_id=modelo.id, resultado="EXITO",
            info={"nombre": modelo.nombre, "id_empresa": modelo.id_empresa,
                  "factores_base": total_factores,
                  "base_modelo_id": base.id if base else None})

    msg = "Modelo creado"
    if total_factores:
        msg = f"Modelo creado con {total_factores} factores base"
    return success(data=modelo.to_dict(), message=msg, status=201)


@core_bp.route("/modelos/clonar", methods=["POST"])
@propietario_required
def clonar_modelo():
    """
    Recicla (clona) un modelo existente hacia una empresa destino.
    Copia factores, catálogos, reglas y umbrales.

    Body:
    {
        "origen_id": int,        # modelo a reciclar
        "id_empresa": int,       # empresa destino
        "nombre": str,           # nombre del nuevo modelo (opcional)
        "version": str,          # opcional
        "descripcion": str       # opcional
    }
    """
    data = request.get_json(silent=True) or {}
    origen_id = data.get("origen_id")
    if not origen_id:
        return error("origen_id (modelo a reciclar) es requerido", 400)
    if data.get("id_empresa") is None:
        return error("Empresa destino requerida", 400)

    origen = ModeloScoring.query.get(origen_id)
    if not origen:
        return error("Modelo origen no encontrado", 404)

    id_empresa_destino = int(data["id_empresa"])

    # Crear el nuevo modelo
    nuevo = ModeloScoring(
        nombre=(data.get("nombre") or f"{origen.nombre} (copia)").strip(),
        version=(data.get("version") or origen.version or "1.0").strip(),
        descripcion=(data.get("descripcion") or origen.descripcion),
        id_empresa=id_empresa_destino,
        activo=True,
    )
    db.session.add(nuevo)
    db.session.flush()  # obtener nuevo.id

    # Copiar factores (con catálogos y reglas) y umbrales
    total_factores, total_reglas = _copiar_estructura_modelo(origen, nuevo)

    db.session.commit()

    auditar("EVALUACIONES", "CLONACION_MODELO", usuario=get_current_user(), modulo="Scoring",
            entidad="ModeloScoring", registro_id=nuevo.id, resultado="EXITO",
            info={"origen_id": origen_id, "id_empresa_destino": id_empresa_destino,
                  "factores": total_factores, "reglas": total_reglas})

    return success(data=nuevo.to_dict(),
                   message=f"Modelo reciclado: {total_factores} factores y {total_reglas} reglas copiadas",
                   status=201)


@core_bp.route("/modelos/<int:modelo_id>/factores", methods=["POST"])
@propietario_required
def create_factor(modelo_id):
    ModeloScoring.query.get_or_404(modelo_id)
    data = request.get_json(silent=True) or {}

    required = ["codigo", "nombre", "tipo_dato"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    factor = FactorScoring(
        modelo_id=modelo_id,
        codigo=data["codigo"].strip(),
        nombre=data["nombre"].strip(),
        descripcion=data.get("descripcion", "").strip() or None,
        tipo_dato=data["tipo_dato"],
        tipo_persona=data.get("tipo_persona", "AMBOS"),
        categoria=data.get("categoria", "principal"),
        obligatorio=data.get("obligatorio", True),
        orden=data.get("orden", 0),
    )
    db.session.add(factor)
    db.session.commit()
    return success(data=factor.to_dict(include_reglas=True), message="Factor creado", status=201)


@core_bp.route("/factores/<int:factor_id>/reglas", methods=["POST"])
@propietario_required
def create_regla(factor_id):
    factor = FactorScoring.query.get_or_404(factor_id)
    data = request.get_json(silent=True) or {}

    required = ["nombre", "operador", "nivel", "peso"]
    missing = [f for f in required if data.get(f) is None]
    if missing:
        return error(f"Campos requeridos: {', '.join(missing)}", 400)

    regla = ReglaScoring(
        factor_id=factor_id,
        nombre=data["nombre"].strip(),
        operador=data["operador"],
        valor_min=str(data.get("valor_min", "")).strip() or None,
        valor_max=str(data.get("valor_max", "")).strip() or None,
        nivel=data["nivel"],
        peso=float(data["peso"]),
        explicacion=data.get("explicacion", "").strip() or None,
        orden=data.get("orden", 0),
    )
    db.session.add(regla)
    db.session.commit()
    return success(data=regla.to_dict(), message="Regla creada", status=201)


@core_bp.route("/modelos/<int:modelo_id>/umbrales", methods=["POST"])
@propietario_required
def create_umbral(modelo_id):
    ModeloScoring.query.get_or_404(modelo_id)
    data = request.get_json(silent=True) or {}

    umbral = UmbralScoring(
        modelo_id=modelo_id,
        nivel=data.get("nivel", "bajo"),
        score_min=float(data.get("score_min", 0)),
        score_max=float(data.get("score_max", 0)),
        descripcion=data.get("descripcion", "").strip() or None,
    )
    db.session.add(umbral)
    db.session.commit()
    return success(data=umbral.to_dict(), message="Umbral creado", status=201)
