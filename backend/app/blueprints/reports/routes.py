from datetime import datetime, timedelta
from io import BytesIO
from flask import request, send_file
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Client, User
from app.core.models import EvaluacionScoring
from app.utils.responses import success, error
from . import reports_bp


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _build_query(args):
    from app.utils.decorators import get_current_user
    current_user = get_current_user()

    query = EvaluacionScoring.query

    # Filtrar por empresa (propietario ve todo)
    if not current_user.is_propietario():
        query = query.filter_by(id_empresa=current_user.id_empresa)

    fecha_from = _parse_date(args.get("fecha_from"))
    fecha_to = _parse_date(args.get("fecha_to"))
    clasificacion = args.get("resultado") or args.get("categoria")
    usuario_id = args.get("evaluador_id", type=int)

    if fecha_from:
        query = query.filter(EvaluacionScoring.fecha >= fecha_from)
    if fecha_to:
        # Incluir todo el día final (hasta las 23:59:59)
        fecha_to_end = fecha_to + timedelta(days=1)
        query = query.filter(EvaluacionScoring.fecha < fecha_to_end)
    if clasificacion:
        query = query.filter_by(clasificacion=clasificacion)
    if usuario_id:
        query = query.filter_by(usuario_id=usuario_id)

    return query.order_by(EvaluacionScoring.fecha.desc())


@reports_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """Resumen estadístico para el dashboard."""
    from app.utils.decorators import get_current_user
    from app.models.cliente_empresa import ClienteEmpresa
    current_user = get_current_user()

    # Base query de evaluaciones filtrada por empresa
    if current_user.is_propietario():
        eval_query = EvaluacionScoring.query
    else:
        eval_query = EvaluacionScoring.query.filter_by(id_empresa=current_user.id_empresa)

    total = eval_query.count()
    bajo = eval_query.filter_by(clasificacion="bajo").count()
    medio = eval_query.filter_by(clasificacion="medio").count()
    alto = eval_query.filter_by(clasificacion="alto").count()
    rechazados = eval_query.filter_by(clasificacion="rechazado").count()

    # Contar clientes según empresa
    if current_user.is_propietario():
        clientes = Client.query.filter_by(estado="activo").count()
    else:
        clientes = db.session.query(ClienteEmpresa).filter_by(
            id_empresa=current_user.id_empresa, estado="activo"
        ).count()

    return success(data={
        "total_evaluaciones": total,
        "bajo_riesgo": bajo,
        "medio_riesgo": medio,
        "alto_riesgo": alto,
        "rechazados": rechazados,
        "total_clientes": clientes,
    })


@reports_bp.route("/evaluations", methods=["GET"])
@jwt_required()
def list_report():
    """Listado filtrado de evaluaciones de riesgo para reporte."""
    from app.utils.decorators import get_current_user
    from app.models import Empresa
    current_user = get_current_user()

    query = _build_query(request.args)
    evals = query.all()

    # Mapa de empresas para mostrar el nombre (solo relevante para propietario)
    empresas = {e.id: e.nombre for e in Empresa.query.all()}

    rows = []
    for ev in evals:
        client = Client.query.get(ev.cliente_id)

        if ev.id_empresa == 0:
            empresa_nombre = "Sistema"
        else:
            empresa_nombre = empresas.get(ev.id_empresa, "—")

        rows.append({
            "id": ev.id,
            "fecha": ev.fecha.strftime("%d/%m/%Y %H:%M") if ev.fecha else "",
            "cliente": f"{client.nombre} {client.apellido or ''}".strip() if client else "N/A",
            "num_doc": client.num_doc if client else "",
            "puntaje_total": float(ev.score_total) if ev.score_total is not None else 0,
            "tipo_persona": ev.tipo_persona,
            "resultado": ev.clasificacion,
            "modelo": ev.modelo_version,
            "estado": ev.estado,
            "id_empresa": ev.id_empresa,
            "empresa": empresa_nombre,
        })

    return success(data={
        "items": rows,
        "total": len(rows),
        "es_propietario": current_user.is_propietario(),
    })


@reports_bp.route("/evaluations/pdf", methods=["GET"])
@jwt_required()
def export_pdf():
    """Genera PDF del reporte de evaluaciones de riesgo."""
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
    except ImportError:
        return error("reportlab no está instalado. Ejecute: pip install reportlab", 500)

    from app.utils.decorators import get_current_user
    from app.models import Empresa
    current_user = get_current_user()
    es_propietario = current_user.is_propietario()

    query = _build_query(request.args)
    evals = query.all()

    empresas = {e.id: e.nombre for e in Empresa.query.all()} if es_propietario else {}

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    elements = []

    # Título
    elements.append(Paragraph("Reporte de Evaluaciones de Riesgo", styles["Title"]))
    elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    # Tabla — el propietario ve una columna extra con la empresa cliente
    if es_propietario:
        headers = ["#", "Fecha", "Empresa", "Cliente", "N° Doc", "Tipo", "Score", "Clasificación", "Estado"]
        col_widths = [1 * cm, 2.6 * cm, 4 * cm, 5.5 * cm, 3 * cm, 1.8 * cm, 2 * cm, 3 * cm, 2.3 * cm]
    else:
        headers = ["#", "Fecha", "Cliente", "N° Doc", "Tipo", "Score", "Clasificación", "Estado"]
        col_widths = [1.2 * cm, 2.8 * cm, 7 * cm, 3.2 * cm, 2 * cm, 2.2 * cm, 3.2 * cm, 2.5 * cm]
    data = [headers]

    COLORES_CATEGORIA = {
        "bajo": colors.HexColor("#d4edda"),
        "medio": colors.HexColor("#fff3cd"),
        "alto": colors.HexColor("#f8d7da"),
        "rechazado": colors.HexColor("#f5c6cb"),
    }

    row_colors = []
    for i, ev in enumerate(evals, start=1):
        client = Client.query.get(ev.cliente_id)
        nombre = f"{client.nombre} {client.apellido or ''}".strip() if client else "N/A"

        fila = [
            str(ev.id),
            ev.fecha.strftime("%d/%m/%Y") if ev.fecha else "",
        ]
        if es_propietario:
            empresa_nombre = "Sistema" if ev.id_empresa == 0 else empresas.get(ev.id_empresa, "—")
            fila.append(empresa_nombre)
        fila += [
            nombre,
            client.num_doc if client else "",
            ev.tipo_persona or "",
            str(round(float(ev.score_total), 1)) if ev.score_total is not None else "0",
            (ev.clasificacion or "").upper(),
            ev.estado or "",
        ]
        data.append(fila)
        color = COLORES_CATEGORIA.get(ev.clasificacion, colors.white)
        row_colors.append(("BACKGROUND", (0, i), (-1, i), color))
    table = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ] + row_colors)
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    filename = f"reporte_evaluaciones_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
