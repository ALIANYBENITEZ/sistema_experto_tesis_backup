-- ============================================================
--  SISTEMA DE EVALUACIÓN DE CLIENTES - INMOBILIARIA
--  Script completo: Tablas, Relaciones, Datos iniciales
--  Motor: SQL Server 2022
--  Fecha: 2026
-- ============================================================

-- ── CREAR BASE DE DATOS ──────────────────────────────────────
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'inmobiliaria_db')
BEGIN
    CREATE DATABASE inmobiliaria_db
    COLLATE Modern_Spanish_CI_AI;
    PRINT '>> Base de datos inmobiliaria_db creada.';
END
GO

USE inmobiliaria_db;
GO

-- ============================================================
--  TABLA 1: usuarios
--  Usuarios del sistema (Administrador / Operador)
-- ============================================================
IF OBJECT_ID('dbo.usuarios', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.usuarios (
        id              INT             IDENTITY(1,1)   NOT NULL,
        nombre          VARCHAR(100)                    NOT NULL,
        apellido        VARCHAR(100)                    NOT NULL,
        email           VARCHAR(150)                    NOT NULL,
        password_hash   VARCHAR(255)                    NOT NULL,
        rol             VARCHAR(20)                     NOT NULL    DEFAULT 'operador',
        activo          BIT                             NOT NULL    DEFAULT 1,
        creado_en       DATETIME2                       NOT NULL    DEFAULT SYSUTCDATETIME(),
        actualizado_en  DATETIME2                       NOT NULL    DEFAULT SYSUTCDATETIME(),

        -- Claves
        CONSTRAINT PK_usuarios          PRIMARY KEY (id),
        CONSTRAINT UQ_usuarios_email    UNIQUE      (email),
        CONSTRAINT CK_usuarios_rol      CHECK       (rol IN ('administrador', 'operador'))
    );
    PRINT '>> Tabla usuarios creada.';
END
GO

-- ============================================================
--  TABLA 2: clientes
--  Clientes que solicitan evaluación para adquirir propiedad
-- ============================================================
IF OBJECT_ID('dbo.clientes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.clientes (
        id               INT          IDENTITY(1,1)  NOT NULL,
        tipo_doc         VARCHAR(10)                 NOT NULL,
        num_doc          VARCHAR(20)                 NOT NULL,
        nombre           VARCHAR(100)                NOT NULL,
        apellido         VARCHAR(100)                NULL,
        email            VARCHAR(150)                NULL,
        telefono         VARCHAR(20)                 NULL,
        direccion        VARCHAR(255)                NULL,
        fecha_nacimiento DATE                        NULL,
        estado           VARCHAR(20)                 NOT NULL  DEFAULT 'activo',
        creado_por       INT                         NULL,
        creado_en        DATETIME2                   NOT NULL  DEFAULT SYSUTCDATETIME(),

        -- Claves
        CONSTRAINT PK_clientes              PRIMARY KEY (id),
        CONSTRAINT UQ_clientes_num_doc      UNIQUE      (num_doc),
        CONSTRAINT CK_clientes_tipo_doc     CHECK       (tipo_doc IN ('DNI', 'RUC', 'CE')),
        CONSTRAINT CK_clientes_estado       CHECK       (estado IN ('activo', 'inactivo')),

        -- Foránea
        CONSTRAINT FK_clientes_creado_por
            FOREIGN KEY (creado_por) REFERENCES dbo.usuarios(id)
            ON UPDATE NO ACTION
            ON DELETE SET NULL
    );
    PRINT '>> Tabla clientes creada.';
END
GO

-- ============================================================
--  TABLA 3: criterios
--  Criterios de evaluación configurables por el administrador
-- ============================================================
IF OBJECT_ID('dbo.criterios', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.criterios (
        id          INT           IDENTITY(1,1)  NOT NULL,
        nombre      VARCHAR(100)                 NOT NULL,
        descripcion VARCHAR(255)                 NULL,
        peso        DECIMAL(5,2)                 NOT NULL,
        activo      BIT                          NOT NULL  DEFAULT 1,

        -- Claves
        CONSTRAINT PK_criterios         PRIMARY KEY (id),
        CONSTRAINT CK_criterios_peso    CHECK       (peso > 0 AND peso <= 100)
    );
    PRINT '>> Tabla criterios creada.';
END
GO

-- ============================================================
--  TABLA 4: evaluaciones
--  Registro de cada evaluación realizada a un cliente
-- ============================================================
IF OBJECT_ID('dbo.evaluaciones', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.evaluaciones (
        id             INT           IDENTITY(1,1)  NOT NULL,
        cliente_id     INT                          NOT NULL,
        evaluador_id   INT                          NOT NULL,
        fecha          DATETIME2                    NOT NULL  DEFAULT SYSUTCDATETIME(),
        puntaje_total  DECIMAL(5,2)                 NULL,
        resultado      VARCHAR(20)                  NULL,
        observaciones  NVARCHAR(MAX)                NULL,
        estado         VARCHAR(20)                  NOT NULL  DEFAULT 'pendiente',

        -- Claves
        CONSTRAINT PK_evaluaciones              PRIMARY KEY (id),
        CONSTRAINT CK_evaluaciones_resultado    CHECK (resultado IN ('aprobado', 'observado', 'rechazado')),
        CONSTRAINT CK_evaluaciones_estado       CHECK (estado IN ('pendiente', 'completado', 'anulado')),

        -- Foráneas
        CONSTRAINT FK_evaluaciones_cliente
            FOREIGN KEY (cliente_id) REFERENCES dbo.clientes(id)
            ON UPDATE NO ACTION
            ON DELETE NO ACTION,

        CONSTRAINT FK_evaluaciones_evaluador
            FOREIGN KEY (evaluador_id) REFERENCES dbo.usuarios(id)
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    );
    PRINT '>> Tabla evaluaciones creada.';
END
GO

-- ============================================================
--  TABLA 5: evaluacion_detalle
--  Detalle por criterio de cada evaluación
-- ============================================================
IF OBJECT_ID('dbo.evaluacion_detalle', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.evaluacion_detalle (
        id             INT           IDENTITY(1,1)  NOT NULL,
        evaluacion_id  INT                          NOT NULL,
        criterio_id    INT                          NOT NULL,
        valor          DECIMAL(5,2)                 NOT NULL,
        comentario     VARCHAR(255)                 NULL,

        -- Claves
        CONSTRAINT PK_evaluacion_detalle        PRIMARY KEY (id),
        CONSTRAINT CK_evaluacion_detalle_valor  CHECK (valor >= 0 AND valor <= 100),

        -- Foráneas
        CONSTRAINT FK_eval_detalle_evaluacion
            FOREIGN KEY (evaluacion_id) REFERENCES dbo.evaluaciones(id)
            ON UPDATE NO ACTION
            ON DELETE CASCADE,

        CONSTRAINT FK_eval_detalle_criterio
            FOREIGN KEY (criterio_id) REFERENCES dbo.criterios(id)
            ON UPDATE NO ACTION
            ON DELETE NO ACTION
    );
    PRINT '>> Tabla evaluacion_detalle creada.';
END
GO

-- ============================================================
--  TABLA 6: documentos
--  Documentos adjuntos por cliente (DNI, recibos, etc.)
-- ============================================================
IF OBJECT_ID('dbo.documentos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.documentos (
        id              INT           IDENTITY(1,1)  NOT NULL,
        cliente_id      INT                          NOT NULL,
        tipo            VARCHAR(50)                  NOT NULL,
        nombre_archivo  VARCHAR(255)                 NOT NULL,
        ruta            VARCHAR(500)                 NOT NULL,
        subido_por      INT                          NULL,
        subido_en       DATETIME2                    NOT NULL  DEFAULT SYSUTCDATETIME(),

        -- Claves
        CONSTRAINT PK_documentos   PRIMARY KEY (id),

        -- Foráneas
        CONSTRAINT FK_documentos_cliente
            FOREIGN KEY (cliente_id) REFERENCES dbo.clientes(id)
            ON UPDATE NO ACTION
            ON DELETE CASCADE,

        CONSTRAINT FK_documentos_usuario
            FOREIGN KEY (subido_por) REFERENCES dbo.usuarios(id)
            ON UPDATE NO ACTION
            ON DELETE SET NULL
    );
    PRINT '>> Tabla documentos creada.';
END
GO

-- ============================================================
--  ÍNDICES para mejorar rendimiento en consultas frecuentes
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_clientes_num_doc')
    CREATE INDEX IX_clientes_num_doc
        ON dbo.clientes(num_doc);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_clientes_estado')
    CREATE INDEX IX_clientes_estado
        ON dbo.clientes(estado);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_evaluaciones_cliente')
    CREATE INDEX IX_evaluaciones_cliente
        ON dbo.evaluaciones(cliente_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_evaluaciones_resultado')
    CREATE INDEX IX_evaluaciones_resultado
        ON dbo.evaluaciones(resultado);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_evaluaciones_fecha')
    CREATE INDEX IX_evaluaciones_fecha
        ON dbo.evaluaciones(fecha DESC);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_eval_detalle_evaluacion')
    CREATE INDEX IX_eval_detalle_evaluacion
        ON dbo.evaluacion_detalle(evaluacion_id);
GO
PRINT '>> Índices creados.';
GO

-- ============================================================
--  DATOS INICIALES
-- ============================================================

-- ── Criterios de evaluación por defecto ─────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.criterios WHERE nombre = 'Capacidad de Pago')
BEGIN
    INSERT INTO dbo.criterios (nombre, descripcion, peso, activo) VALUES
    ('Capacidad de Pago',
     'Evalúa la relación entre la cuota mensual estimada y el ingreso neto del cliente. Ratio máximo aceptable: 40%.',
     25.00, 1),

    ('Historial Crediticio',
     'Antecedentes financieros del cliente: deudas anteriores, moras, calificación en centrales de riesgo.',
     25.00, 1),

    ('Estabilidad Laboral',
     'Tiempo en el empleo actual, tipo de contrato (indefinido, plazo fijo, independiente) y sector económico.',
     20.00, 1),

    ('Documentación',
     'Completitud y validez de los documentos presentados: DNI, boletas, declaración jurada, etc.',
     15.00, 1),

    ('Patrimonio',
     'Bienes, activos y propiedades declaradas por el cliente que respaldan la operación.',
     15.00, 1);

    PRINT '>> Criterios de evaluación insertados.';
END
GO

-- ── Usuario Administrador inicial ───────────────────────────
-- Contraseña: Admin@2026
-- Hash generado con werkzeug.security (scrypt) desde seed.py
-- Este registro es solo de referencia; usar seed.py para el hash real.
IF NOT EXISTS (SELECT 1 FROM dbo.usuarios WHERE email = 'admin@inmobiliaria.com')
BEGIN
    INSERT INTO dbo.usuarios (nombre, apellido, email, password_hash, rol, activo)
    VALUES (
        'Administrador',
        'Sistema',
        'admin@inmobiliaria.com',
        'EJECUTAR_SEED_PY_PARA_HASH_REAL',
        'administrador',
        1
    );
    PRINT '>> Usuario administrador insertado (ejecutar seed.py para hash correcto).';
END
GO

-- ── Usuario Operador de prueba ───────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.usuarios WHERE email = 'operador@inmobiliaria.com')
BEGIN
    INSERT INTO dbo.usuarios (nombre, apellido, email, password_hash, rol, activo)
    VALUES (
        'Juan',
        'Pérez',
        'operador@inmobiliaria.com',
        'EJECUTAR_SEED_PY_PARA_HASH_REAL',
        'operador',
        1
    );
    PRINT '>> Usuario operador insertado (ejecutar seed.py para hash correcto).';
END
GO

-- ── Clientes de prueba ───────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM dbo.clientes WHERE num_doc = '12345678')
BEGIN
    INSERT INTO dbo.clientes
        (tipo_doc, num_doc, nombre, apellido, email, telefono, direccion, fecha_nacimiento, estado, creado_por)
    VALUES
    ('DNI', '12345678', 'Carlos',  'Mendoza',  'cmendoza@email.com',  '987654321', 'Av. Lima 123, Miraflores',    '1985-03-15', 'activo', 1),
    ('DNI', '87654321', 'Ana',     'García',   'agarcia@email.com',   '912345678', 'Jr. Cusco 456, San Isidro',   '1990-07-22', 'activo', 1),
    ('RUC', '20512345678', 'Luis', 'Torres',   'ltorres@empresa.com', '945678123', 'Av. Javier Prado 789, Surco', '1978-11-30', 'activo', 1),
    ('DNI', '45678901', 'María',   'López',    'mlopez@email.com',    '978123456', 'Calle Los Pinos 321, La Molina','1995-02-10','activo', 1),
    ('CE',  'CE001234', 'Roberto', 'Díaz',     'rdiaz@email.com',     '956789012', 'Av. Arequipa 654, Lince',     '1982-08-05', 'activo', 1);

    PRINT '>> Clientes de prueba insertados.';
END
GO

-- ============================================================
--  VISTA: resumen de evaluaciones (útil para reportes)
-- ============================================================
IF OBJECT_ID('dbo.vw_resumen_evaluaciones', 'V') IS NOT NULL
    DROP VIEW dbo.vw_resumen_evaluaciones;
GO

CREATE VIEW dbo.vw_resumen_evaluaciones AS
SELECT
    e.id                                                        AS evaluacion_id,
    e.fecha,
    e.puntaje_total,
    e.resultado,
    e.estado,
    c.num_doc,
    c.tipo_doc,
    CONCAT(c.nombre, ' ', ISNULL(c.apellido, ''))               AS cliente_nombre,
    c.email                                                     AS cliente_email,
    CONCAT(u.nombre, ' ', u.apellido)                           AS evaluador_nombre,
    u.rol                                                       AS evaluador_rol,
    (SELECT COUNT(*) FROM dbo.evaluacion_detalle ed
     WHERE ed.evaluacion_id = e.id)                             AS total_criterios
FROM
    dbo.evaluaciones    e
    INNER JOIN dbo.clientes  c ON c.id = e.cliente_id
    INNER JOIN dbo.usuarios  u ON u.id = e.evaluador_id;
GO
PRINT '>> Vista vw_resumen_evaluaciones creada.';
GO

-- ============================================================
--  VISTA: dashboard stats
-- ============================================================
IF OBJECT_ID('dbo.vw_dashboard_stats', 'V') IS NOT NULL
    DROP VIEW dbo.vw_dashboard_stats;
GO

CREATE VIEW dbo.vw_dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM dbo.clientes  WHERE estado = 'activo')            AS total_clientes,
    (SELECT COUNT(*) FROM dbo.evaluaciones)                                 AS total_evaluaciones,
    (SELECT COUNT(*) FROM dbo.evaluaciones WHERE resultado = 'aprobado')    AS aprobados,
    (SELECT COUNT(*) FROM dbo.evaluaciones WHERE resultado = 'observado')   AS observados,
    (SELECT COUNT(*) FROM dbo.evaluaciones WHERE resultado = 'rechazado')   AS rechazados,
    (SELECT COUNT(*) FROM dbo.usuarios   WHERE activo = 1)                  AS usuarios_activos;
GO
PRINT '>> Vista vw_dashboard_stats creada.';
GO

-- ============================================================
--  RESUMEN FINAL
-- ============================================================
PRINT '';
PRINT '============================================';
PRINT ' Script ejecutado exitosamente';
PRINT ' Base de datos: inmobiliaria_db';
PRINT '--------------------------------------------';
PRINT ' Tablas creadas:';
PRINT '   - usuarios';
PRINT '   - clientes';
PRINT '   - criterios';
PRINT '   - evaluaciones';
PRINT '   - evaluacion_detalle';
PRINT '   - documentos';
PRINT ' Vistas creadas:';
PRINT '   - vw_resumen_evaluaciones';
PRINT '   - vw_dashboard_stats';
PRINT '--------------------------------------------';
PRINT ' IMPORTANTE: Ejecutar seed.py para generar';
PRINT ' los hashes de contraseña correctos.';
PRINT '============================================';
GO
