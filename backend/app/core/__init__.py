"""
Core de Scoring de Riesgo Comercial
====================================
Motor de decisión configurable basado en reglas de negocio.

Arquitectura:
  DATOS → FACTORES → REGLAS → NIVELES → PESOS → SCORE → CLASIFICACIÓN → EXPLICACIÓN

Componentes:
  - models.py    : Modelos de datos del Core (Factor, Regla, Modelo, etc.)
  - engine.py    : Orquestador principal del flujo de evaluación
  - evaluator.py : Evaluador de reglas IF-THEN por factor
  - classifier.py: Clasificador de riesgo global
  - explainer.py : Generador de explicaciones
  - validator.py : Validador de datos de entrada
"""
