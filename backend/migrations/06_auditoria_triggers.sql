/* ============================================================================
   06_auditoria_triggers.sql
   Triggers de auditoría a nivel BASE DE DATOS (SQL Server).

   PROPÓSITO
   ---------
   Complementan la auditoría a nivel servicio (backend Python). Capturan cambios
   hechos DIRECTAMENTE sobre la base (SSMS, scripts, ETL, etc.), es decir, por
   fuera de la aplicación.

   EVITAR DUPLICADOS
   -----------------
   La aplicación puede "marcar" su sesión con CONTEXT_INFO para que los triggers
   NO vuelvan a registrar lo que ya audita el servicio. Convención:
       SET CONTEXT_INFO 0x4150500000000000;   -- 'APP' -> el trigger se salta
   Si CONTEXT_INFO no está marcado como APP, se asume operación DIRECTA en BD y
   el trigger registra el evento con origen 'BD_DIRECTO'.

   Los eventos generados por estos triggers usan:
       tipo_evento = <USUARIOS|CLIENTES|EMPRESAS>
       modulo      = 'BD'
       usuario_nombre = 'BD: ' + SUSER_SNAME()   (login de SQL Server)
       info_adicional = JSON con host, programa y login
   ============================================================================ */

SET NOCOUNT ON;
GO

/* ----------------------------------------------------------------------------
   Función helper: ¿la operación viene de la aplicación?
   Devuelve 1 si CONTEXT_INFO está marcado como 'APP'.
---------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.fn_auditoria_es_app', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_auditoria_es_app;
GO
CREATE FUNCTION dbo.fn_auditoria_es_app()
RETURNS BIT
AS
BEGIN
    DECLARE @ctx VARBINARY(128) = CONTEXT_INFO();
    -- 0x4150500000... = 'APP'
    IF @ctx IS NOT NULL AND LEFT(CONVERT(VARCHAR(3), CONVERT(VARBINARY(3), @ctx)), 3) = 'APP'
        RETURN 1;
    RETURN 0;
END;
GO

/* ----------------------------------------------------------------------------
   Metadatos comunes (login/host/programa) en formato JSON.
   SQL Server 2022 soporta STRING_ESCAPE para escapar comillas.
---------------------------------------------------------------------------- */
-- Se arma inline en cada trigger.


/* ============================================================================
   TABLA: usuarios
   ============================================================================ */
IF OBJECT_ID('dbo.trg_aud_usuarios', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_aud_usuarios;
GO
CREATE TRIGGER dbo.trg_aud_usuarios
ON dbo.usuarios
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF dbo.fn_auditoria_es_app() = 1 RETURN;   -- ya lo audita el servicio

    DECLARE @accion VARCHAR(50), @resultado VARCHAR(20) = 'EXITO';
    DECLARE @hayIns BIT = CASE WHEN EXISTS(SELECT 1 FROM inserted) THEN 1 ELSE 0 END;
    DECLARE @hayDel BIT = CASE WHEN EXISTS(SELECT 1 FROM deleted)  THEN 1 ELSE 0 END;

    IF @hayIns = 1 AND @hayDel = 1 SET @accion = 'BD_UPDATE_USUARIO';
    ELSE IF @hayIns = 1            SET @accion = 'BD_INSERT_USUARIO';
    ELSE                           SET @accion = 'BD_DELETE_USUARIO';

    DECLARE @info NVARCHAR(400) =
        N'{"origen":"BD_DIRECTO","login":"' + STRING_ESCAPE(SUSER_SNAME(),'json') +
        N'","host":"' + STRING_ESCAPE(ISNULL(HOST_NAME(),''),'json') +
        N'","programa":"' + STRING_ESCAPE(ISNULL(PROGRAM_NAME(),''),'json') + N'"}';

    -- INSERT / UPDATE -> tomar filas de inserted; DELETE -> de deleted
    IF @hayIns = 1
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), i.id_empresa, 'USUARIOS', @accion, 'BD',
            'Usuario', CAST(i.id AS VARCHAR(50)), @resultado, NULL, @info, SYSUTCDATETIME()
        FROM inserted i;
    END
    ELSE
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), d.id_empresa, 'USUARIOS', @accion, 'BD',
            'Usuario', CAST(d.id AS VARCHAR(50)), @resultado, NULL, @info, SYSUTCDATETIME()
        FROM deleted d;
    END
END;
GO


/* ============================================================================
   TABLA: clientes
   ============================================================================ */
