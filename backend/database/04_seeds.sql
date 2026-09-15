-- ============================================================================
--  04_seeds.sql  (PostgreSQL)
--  Datos iniciales del motor de reglas IF-THEN (idénticos a la versión previa).
--  Los criterios de evaluación y el usuario administrador los crea seed.py.
--  Este script es idempotente: no duplica el motor si ya existe.
--    SCOPE_IDENTITY()  ->  variable capturada con RETURNING
--    SELECT TOP 1      ->  SELECT ... LIMIT 1
--    BIT 1/0           ->  BOOLEAN true/false
-- ============================================================================

DO $$
DECLARE
    v_motor_id  integer;
    v_admin_id  integer;
BEGIN
    IF EXISTS (SELECT 1 FROM motor_reglas WHERE nombre = 'Plantilla Estándar Inmobiliaria') THEN
        RAISE NOTICE 'El motor de reglas de ejemplo ya existe; se omite.';
        RETURN;
    END IF;

    SELECT id INTO v_admin_id
    FROM usuarios
    WHERE rol IN ('administrador', 'propietario')
    ORDER BY id
    LIMIT 1;

    INSERT INTO motor_reglas (nombre, version, descripcion, activo, creado_por)
    VALUES (
        'Plantilla Estándar Inmobiliaria',
        '1.0',
        'Plantilla base de evaluación de riesgo para clientes de inmobiliaria. '
        || 'Evalúa capacidad de pago, historial y estabilidad laboral.',
        true,
        v_admin_id
    )
    RETURNING id INTO v_motor_id;

    INSERT INTO reglas
        (motor_id, nombre, descripcion, parametro, operador, valor_referencia,
         tipo_valor, peso_puntos, es_determinante, activo, orden)
    VALUES
    (v_motor_id, 'Sin antecedentes en lista negra',
     'El cliente NO debe estar en listas OFAC, ONU u otras listas de riesgo.',
     'en_lista_negra', '==', 'false', 'booleano', 100, true, true, 1),

    (v_motor_id, 'Edad mínima requerida',
     'El cliente debe tener al menos 21 años.',
     'edad', '>=', '21', 'numerico', 50, true, true, 2),

    (v_motor_id, 'Ingresos mínimos',
     'Ingresos mensuales iguales o superiores a 3.000.000 Gs.',
     'ingresos_mensuales', '>=', '3000000', 'numerico', 150, false, true, 3),

    (v_motor_id, 'Nivel de endeudamiento aceptable',
     'La relación deuda/ingreso no debe superar el 40%.',
     'nivel_endeudamiento', '<=', '40', 'numerico', 120, false, true, 4),

    (v_motor_id, 'Deuda total en sistema controlada',
     'Deuda total en el sistema financiero menor a 50.000.000 Gs.',
     'deuda_total_sistema', '<=', '50000000', 'numerico', 100, false, true, 5),

    (v_motor_id, 'Historial de pagos bueno',
     'El cliente debe tener un historial de pagos bueno o excelente.',
     'historial_pagos', '==', 'bueno', 'texto', 130, false, true, 6),

    (v_motor_id, 'Sin atrasos registrados',
     'El cliente no debe tener atrasos en pagos anteriores.',
     'cantidad_atrasos', '==', '0', 'numerico', 100, false, true, 7),

    (v_motor_id, 'Antigüedad laboral mínima',
     'El cliente debe tener al menos 6 meses en su empleo actual.',
     'meses_empleo_actual', '>=', '6', 'numerico', 80, false, true, 8),

    (v_motor_id, 'Score crediticio externo aceptable',
     'Score en centrales de riesgo igual o superior a 500.',
     'score_externo', '>=', '500', 'numerico', 120, false, true, 9),

    (v_motor_id, 'Referencias personales verificadas',
     'Las referencias personales deben ser buenas o regulares.',
     'referencias_personales', '!=', 'malas', 'texto', 50, false, true, 10);

    RAISE NOTICE 'Motor de reglas de ejemplo insertado con 10 reglas (motor_id=%).', v_motor_id;
END $$;
