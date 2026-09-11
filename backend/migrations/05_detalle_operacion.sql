-- ============================================================
--  TABLA: detalle_operacion
--  Datos de la operación inmobiliaria asociada a una evaluación
--  SQL Server 2022 | Base de datos: inmobiliaria_db
-- ============================================================

USE inmobiliaria_db;
GO

IF OBJECT_ID('dbo.detalle_operacion', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.detalle_operacion (
        id               INT           IDENTITY(1,1)  NOT NULL,
        evaluacion_id    INT                          NOT NULL,
        tipo_propiedad   VARCHAR(50)                  NOT NULL,
        valor_propiedad  DECIMAL(14,2)                NOT NULL,
        monto_solicitado DECIMAL(14,2)                NOT NULL,
        plazo_meses      INT                          NOT NULL,
        ubicacion        VARCHAR(255)                 NULL,
        destino          VARCHAR(50)                  NULL,

        CONSTRAINT PK_detalle_operacion  PRIMARY KEY (id),
        CONSTRAINT CK_detop_tipo         CHECK (tipo_propiedad IN
            ('casa','departamento','terreno','local_comercial','oficina')),
        CONSTRAINT CK_detop_destino      CHECK (destino IN
            ('vivienda','inversion','comercial') OR destino IS NULL),

        CONSTRAINT FK_detop_evaluacion
            FOREIGN KEY (evaluacion_id) REFERENCES dbo.evaluacion_riesgo(id)
            ON DELETE CASCADE
    );
    PRINT '>> Tabla detalle_operacion creada.';
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_detop_evaluacion')
    CREATE INDEX IX_detop_evaluacion ON dbo.detalle_operacion(evaluacion_id);
GO

PRINT '>> Migración 05 completada.';
GO