IF OBJECT_ID('dbo.trg_aud_clientes', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_aud_clientes;
GO
CREATE TRIGGER dbo.trg_aud_clientes
ON dbo.clientes
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF dbo.fn_auditoria_es_app() = 1 RETURN;

    DECLARE @accion VARCHAR(50);
    DECLARE @hayIns BIT = CASE WHEN EXISTS(SELECT 1 FROM inserted) THEN 1 ELSE 0 END;
    DECLARE @hayDel BIT = CASE WHEN EXISTS(SELECT 1 FROM deleted)  THEN 1 ELSE 0 END;

    IF @hayIns = 1 AND @hayDel = 1 SET @accion = 'BD_UPDATE_CLIENTE';
    ELSE IF @hayIns = 1            SET @accion = 'BD_INSERT_CLIENTE';
    ELSE                           SET @accion = 'BD_DELETE_CLIENTE';

    DECLARE @info NVARCHAR(400) =
        N'{"origen":"BD_DIRECTO","login":"' + STRING_ESCAPE(SUSER_SNAME(),'json') +
        N'","host":"' + STRING_ESCAPE(ISNULL(HOST_NAME(),''),'json') +
        N'","programa":"' + STRING_ESCAPE(ISNULL(PROGRAM_NAME(),''),'json') + N'"}';

    IF @hayIns = 1
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), NULL, 'CLIENTES', @accion, 'BD',
            'Cliente', CAST(i.id AS VARCHAR(50)), 'EXITO', NULL, @info, SYSUTCDATETIME()
        FROM inserted i;
    END
    ELSE
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), NULL, 'CLIENTES', @accion, 'BD',
            'Cliente', CAST(d.id AS VARCHAR(50)), 'EXITO', NULL, @info, SYSUTCDATETIME()
        FROM deleted d;
    END
END;
GO


/* ============================================================================
   TABLA: empresas
   ============================================================================ */
IF OBJECT_ID('dbo.trg_aud_empresas', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_aud_empresas;
GO
CREATE TRIGGER dbo.trg_aud_empresas
ON dbo.empresas
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF dbo.fn_auditoria_es_app() = 1 RETURN;

    DECLARE @accion VARCHAR(50);
    DECLARE @hayIns BIT = CASE WHEN EXISTS(SELECT 1 FROM inserted) THEN 1 ELSE 0 END;
    DECLARE @hayDel BIT = CASE WHEN EXISTS(SELECT 1 FROM deleted)  THEN 1 ELSE 0 END;

    IF @hayIns = 1 AND @hayDel = 1 SET @accion = 'BD_UPDATE_EMPRESA';
    ELSE IF @hayIns = 1            SET @accion = 'BD_INSERT_EMPRESA';
    ELSE                           SET @accion = 'BD_DELETE_EMPRESA';

    DECLARE @info NVARCHAR(400) =
        N'{"origen":"BD_DIRECTO","login":"' + STRING_ESCAPE(SUSER_SNAME(),'json') +
        N'","host":"' + STRING_ESCAPE(ISNULL(HOST_NAME(),''),'json') +
        N'","programa":"' + STRING_ESCAPE(ISNULL(PROGRAM_NAME(),''),'json') + N'"}';

    IF @hayIns = 1
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), i.id, 'EMPRESAS', @accion, 'BD',
            'Empresa', CAST(i.id AS VARCHAR(50)), 'EXITO', NULL, @info, SYSUTCDATETIME()
        FROM inserted i;
    END
    ELSE
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), d.id, 'EMPRESAS', @accion, 'BD',
            'Empresa', CAST(d.id AS VARCHAR(50)), 'EXITO', NULL, @info, SYSUTCDATETIME()
        FROM deleted d;
    END
END;
GO


/* ============================================================================
   TABLA: cliente_empresa  (vínculos cliente <-> empresa)
   ============================================================================ */
IF OBJECT_ID('dbo.trg_aud_cliente_empresa', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_aud_cliente_empresa;
GO
CREATE TRIGGER dbo.trg_aud_cliente_empresa
ON dbo.cliente_empresa
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    IF dbo.fn_auditoria_es_app() = 1 RETURN;

    DECLARE @accion VARCHAR(50);
    DECLARE @hayIns BIT = CASE WHEN EXISTS(SELECT 1 FROM inserted) THEN 1 ELSE 0 END;
    DECLARE @hayDel BIT = CASE WHEN EXISTS(SELECT 1 FROM deleted)  THEN 1 ELSE 0 END;

    IF @hayIns = 1 AND @hayDel = 1 SET @accion = 'BD_UPDATE_VINCULO';
    ELSE IF @hayIns = 1            SET @accion = 'BD_INSERT_VINCULO';
    ELSE                           SET @accion = 'BD_DELETE_VINCULO';

    DECLARE @info NVARCHAR(400) =
        N'{"origen":"BD_DIRECTO","login":"' + STRING_ESCAPE(SUSER_SNAME(),'json') +
        N'","host":"' + STRING_ESCAPE(ISNULL(HOST_NAME(),''),'json') +
        N'","programa":"' + STRING_ESCAPE(ISNULL(PROGRAM_NAME(),''),'json') + N'"}';

    IF @hayIns = 1
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), i.id_empresa, 'CLIENTES', @accion, 'BD',
            'ClienteEmpresa', CAST(i.id AS VARCHAR(50)), 'EXITO', NULL, @info, SYSUTCDATETIME()
        FROM inserted i;
    END
    ELSE
    BEGIN
        INSERT INTO dbo.auditoria
            (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
             entidad, registro_id, resultado, ip, info_adicional, fecha)
        SELECT
            NULL, 'BD: ' + SUSER_SNAME(), d.id_empresa, 'CLIENTES', @accion, 'BD',
            'ClienteEmpresa', CAST(d.id AS VARCHAR(50)), 'EXITO', NULL, @info, SYSUTCDATETIME()
        FROM deleted d;
    END
END;
GO

PRINT 'Triggers de auditoría creados: usuarios, clientes, empresas, cliente_empresa';
GO
