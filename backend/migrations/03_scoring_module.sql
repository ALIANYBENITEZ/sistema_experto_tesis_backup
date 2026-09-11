-- ============================================================
--  MÓDULO DE SCORING — Motor de Reglas IF-THEN
--  Sistema Experto de Evaluación de Riesgo de Clientes
--  SQL Server 2022 | Base de datos: inmobiliaria_db
-- ============================================================

USE inmobiliaria_db;
GO

-- ── TABLA: motor_reglas ──────────────────────────────────────
IF OBJECT_ID('dbo.motor_reglas', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.motor_reglas (
        id          INT           IDENTITY(1,1)  NOT NULL,
        nombre      VARCHAR(100)                 NOT NULL,
        version     VARCHAR(20)                  NOT NULL  DEFAULT '1.0',
        descripcion VARCHAR(255)                 NULL,
        activo      BIT                          NOT NULL  DEFAULT 1,
        creado_por  INT                          NULL  REFERENCES dbo.usuarios(id),
        creado_en   DATETIME2                    NOT NULL  DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_motor_reglas PRIMARY KEY (id)
    );
    PRINT '>> Tabla motor_reglas creada.';
END
GO

-- ── TABLA: reglas ────────────────────────────────────────────
IF OBJECT_ID('dbo.reglas', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.reglas (
        id               INT           IDENTITY(1,1)  NOT NULL,
        motor_id         INT                          NOT NULL,
        nombre           VARCHAR(100)                 NOT NULL,
        descripcion      VARCHAR(255)                 NULL,
        parametro        VARCHAR(50)                  NOT NULL,
        operador         VARCHAR(10)                  NOT NULL,
        valor_referencia VARCHAR(100)                 NOT NULL,
        tipo_valor       VARCHAR(20)                  NOT NULL  DEFAULT 'numerico',
        peso_puntos      DECIMAL(6,2)                 NOT NULL,
        es_determinante  BIT                          NOT NULL  DEFAULT 0,
        activo           BIT                          NOT NULL  DEFAULT 1,
        orden            INT                          NOT NULL  DEFAULT 0,

        CONSTRAINT PK_reglas             PRIMARY KEY (id),
        CONSTRAINT CK_reglas_operador    CHECK (operador IN ('>=','<=','==','>','<','!=')),
        CONSTRAINT CK_reglas_tipo_valor  CHECK (tipo_valor IN ('numerico','texto','booleano')),
        CONSTRAINT CK_reglas_peso        CHECK (peso_puntos > 0),

        CONSTRAINT FK_reglas_motor
            FOREIGN KEY (motor_id) REFERENCES dbo.motor_reglas(id)
            ON DELETE CASCADE
    );
    PRINT '>> Tabla reglas creada.';
END
GO

-- ── TABLA: historial_crediticio ──────────────────────────────
IF OBJECT_ID('dbo.historial_crediticio', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.historial_crediticio (
        id                    INT           IDENTITY(1,1)  NOT NULL,
        cliente_id            INT                          NOT NULL,
        fuente_externa        VARCHAR(100)                 NULL,
        score_externo         DECIMAL(6,2)                 NULL,
        cantidad_atrasos      INT                          NOT NULL  DEFAULT 0,
        deuda_total_sistema   DECIMAL(14,2)                NOT NULL  DEFAULT 0,
        historial_pagos       VARCHAR(20)                  NOT NULL  DEFAULT 'sin_historial',
        en_lista_negra        BIT                          NOT NULL  DEFAULT 0,
        nivel_endeudamiento   DECIMAL(5,2)                 NOT NULL  DEFAULT 0,
        meses_empleo_actual   INT                          NOT NULL  DEFAULT 0,
        tipo_empleo           VARCHAR(50)                  NULL,
        referencias_personales VARCHAR(20)                 NOT NULL  DEFAULT 'no_verificadas',
        fecha_consulta        DATETIME2                    NOT NULL  DEFAULT SYSUTCDATETIME(),
        actualizado_en        DATETIME2                    NOT NULL  DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_historial_crediticio   PRIMARY KEY (id),
        CONSTRAINT UQ_historial_cliente      UNIQUE (cliente_id),
        CONSTRAINT CK_historial_pagos        CHECK (historial_pagos IN
            ('bueno','regular','malo','sin_historial')),
        CONSTRAINT CK_historial_referencias  CHECK (referencias_personales IN
            ('buenas','regulares','malas','no_verificadas')),
        CONSTRAINT CK_historial_tipo_empleo  CHECK (tipo_empleo IN
            ('dependiente','independiente','desempleado') OR tipo_empleo IS NULL),

        CONSTRAINT FK_historial_cliente
            FOREIGN KEY (cliente_id) REFERENCES dbo.clientes(id)
            ON DELETE CASCADE
    );
    PRINT '>> Tabla historial_crediticio creada.';
END
GO

-- ── TABLA: evaluacion_riesgo ─────────────────────────────────
IF OBJECT_ID('dbo.evaluacion_riesgo', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.evaluacion_riesgo (
        id                    INT           IDENTITY(1,1)  NOT NULL,
        cliente_id            INT                          NOT NULL,
        motor_id              INT                          NOT NULL,
        usuario_id            INT                          NOT NULL,
        fecha_analisis        DATETIME2                    NOT NULL  DEFAULT SYSUTCDATETIME(),
        score_final           DECIMAL(6,2)                 NULL,
        score_maximo          DECIMAL(6,2)                 NULL,
        categoria_riesgo      VARCHAR(20)                  NULL,
        estado                VARCHAR(20)                  NOT NULL  DEFAULT 'completado',
        observaciones         NVARCHAR(MAX)                NULL,
        regla_determinante_id INT                          NULL,

        CONSTRAINT PK_evaluacion_riesgo      PRIMARY KEY (id),
        CONSTRAINT CK_eval_categoria         CHECK (categoria_riesgo IN
            ('bajo','medio','alto','rechazado')),

        CONSTRAINT FK_evalriesgo_cliente
            FOREIGN KEY (cliente_id) REFERENCES dbo.clientes(id),
        CONSTRAINT FK_evalriesgo_motor
            FOREIGN KEY (motor_id)   REFERENCES dbo.motor_reglas(id),
        CONSTRAINT FK_evalriesgo_usuario
            FOREIGN KEY (usuario_id) REFERENCES dbo.usuarios(id),
        CONSTRAINT FK_evalriesgo_regla_det
            FOREIGN KEY (regla_determinante_id) REFERENCES dbo.reglas(id)
    );
    PRINT '>> Tabla evaluacion_riesgo creada.';
END
GO

-- ── TABLA: resultado_detalle ─────────────────────────────────
IF OBJECT_ID('dbo.resultado_detalle', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.resultado_detalle (
        id               INT           IDENTITY(1,1)  NOT NULL,
        evaluacion_id    INT                          NOT NULL,
        regla_id         INT                          NOT NULL,
        cumplido         BIT                          NOT NULL,
        valor_evaluado   VARCHAR(100)                 NULL,
        puntos_obtenidos DECIMAL(6,2)                 NOT NULL  DEFAULT 0,

        CONSTRAINT PK_resultado_detalle   PRIMARY KEY (id),

        CONSTRAINT FK_resdet_evaluacion
            FOREIGN KEY (evaluacion_id) REFERENCES dbo.evaluacion_riesgo(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_resdet_regla
            FOREIGN KEY (regla_id) REFERENCES dbo.reglas(id)
    );
    PRINT '>> Tabla resultado_detalle creada.';
END
GO

-- ── ÍNDICES ──────────────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_evalriesgo_cliente')
    CREATE INDEX IX_evalriesgo_cliente   ON dbo.evaluacion_riesgo(cliente_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_evalriesgo_categoria')
    CREATE INDEX IX_evalriesgo_categoria ON dbo.evaluacion_riesgo(categoria_riesgo);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_evalriesgo_fecha')
    CREATE INDEX IX_evalriesgo_fecha     ON dbo.evaluacion_riesgo(fecha_analisis DESC);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_reglas_motor')
    CREATE INDEX IX_reglas_motor         ON dbo.reglas(motor_id);
GO

-- ══════════════════════════════════════════════════════════════
--  DATOS INICIALES — Motor de ejemplo con reglas reales
-- ══════════════════════════════════════════════════════════════

IF NOT EXISTS (SELECT 1 FROM dbo.motor_reglas WHERE nombre = 'Plantilla Estándar Inmobiliaria')
BEGIN
    INSERT INTO dbo.motor_reglas (nombre, version, descripcion, activo, creado_por)
    VALUES (
        'Plantilla Estándar Inmobiliaria',
        '1.0',
        'Plantilla base de evaluación de riesgo para clientes de inmobiliaria. '
        + 'Evalúa capacidad de pago, historial y estabilidad laboral.',
        1,
        (SELECT TOP 1 id FROM dbo.usuarios WHERE rol = 'administrador')
    );

    DECLARE @motor_id INT = SCOPE_IDENTITY();

    -- REGLAS DETERMINANTES (rechazo automático si fallan)
    INSERT INTO dbo.reglas
        (motor_id, nombre, descripcion, parametro, operador, valor_referencia,
         tipo_valor, peso_puntos, es_determinante, activo, orden)
    VALUES
    (@motor_id,
     'Sin antecedentes en lista negra',
     'El cliente NO debe estar en listas OFAC, ONU u otras listas de riesgo.',
     'en_lista_negra', '==', 'false', 'booleano', 100, 1, 1, 1),

    (@motor_id,
     'Edad mínima requerida',
     'El cliente debe tener al menos 21 años.',
     'edad', '>=', '21', 'numerico', 50, 1, 1, 2),

    -- REGLAS DE CAPACIDAD FINANCIERA
    (@motor_id,
     'Ingresos mínimos',
     'Ingresos mensuales iguales o superiores a 3.000.000 Gs.',
     'ingresos_mensuales', '>=', '3000000', 'numerico', 150, 0, 1, 3),

    (@motor_id,
     'Nivel de endeudamiento aceptable',
     'La relación deuda/ingreso no debe superar el 40%.',
     'nivel_endeudamiento', '<=', '40', 'numerico', 120, 0, 1, 4),

    (@motor_id,
     'Deuda total en sistema controlada',
     'Deuda total en el sistema financiero menor a 50.000.000 Gs.',
     'deuda_total_sistema', '<=', '50000000', 'numerico', 100, 0, 1, 5),

    -- REGLAS DE HISTORIAL
    (@motor_id,
     'Historial de pagos bueno',
     'El cliente debe tener un historial de pagos bueno o excelente.',
     'historial_pagos', '==', 'bueno', 'texto', 130, 0, 1, 6),

    (@motor_id,
     'Sin atrasos registrados',
     'El cliente no debe tener atrasos en pagos anteriores.',
     'cantidad_atrasos', '==', '0', 'numerico', 100, 0, 1, 7),

    -- REGLAS DE ESTABILIDAD LABORAL
    (@motor_id,
     'Antigüedad laboral mínima',
     'El cliente debe tener al menos 6 meses en su empleo actual.',
     'meses_empleo_actual', '>=', '6', 'numerico', 80, 0, 1, 8),

    (@motor_id,
     'Score crediticio externo aceptable',
     'Score en centrales de riesgo igual o superior a 500.',
     'score_externo', '>=', '500', 'numerico', 120, 0, 1, 9),

    (@motor_id,
     'Referencias personales verificadas',
     'Las referencias personales deben ser buenas o regulares.',
     'referencias_personales', '!=', 'malas', 'texto', 50, 0, 1, 10);

    PRINT '>> Motor de reglas de ejemplo insertado con 10 reglas.';
END
GO

-- ══════════════════════════════════════════════════════════════
--  VISTA: evaluaciones de riesgo con detalle
-- ══════════════════════════════════════════════════════════════
IF OBJECT_ID('dbo.vw_evaluaciones_riesgo', 'V') IS NOT NULL
    DROP VIEW dbo.vw_evaluaciones_riesgo;
GO

CREATE VIEW dbo.vw_evaluaciones_riesgo AS
SELECT
    er.id                                                       AS evaluacion_id,
    er.fecha_analisis,
    er.score_final,
    er.score_maximo,
    CASE
        WHEN er.score_maximo > 0
        THEN ROUND(er.score_final / er.score_maximo * 100, 1)
        ELSE 0
    END                                                         AS porcentaje,
    er.categoria_riesgo,
    er.estado,
    CONCAT(c.nombre, ' ', ISNULL(c.apellido, ''))               AS cliente_nombre,
    c.num_doc,
    c.tipo_doc,
    mr.nombre                                                   AS motor_nombre,
    mr.version                                                  AS motor_version,
    CONCAT(u.nombre, ' ', u.apellido)                           AS evaluador_nombre,
    (SELECT COUNT(*) FROM dbo.resultado_detalle rd
     WHERE rd.evaluacion_id = er.id AND rd.cumplido = 1)        AS reglas_cumplidas,
    (SELECT COUNT(*) FROM dbo.resultado_detalle rd
     WHERE rd.evaluacion_id = er.id)                            AS total_reglas_evaluadas
FROM
    dbo.evaluacion_riesgo   er
    INNER JOIN dbo.clientes      c  ON c.id  = er.cliente_id
    INNER JOIN dbo.motor_reglas  mr ON mr.id = er.motor_id
    INNER JOIN dbo.usuarios      u  ON u.id  = er.usuario_id;
GO

PRINT '>> Vista vw_evaluaciones_riesgo creada.';
GO

PRINT '';
PRINT '============================================';
PRINT ' Módulo de Scoring instalado correctamente';
PRINT ' Nuevas tablas:';
PRINT '   - motor_reglas';
PRINT '   - reglas';
PRINT '   - historial_crediticio';
PRINT '   - evaluacion_riesgo';
PRINT '   - resultado_detalle';
PRINT ' Nueva vista:';
PRINT '   - vw_evaluaciones_riesgo';
PRINT '============================================';
GO
