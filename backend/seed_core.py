"""
Seed del Core de Scoring — Modelo de ejemplo para inmobiliaria.
Ejecutar: python seed_core.py
"""
from app import create_app
from app.extensions import db
from app.core.models import ModeloScoring, FactorScoring, ReglaScoring, UmbralScoring, CatalogoScoring

app = create_app()
with app.app_context():
    # Verificar si ya existe
    if ModeloScoring.query.filter_by(nombre="Riesgo Comercial Inmobiliario").first():
        print("! Modelo ya existe, se omite.")
    else:
        # Crear modelo
        modelo = ModeloScoring(
            nombre="Riesgo Comercial Inmobiliario",
            version="1.0",
            descripcion="Modelo de evaluación de riesgo comercial para clientes de inmobiliarias. "
                        "Evalúa capacidad financiera, historial y perfil del solicitante.",
            id_empresa=1,  # Ajustar según empresa
        )
        db.session.add(modelo)
        db.session.flush()

        # ── FACTORES PRINCIPALES ──────────────────────────────────────

        # 1. Ingresos mensuales
        f1 = FactorScoring(modelo_id=modelo.id, codigo="ingresos_mensuales",
            nombre="Ingresos Mensuales", descripcion="Ingresos netos mensuales del cliente en guaraníes.",
            tipo_dato="numerico", tipo_persona="AMBOS", categoria="principal", obligatorio=True, orden=1)
        db.session.add(f1)
        db.session.flush()
        db.session.add_all([
            ReglaScoring(factor_id=f1.id, nombre="Ingresos altos", operador=">=", valor_min="8000000",
                         nivel="bajo", peso=-3, explicacion="Los ingresos son elevados, lo que reduce el riesgo.", orden=1),
            ReglaScoring(factor_id=f1.id, nombre="Ingresos medios", operador="entre", valor_min="4000000", valor_max="7999999",
                         nivel="medio", peso=5, explicacion="Los ingresos son moderados.", orden=2),
            ReglaScoring(factor_id=f1.id, nombre="Ingresos bajos", operador="<", valor_min="4000000",
                         nivel="alto", peso=15, explicacion="Los ingresos son insuficientes para la operación.", orden=3),
        ])

        # 2. Nivel de endeudamiento
        f2 = FactorScoring(modelo_id=modelo.id, codigo="nivel_endeudamiento",
            nombre="Nivel de Endeudamiento", descripcion="Porcentaje de deuda sobre ingresos.",
            tipo_dato="porcentaje", tipo_persona="AMBOS", categoria="principal", obligatorio=True, orden=2)
        db.session.add(f2)
        db.session.flush()
        db.session.add_all([
            ReglaScoring(factor_id=f2.id, nombre="Endeudamiento bajo", operador="<", valor_min="30",
                         nivel="bajo", peso=2, explicacion="El endeudamiento es bajo y manejable.", orden=1),
            ReglaScoring(factor_id=f2.id, nombre="Endeudamiento medio", operador="entre", valor_min="30", valor_max="50",
                         nivel="medio", peso=8, explicacion="El endeudamiento es moderado, requiere atención.", orden=2),
            ReglaScoring(factor_id=f2.id, nombre="Endeudamiento alto", operador="entre", valor_min="51", valor_max="70",
                         nivel="alto", peso=15, explicacion="El endeudamiento es elevado y compromete la capacidad de pago.", orden=3),
            ReglaScoring(factor_id=f2.id, nombre="Endeudamiento crítico", operador=">", valor_min="70",
                         nivel="alto", peso=20, explicacion="El endeudamiento supera los límites aceptables.", orden=4),
        ])

        # 3. Historial de pagos
        f3 = FactorScoring(modelo_id=modelo.id, codigo="historial_pagos",
            nombre="Historial de Pagos", descripcion="Comportamiento histórico de pagos del cliente.",
            tipo_dato="catalogo", tipo_persona="AMBOS", categoria="principal", obligatorio=True, orden=3)
        db.session.add(f3)
        db.session.flush()
        db.session.add_all([
            CatalogoScoring(factor_id=f3.id, valor="excelente", etiqueta="Excelente", orden=1),
            CatalogoScoring(factor_id=f3.id, valor="bueno", etiqueta="Bueno", orden=2),
            CatalogoScoring(factor_id=f3.id, valor="regular", etiqueta="Regular", orden=3),
            CatalogoScoring(factor_id=f3.id, valor="malo", etiqueta="Malo", orden=4),
            CatalogoScoring(factor_id=f3.id, valor="sin_historial", etiqueta="Sin historial", orden=5),
        ])
        db.session.add_all([
            ReglaScoring(factor_id=f3.id, nombre="Historial excelente", operador="==", valor_min="excelente",
                         nivel="bajo", peso=-5, explicacion="Historial de pagos impecable, factor favorable.", orden=1),
            ReglaScoring(factor_id=f3.id, nombre="Historial bueno", operador="==", valor_min="bueno",
                         nivel="bajo", peso=2, explicacion="Historial de pagos favorable.", orden=2),
            ReglaScoring(factor_id=f3.id, nombre="Historial regular", operador="==", valor_min="regular",
                         nivel="medio", peso=8, explicacion="El historial presenta algunas irregularidades.", orden=3),
            ReglaScoring(factor_id=f3.id, nombre="Historial malo", operador="==", valor_min="malo",
                         nivel="alto", peso=18, explicacion="El historial es desfavorable con múltiples incumplimientos.", orden=4),
            ReglaScoring(factor_id=f3.id, nombre="Sin historial", operador="==", valor_min="sin_historial",
                         nivel="medio", peso=6, explicacion="No se cuenta con historial previo de pagos.", orden=5),
        ])

        # 4. Antigüedad laboral
        f4 = FactorScoring(modelo_id=modelo.id, codigo="antiguedad_laboral",
            nombre="Antigüedad Laboral", descripcion="Meses en el empleo o actividad actual.",
            tipo_dato="numerico", tipo_persona="PF", categoria="principal", obligatorio=True, orden=4)
        db.session.add(f4)
        db.session.flush()
        db.session.add_all([
            ReglaScoring(factor_id=f4.id, nombre="Alta antigüedad", operador=">=", valor_min="36",
                         nivel="bajo", peso=-2, explicacion="Estabilidad laboral comprobada (más de 3 años).", orden=1),
            ReglaScoring(factor_id=f4.id, nombre="Antigüedad media", operador="entre", valor_min="12", valor_max="35",
                         nivel="medio", peso=5, explicacion="Antigüedad laboral aceptable.", orden=2),
            ReglaScoring(factor_id=f4.id, nombre="Baja antigüedad", operador="<", valor_min="12",
                         nivel="alto", peso=12, explicacion="Poca estabilidad laboral (menos de 1 año).", orden=3),
        ])

        # 5. Capacidad de pago (relación cuota/ingreso)
        f5 = FactorScoring(modelo_id=modelo.id, codigo="relacion_cuota_ingreso",
            nombre="Relación Cuota/Ingreso", descripcion="Porcentaje que representaría la cuota sobre los ingresos.",
            tipo_dato="porcentaje", tipo_persona="AMBOS", categoria="principal", obligatorio=False, orden=5)
        db.session.add(f5)
        db.session.flush()
        db.session.add_all([
            ReglaScoring(factor_id=f5.id, nombre="Cuota baja", operador="<=", valor_min="25",
                         nivel="bajo", peso=-2, explicacion="La cuota representa una porción baja de los ingresos.", orden=1),
            ReglaScoring(factor_id=f5.id, nombre="Cuota moderada", operador="entre", valor_min="26", valor_max="40",
                         nivel="medio", peso=8, explicacion="La cuota es moderada respecto a los ingresos.", orden=2),
            ReglaScoring(factor_id=f5.id, nombre="Cuota elevada", operador=">", valor_min="40",
                         nivel="alto", peso=18, explicacion="La cuota supera el 40% de los ingresos, riesgo elevado.", orden=3),
        ])

        # 6. Patrimonio
        f6 = FactorScoring(modelo_id=modelo.id, codigo="patrimonio",
            nombre="Patrimonio", descripcion="Nivel de patrimonio declarado por el cliente.",
            tipo_dato="catalogo", tipo_persona="AMBOS", categoria="principal", obligatorio=False, orden=6)
        db.session.add(f6)
        db.session.flush()
        db.session.add_all([
            CatalogoScoring(factor_id=f6.id, valor="alto", etiqueta="Alto", orden=1),
            CatalogoScoring(factor_id=f6.id, valor="medio", etiqueta="Medio", orden=2),
            CatalogoScoring(factor_id=f6.id, valor="bajo", etiqueta="Bajo", orden=3),
            CatalogoScoring(factor_id=f6.id, valor="sin_patrimonio", etiqueta="Sin patrimonio", orden=4),
        ])
        db.session.add_all([
            ReglaScoring(factor_id=f6.id, nombre="Patrimonio alto", operador="==", valor_min="alto",
                         nivel="bajo", peso=-4, explicacion="El patrimonio respalda la operación.", orden=1),
            ReglaScoring(factor_id=f6.id, nombre="Patrimonio medio", operador="==", valor_min="medio",
                         nivel="bajo", peso=2, explicacion="Patrimonio adecuado.", orden=2),
            ReglaScoring(factor_id=f6.id, nombre="Patrimonio bajo", operador="==", valor_min="bajo",
                         nivel="medio", peso=8, explicacion="El patrimonio es limitado.", orden=3),
            ReglaScoring(factor_id=f6.id, nombre="Sin patrimonio", operador="==", valor_min="sin_patrimonio",
                         nivel="alto", peso=14, explicacion="No se declara patrimonio de respaldo.", orden=4),
        ])

        # ── FACTORES COMPLEMENTARIOS ──────────────────────────────────

        # 7. PEP
        f7 = FactorScoring(modelo_id=modelo.id, codigo="es_pep",
            nombre="Persona Expuesta Políticamente", descripcion="Indica si el cliente es PEP.",
            tipo_dato="booleano", tipo_persona="AMBOS", categoria="complementario", obligatorio=False, orden=7)
        db.session.add(f7)
        db.session.flush()
        db.session.add_all([
            ReglaScoring(factor_id=f7.id, nombre="No es PEP", operador="==", valor_min="false",
                         nivel="bajo", peso=0, explicacion="El cliente no es persona políticamente expuesta.", orden=1),
            ReglaScoring(factor_id=f7.id, nombre="Es PEP", operador="==", valor_min="true",
                         nivel="alto", peso=10, explicacion="Cliente políticamente expuesto, requiere diligencia reforzada.", orden=2),
        ])

        # 8. Residencia
        f8 = FactorScoring(modelo_id=modelo.id, codigo="residencia",
            nombre="Residencia", descripcion="País de residencia del cliente.",
            tipo_dato="catalogo", tipo_persona="AMBOS", categoria="complementario", obligatorio=False, orden=8)
        db.session.add(f8)
        db.session.flush()
        db.session.add_all([
            CatalogoScoring(factor_id=f8.id, valor="paraguay", etiqueta="Paraguay", orden=1),
            CatalogoScoring(factor_id=f8.id, valor="extranjero", etiqueta="País extranjero", orden=2),
        ])
        db.session.add_all([
            ReglaScoring(factor_id=f8.id, nombre="Residente local", operador="==", valor_min="paraguay",
                         nivel="bajo", peso=0, explicacion="Residente en Paraguay.", orden=1),
            ReglaScoring(factor_id=f8.id, nombre="Residente extranjero", operador="==", valor_min="extranjero",
                         nivel="medio", peso=5, explicacion="Residente en el extranjero, factor complementario de riesgo.", orden=2),
        ])

        # ── UMBRALES DE CLASIFICACIÓN ─────────────────────────────────
        db.session.add_all([
            UmbralScoring(modelo_id=modelo.id, nivel="bajo", score_min=0, score_max=20,
                          descripcion="Riesgo bajo: cliente con perfil favorable."),
            UmbralScoring(modelo_id=modelo.id, nivel="medio", score_min=21, score_max=50,
                          descripcion="Riesgo medio: requiere análisis adicional."),
            UmbralScoring(modelo_id=modelo.id, nivel="alto", score_min=51, score_max=999,
                          descripcion="Riesgo alto: operación no recomendada."),
        ])

        db.session.commit()
        print("✅ Modelo 'Riesgo Comercial Inmobiliario' creado con 8 factores y reglas.")
        print("   Factores principales: ingresos, endeudamiento, historial, antigüedad, cuota/ingreso, patrimonio")
        print("   Factores complementarios: PEP, residencia")
        print("   Umbrales: 0-20=bajo, 21-50=medio, 51+=alto")
