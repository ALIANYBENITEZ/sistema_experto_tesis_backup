-- ============================================================
--  Actualizar tipos de documento: DNI→CI, CE→PAS
--  SQL Server 2022 | Base de datos: inmobiliaria_db
-- ============================================================

USE inmobiliaria_db;
GO

-- Eliminar constraint viejo
IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_clientes_tipo_doc')
BEGIN
    ALTER TABLE dbo.clientes DROP CONSTRAINT CK_clientes_tipo_doc;
    PRINT '>> Constraint CK_clientes_tipo_doc eliminado.';
END
GO

-- Crear constraint nuevo con CI, RUC, PAS
ALTER TABLE dbo.clientes
    ADD CONSTRAINT CK_clientes_tipo_doc CHECK (tipo_doc IN ('CI', 'RUC', 'PAS'));
GO
PRINT '>> Constraint CK_clientes_tipo_doc actualizado (CI, RUC, PAS).';
GO

-- Actualizar datos existentes
UPDATE dbo.clientes SET tipo_doc = 'CI'  WHERE tipo_doc = 'DNI';
UPDATE dbo.clientes SET tipo_doc = 'PAS' WHERE tipo_doc = 'CE';
GO
PRINT '>> Datos actualizados: DNI→CI, CE→PAS.';
GO
