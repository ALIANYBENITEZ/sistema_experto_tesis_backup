# Producto

Sistema de evaluación de clientes para una empresa inmobiliaria. Permite registrar clientes, evaluarlos mediante criterios ponderados y un motor de inferencia basado en reglas (sistema experto IF-THEN), y generar reportes de riesgo crediticio.

## Usuarios del sistema

- **Administrador**: Gestión de usuarios, configuración de criterios y motores de reglas, acceso total.
- **Operador**: Registro de clientes, ejecución de evaluaciones y consulta de reportes.

## Módulos principales

- **Autenticación**: Login con JWT (access + refresh tokens).
- **Clientes**: CRUD de clientes con documentos adjuntos.
- **Evaluación por Criterios**: Puntaje ponderado basado en criterios configurables (Capacidad de Pago, Historial Crediticio, Estabilidad Laboral, Documentación, Patrimonio).
- **Scoring / Motor de Reglas**: Sistema experto con reglas IF-THEN, operadores lógicos, reglas determinantes, y clasificación automática de riesgo (bajo/medio/alto/rechazado).
- **Reportes**: Generación de reportes PDF y estadísticas de dashboard.
- **Gestión de Usuarios**: Alta/baja de usuarios del sistema (solo admin).

## Dominio

- Idioma del dominio: Español (nombres de tablas, campos, variables de negocio).
- Contexto geográfico: Perú (DNI, RUC, CE como tipos de documento).
- Base de datos: `inmobiliaria_db`.
