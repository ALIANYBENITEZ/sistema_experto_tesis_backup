-- ============================================================================
--  03_views.sql  (PostgreSQL)
--  Vistas de reportes/dashboard. Equivalentes a las de SQL Server.
--    CONCAT + ISNULL  ->  concat_ws / coalesce
--    ROUND(x,1)       ->  round(x, 1)
-- ============================================================================

-- ── Resumen de evaluaciones por criterios ──────────────────────────────────
CREATE OR REPLACE VIEW vw_resumen_evaluaciones AS
SELECT
    e.id                                            AS evaluacion_id,
    e.fecha,
    e.puntaje_total,
    e.resultado,
    e.estado,
    c.num_doc,
    c.tipo_doc,
    concat_ws(' ', c.nombre, coalesce(c.apellido, '')) AS cliente_nombre,
    c.email                                         AS cliente_email,
    concat_ws(' ', u.nombre, u.apellido)            AS evaluador_nombre,
    u.rol                                           AS evaluador_rol,
    (SELECT count(*) FROM evaluacion_detalle ed
     WHERE ed.evaluacion_id = e.id)                 AS total_criterios
FROM evaluaciones e
    JOIN clientes c ON c.id = e.cliente_id
    JOIN usuarios u ON u.id = e.evaluador_id;


-- ── Estadísticas para el dashboard ─────────────────────────────────────────
CREATE OR REPLACE VIEW vw_dashboard_stats AS
SELECT
    (SELECT count(*) FROM clientes     WHERE estado = 'activo')          AS total_clientes,
    (SELECT count(*) FROM evaluaciones)                                  AS total_evaluaciones,
    (SELECT count(*) FROM evaluaciones WHERE resultado = 'aprobado')     AS aprobados,
    (SELECT count(*) FROM evaluaciones WHERE resultado = 'observado')    AS observados,
    (SELECT count(*) FROM evaluaciones WHERE resultado = 'rechazado')    AS rechazados,
    (SELECT count(*) FROM usuarios     WHERE activo = true)              AS usuarios_activos;


-- ── Evaluaciones de riesgo (motor de reglas) con detalle ───────────────────
CREATE OR REPLACE VIEW vw_evaluaciones_riesgo AS
SELECT
    er.id                                           AS evaluacion_id,
    er.fecha_analisis,
    er.score_final,
    er.score_maximo,
    CASE
        WHEN er.score_maximo > 0
        THEN round(er.score_final / er.score_maximo * 100, 1)
        ELSE 0
    END                                             AS porcentaje,
    er.categoria_riesgo,
    er.estado,
    concat_ws(' ', c.nombre, coalesce(c.apellido, '')) AS cliente_nombre,
    c.num_doc,
    c.tipo_doc,
    mr.nombre                                       AS motor_nombre,
    mr.version                                      AS motor_version,
    concat_ws(' ', u.nombre, u.apellido)            AS evaluador_nombre,
    (SELECT count(*) FROM resultado_detalle rd
     WHERE rd.evaluacion_id = er.id AND rd.cumplido = true) AS reglas_cumplidas,
    (SELECT count(*) FROM resultado_detalle rd
     WHERE rd.evaluacion_id = er.id)                AS total_reglas_evaluadas
FROM evaluacion_riesgo er
    JOIN clientes     c  ON c.id  = er.cliente_id
    JOIN motor_reglas mr ON mr.id = er.motor_id
    JOIN usuarios     u  ON u.id  = er.usuario_id;


DO $$ BEGIN
    RAISE NOTICE 'Vistas creadas: vw_resumen_evaluaciones, vw_dashboard_stats, vw_evaluaciones_riesgo';
END $$;
