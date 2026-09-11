-- ============================================================
-- Sistema de Evaluación de Clientes - Inmobiliaria
-- Script DDL: Creación de tablas en SQL Server 2022
-- ============================================================

USE inmobiliaria_db;
GO

-- ── 1. USUARIOS DEL SISTEMA ──────────────────────────────────
CREATE TABLE usuarios (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    nombre          VARCHAR(100)  NOT NULL,
    apellido        VARCHAR(100)  NOT NULL,
    email           VARCHAR(150)  NOT NULL,
    password_hash   VARCHAR(255)  NOT NULL,
    rol             VARCHAR(20)   NOT NULL DEFAULT 'operador'
                        CONSTRAINT chk_rol CHECK (rol IN ('administrador','operador')),
    activo          BIT           NOT NULL DEFAULT 1,
    creado_en       DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    actualizado_en  DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT uq_usuarios_email UNIQUE (email)
);
GO

-- ── 2. CLIENTES ──────────────────────────────────────────────
CREATE TABLE clientes (
    id               INT IDENTITY(1,1) PRIMARY KEY,
    tipo_doc         VARCHAR(10)   NOT NULL
                         CONSTRAINT chk_tipo_doc CHECK (tipo_doc IN ('DNI','RUC','CE')),
    num_doc          VARCHAR(20)   NOT NULL,
    nombre           VARCHAR(100)  NOT NULL,
    apellido         VARCHAR(100),
    email            VARCHAR(150),
    telefono         VARCHAR(20),
    direccion        VARCHAR(255),
    fecha_nacimiento DATE,
    estado           VARCHAR(20)   NOT NULL DEFAULT 'activo',
    creado_por       INT           REFERENCES usuarios(id),
    creado_en        DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT uq_clientes_num_doc UNIQUE (num_doc)
);
GO

-- ── 3. CRITERIOS DE EVALUACIÓN ────────────────────────────────
CREATE TABLE criterios (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    nombre      VARCHAR(100)  NOT NULL,
    descripcion VARCHAR(255),
    peso        DECIMAL(5,2)  NOT NULL
                    CONSTRAINT chk_peso CHECK (peso > 0 AND peso <= 100),
    activo      BIT           NOT NULL DEFAULT 1
);
GO

-- ── 4. EVALUACIONES ──────────────────────────────────────────
CREATE TABLE evaluaciones (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id    INT           NOT NULL REFERENCES clientes(id),
    evaluador_id  INT           NOT NULL REFERENCES usuarios(id),
    fecha         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    puntaje_total DECIMAL(5,2),
    resultado     VARCHAR(20)
                      CONSTRAINT chk_resultado CHECK (resultado IN ('aprobado','observado','rechazado')),
    observaciones NVARCHAR(MAX),
    estado        VARCHAR(20)   NOT NULL DEFAULT 'pendiente'
);
GO

-- ── 5. DETALLE DE EVALUACIÓN ──────────────────────────────────
CREATE TABLE evaluacion_detalle (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    evaluacion_id INT           NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
    criterio_id   INT           NOT NULL REFERENCES criterios(id),
    valor         DECIMAL(5,2)  NOT NULL
                      CONSTRAINT chk_valor CHECK (valor >= 0 AND valor <= 100),
    comentario    VARCHAR(255)
);
GO

-- ── 6. DOCUMENTOS ADJUNTOS ────────────────────────────────────
CREATE TABLE documentos (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id     INT           NOT NULL REFERENCES clientes(id),
    tipo           VARCHAR(50)   NOT NULL,
    nombre_archivo VARCHAR(255)  NOT NULL,
    ruta           VARCHAR(500)  NOT NULL,
    subido_por     INT           REFERENCES usuarios(id),
    subido_en      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- ============================================================
-- DATOS INICIALES
-- ============================================================

-- Criterios por defecto
INSERT INTO criterios (nombre, descripcion, peso) VALUES
('Capacidad de Pago',    'Relación cuota/ingreso mensual',              25.00),
('Historial Crediticio', 'Antecedentes financieros del cliente',        25.00),
('Estabilidad Laboral',  'Tiempo y tipo de relación laboral',           20.00),
('Documentación',        'Completitud y validez de documentos',         15.00),
('Patrimonio',           'Bienes y activos declarados por el cliente',  15.00);
GO

-- Usuario administrador inicial (password: Admin@2026)
-- Hash generado con werkzeug.security.generate_password_hash
INSERT INTO usuarios (nombre, apellido, email, password_hash, rol) VALUES
('Administrador', 'Sistema',
 'admin@inmobiliaria.com',
 'scrypt:32768:8:1$placeholder$changeme_run_seed_script',
 'administrador');
GO

PRINT 'Base de datos creada exitosamente.';
GO
