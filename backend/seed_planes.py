"""Seed: Crear planes comerciales iniciales."""
from app import create_app
from app.extensions import db
from app.models.facturacion import Plan

app = create_app()
with app.app_context():
    db.create_all()
    print("OK: Tablas de facturación creadas")

    if Plan.query.count() > 0:
        print("! Planes ya existen, se omite.")
    else:
        planes = [
            Plan(nombre="Bronce", cantidad_reportes_incluidos=15, precio_plan=150000,
                 precio_reporte_incluido=10000, precio_reporte_sobre_facturado=12000),
            Plan(nombre="Plata", cantidad_reportes_incluidos=30, precio_plan=270000,
                 precio_reporte_incluido=9000, precio_reporte_sobre_facturado=10000),
            Plan(nombre="Oro", cantidad_reportes_incluidos=50, precio_plan=400000,
                 precio_reporte_incluido=8000, precio_reporte_sobre_facturado=8000),
        ]
        db.session.add_all(planes)
        db.session.commit()
        print("✅ Planes creados: Bronce (15), Plata (30), Oro (50)")
