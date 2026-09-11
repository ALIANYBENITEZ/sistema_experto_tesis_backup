"""
Script de semilla: crea el usuario administrador inicial y criterios por defecto.
Ejecutar UNA sola vez después de crear las tablas.

    python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import User, Criterion


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ── Usuario admin ──────────────────────────────────────────────────
        if not User.query.filter_by(email="admin@inmobiliaria.com").first():
            admin = User(
                nombre   = "Administrador",
                apellido = "Sistema",
                email    = "admin@inmobiliaria.com",
                rol      = User.ROL_ADMIN,
            )
            admin.set_password("Admin@2026")
            db.session.add(admin)
            print("✓ Usuario administrador creado: admin@inmobiliaria.com / Admin@2026")
        else:
            print("! Usuario administrador ya existe, se omite.")

        # ── Criterios por defecto ──────────────────────────────────────────
        criterios_default = [
            ("Capacidad de Pago",    "Relación cuota/ingreso mensual",             25.00),
            ("Historial Crediticio", "Antecedentes financieros del cliente",       25.00),
            ("Estabilidad Laboral",  "Tiempo y tipo de relación laboral",          20.00),
            ("Documentación",        "Completitud y validez de documentos",        15.00),
            ("Patrimonio",           "Bienes y activos declarados por el cliente", 15.00),
        ]

        for nombre, desc, peso in criterios_default:
            if not Criterion.query.filter_by(nombre=nombre).first():
                db.session.add(Criterion(nombre=nombre, descripcion=desc, peso=peso))
                print(f"✓ Criterio creado: {nombre} ({peso}%)")
            else:
                print(f"! Criterio ya existe: {nombre}")

        db.session.commit()
        print("\n✅ Seed completado exitosamente.")


if __name__ == "__main__":
    seed()
