-- ============================================================
-- SCRIPT SQL COMPLETO - Sistema Experto de Scoring Comercial
-- Base de datos: inmobiliaria_db  |  Motor: SQL Server 2022
-- Contiene: CREATE TABLE, PK, UNIQUE, FOREIGN KEY, INDICES y TRIGGERS
-- ============================================================

-- Tabla: usuarios
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    activo BIT NOT NULL,
    creado_en DATETIME2 NOT NULL,
    actualizado_en DATETIME2 NOT NULL,
    id_empresa INT NULL,
    totp_secret VARCHAR(255) NULL,
    totp_estado VARCHAR(20) NULL,
    totp_fecha_config DATETIME2 NULL,
    totp_fecha_reset DATETIME2 NULL,
    CONSTRAINT PK_usuarios PRIMARY KEY (id)
);
GO

-- Tabla: empresas
CREATE TABLE empresas (
    id INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    ruc VARCHAR(30) NULL,
    direccion VARCHAR(255) NULL,
    telefono VARCHAR(30) NULL,
    email VARCHAR(150) NULL,
    activo BIT NULL,
    creado_en DATETIME NULL,
    consultas_habilitadas BIT NOT NULL,
    motivo_bloqueo VARCHAR(50) NULL,
    fecha_bloqueo DATETIME2 NULL,
    fecha_desbloqueo DATETIME2 NULL,
    CONSTRAINT PK_empresas PRIMARY KEY (id)
);
GO

-- Tabla: paises
CREATE TABLE paises (
    id_pais VARCHAR(3) NOT NULL,
    nombre_pais VARCHAR(20) NOT NULL,
    CONSTRAINT PK_paises PRIMARY KEY (id_pais)
);
GO

-- Tabla: departamento
CREATE TABLE departamento (
    id_departamento INT NOT NULL,
    nombre_departamento VARCHAR(100) NOT NULL,
    CONSTRAINT PK_departamento PRIMARY KEY (id_departamento)
);
GO

-- Tabla: ciudad
CREATE TABLE ciudad (
    id_ciudad INT NOT NULL,
    nombre_ciudad VARCHAR(100) NOT NULL,
    id_departamento INT NOT NULL
);
GO

-- Tabla: clientes
CREATE TABLE clientes (
    id INT IDENTITY(1,1) NOT NULL,
    tipo_doc VARCHAR(10) NOT NULL,
    num_doc VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NULL,
    email VARCHAR(150) NULL,
    telefono VARCHAR(20) NULL,
    direccion VARCHAR(255) NULL,
    fecha_nacimiento DATE NULL,
    estado VARCHAR(20) NOT NULL,
    creado_por INT NULL,
    creado_en DATETIME2 NOT NULL,
    nacionalidad VARCHAR(3) NULL,
    id_ciudad INT NULL,
    CONSTRAINT PK_clientes PRIMARY KEY (id)
);
GO

-- Tabla: cliente_empresa
CREATE TABLE cliente_empresa (
    id INT IDENTITY(1,1) NOT NULL,
    id_cliente INT NOT NULL,
    id_empresa INT NOT NULL,
    estado VARCHAR(20) NULL,
    creado_en DATETIME NULL,
    CONSTRAINT PK_cliente_empresa PRIMARY KEY (id)
);
GO

-- Tabla: documentos
CREATE TABLE documentos (
    id INT IDENTITY(1,1) NOT NULL,
    cliente_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta VARCHAR(500) NOT NULL,
    subido_por INT NULL,
    subido_en DATETIME2 NOT NULL,
    CONSTRAINT PK_documentos PRIMARY KEY (id)
);
GO

-- Tabla: historial_crediticio
CREATE TABLE historial_crediticio (
    id INT IDENTITY(1,1) NOT NULL,
    cliente_id INT NOT NULL,
    fuente_externa VARCHAR(100) NULL,
    score_externo NUMERIC(6,2) NULL,
    cantidad_atrasos INT NULL,
    deuda_total_sistema NUMERIC(14,2) NULL,
    historial_pagos VARCHAR(20) NULL,
    en_lista_negra BIT NULL,
    nivel_endeudamiento NUMERIC(5,2) NULL,
    meses_empleo_actual INT NULL,
    tipo_empleo VARCHAR(50) NULL,
    referencias_personales VARCHAR(20) NULL,
    fecha_consulta DATETIME NULL,
    actualizado_en DATETIME NULL,
    CONSTRAINT PK_historial_crediticio PRIMARY KEY (id)
);
GO

-- Tabla: criterios
CREATE TABLE criterios (
    id INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NULL,
    peso DECIMAL(5,2) NOT NULL,
    activo BIT NOT NULL,
    CONSTRAINT PK_criterios PRIMARY KEY (id)
);
GO

-- Tabla: evaluaciones
CREATE TABLE evaluaciones (
    id INT IDENTITY(1,1) NOT NULL,
    cliente_id INT NOT NULL,
    evaluador_id INT NOT NULL,
    fecha DATETIME2 NOT NULL,
    puntaje_total DECIMAL(5,2) NULL,
    resultado VARCHAR(20) NULL,
    observaciones NVARCHAR(MAX) NULL,
    estado VARCHAR(20) NOT NULL,
    CONSTRAINT PK_evaluaciones PRIMARY KEY (id)
);
GO

-- Tabla: evaluacion_detalle
CREATE TABLE evaluacion_detalle (
    id INT IDENTITY(1,1) NOT NULL,
    evaluacion_id INT NOT NULL,
    criterio_id INT NOT NULL,
    valor DECIMAL(5,2) NOT NULL,
    comentario VARCHAR(255) NULL,
    CONSTRAINT PK_evaluacion_detalle PRIMARY KEY (id)
);
GO

-- Tabla: motor_reglas
CREATE TABLE motor_reglas (
    id INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    descripcion VARCHAR(255) NULL,
    activo BIT NULL,
    creado_por INT NULL,
    creado_en DATETIME NULL,
    id_empresa_motor INT NULL,
    CONSTRAINT PK_motor_reglas PRIMARY KEY (id)
);
GO

-- Tabla: reglas
CREATE TABLE reglas (
    id INT IDENTITY(1,1) NOT NULL,
    motor_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NULL,
    parametro VARCHAR(50) NOT NULL,
    operador VARCHAR(10) NOT NULL,
    valor_referencia VARCHAR(100) NOT NULL,
    tipo_valor VARCHAR(20) NOT NULL,
    peso_puntos NUMERIC(6,2) NOT NULL,
    es_determinante BIT NULL,
    activo BIT NULL,
    orden INT NULL,
    CONSTRAINT PK_reglas PRIMARY KEY (id)
);
GO

-- Tabla: evaluacion_riesgo
CREATE TABLE evaluacion_riesgo (
    id INT IDENTITY(1,1) NOT NULL,
    cliente_id INT NOT NULL,
    motor_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_analisis DATETIME NULL,
    score_final NUMERIC(6,2) NULL,
    score_maximo NUMERIC(6,2) NULL,
    categoria_riesgo VARCHAR(20) NULL,
    estado VARCHAR(20) NULL,
    observaciones VARCHAR(MAX) NULL,
    regla_determinante_id INT NULL,
    id_empresa INT NULL,
    CONSTRAINT PK_evaluacion_riesgo PRIMARY KEY (id)
);
GO

-- Tabla: resultado_detalle
CREATE TABLE resultado_detalle (
    id INT IDENTITY(1,1) NOT NULL,
    evaluacion_id INT NOT NULL,
    regla_id INT NOT NULL,
    cumplido BIT NOT NULL,
    valor_evaluado VARCHAR(100) NULL,
    puntos_obtenidos NUMERIC(6,2) NULL,
    CONSTRAINT PK_resultado_detalle PRIMARY KEY (id)
);
GO

-- Tabla: detalle_operacion
CREATE TABLE detalle_operacion (
    id INT IDENTITY(1,1) NOT NULL,
    evaluacion_id INT NOT NULL,
    tipo_propiedad VARCHAR(50) NOT NULL,
    valor_propiedad NUMERIC(14,2) NOT NULL,
    monto_solicitado NUMERIC(14,2) NOT NULL,
    plazo_meses INT NOT NULL,
    ubicacion VARCHAR(255) NULL,
    destino VARCHAR(50) NULL,
    CONSTRAINT PK_detalle_operacion PRIMARY KEY (id)
);
GO

-- Tabla: scoring_modelo
CREATE TABLE scoring_modelo (
    id INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    descripcion VARCHAR(500) NULL,
    id_empresa INT NOT NULL,
    activo BIT NULL,
    creado_en DATETIME NULL,
    CONSTRAINT PK_scoring_modelo PRIMARY KEY (id)
);
GO

-- Tabla: scoring_factor
CREATE TABLE scoring_factor (
    id INT IDENTITY(1,1) NOT NULL,
    modelo_id INT NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500) NULL,
    tipo_dato VARCHAR(20) NOT NULL,
    tipo_persona VARCHAR(10) NOT NULL,
    categoria VARCHAR(20) NULL,
    obligatorio BIT NULL,
    activo BIT NULL,
    orden INT NULL,
    CONSTRAINT PK_scoring_factor PRIMARY KEY (id)
);
GO

-- Tabla: scoring_catalogo
CREATE TABLE scoring_catalogo (
    id INT IDENTITY(1,1) NOT NULL,
    factor_id INT NOT NULL,
    valor VARCHAR(100) NOT NULL,
    etiqueta VARCHAR(100) NOT NULL,
    orden INT NULL,
    CONSTRAINT PK_scoring_catalogo PRIMARY KEY (id)
);
GO

-- Tabla: scoring_regla
CREATE TABLE scoring_regla (
    id INT IDENTITY(1,1) NOT NULL,
    factor_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    operador VARCHAR(10) NOT NULL,
    valor_min VARCHAR(100) NULL,
    valor_max VARCHAR(100) NULL,
    nivel VARCHAR(10) NOT NULL,
    peso NUMERIC(8,2) NOT NULL,
    explicacion VARCHAR(500) NULL,
    orden INT NULL,
    CONSTRAINT PK_scoring_regla PRIMARY KEY (id)
);
GO

-- Tabla: scoring_umbral
CREATE TABLE scoring_umbral (
    id INT IDENTITY(1,1) NOT NULL,
    modelo_id INT NOT NULL,
    nivel VARCHAR(10) NOT NULL,
    score_min NUMERIC(8,2) NOT NULL,
    score_max NUMERIC(8,2) NOT NULL,
    descripcion VARCHAR(200) NULL,
    CONSTRAINT PK_scoring_umbral PRIMARY KEY (id)
);
GO

-- Tabla: scoring_evaluacion
CREATE TABLE scoring_evaluacion (
    id INT IDENTITY(1,1) NOT NULL,
    cliente_id INT NOT NULL,
    modelo_id INT NOT NULL,
    modelo_version VARCHAR(20) NOT NULL,
    usuario_id INT NOT NULL,
    id_empresa INT NOT NULL,
    tipo_persona VARCHAR(10) NOT NULL,
    fecha DATETIME NULL,
    score_total NUMERIC(8,2) NOT NULL,
    clasificacion VARCHAR(10) NOT NULL,
    explicacion VARCHAR(MAX) NULL,
    factores_evaluados INT NULL,
    factores_sin_dato INT NULL,
    estado VARCHAR(20) NULL,
    CONSTRAINT PK_scoring_evaluacion PRIMARY KEY (id)
);
GO

-- Tabla: scoring_detalle
CREATE TABLE scoring_detalle (
    id INT IDENTITY(1,1) NOT NULL,
    evaluacion_id INT NOT NULL,
    factor_codigo VARCHAR(50) NOT NULL,
    factor_nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(20) NULL,
    valor_original VARCHAR(200) NULL,
    estado VARCHAR(20) NOT NULL,
    regla_aplicada VARCHAR(100) NULL,
    nivel VARCHAR(10) NULL,
    peso NUMERIC(8,2) NULL,
    explicacion VARCHAR(500) NULL,
    CONSTRAINT PK_scoring_detalle PRIMARY KEY (id)
);
GO

-- Tabla: planes
CREATE TABLE planes (
    id INT IDENTITY(1,1) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    cantidad_reportes_incluidos INT NOT NULL,
    precio_plan NUMERIC(14,0) NOT NULL,
    precio_reporte_incluido NUMERIC(14,0) NOT NULL,
    precio_reporte_sobre_facturado NUMERIC(14,0) NOT NULL,
    activo BIT NULL,
    creado_en DATETIME NULL,
    actualizado_en DATETIME NULL,
    CONSTRAINT PK_planes PRIMARY KEY (id)
);
GO

-- Tabla: empresa_planes
CREATE TABLE empresa_planes (
    id INT IDENTITY(1,1) NOT NULL,
    empresa_id INT NOT NULL,
    plan_id INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NULL,
    estado VARCHAR(20) NULL,
    precio_plan_contratado NUMERIC(14,0) NOT NULL,
    cantidad_reportes_incluidos INT NOT NULL,
    precio_reporte_sobre_facturado NUMERIC(14,0) NOT NULL,
    creado_en DATETIME NULL,
    CONSTRAINT PK_empresa_planes PRIMARY KEY (id)
);
GO

-- Tabla: periodos_facturacion
CREATE TABLE periodos_facturacion (
    id INT IDENTITY(1,1) NOT NULL,
    empresa_id INT NOT NULL,
    empresa_plan_id INT NOT NULL,
    anio INT NOT NULL,
    mes INT NOT NULL,
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    cantidad_reportes_incluidos INT NOT NULL,
    reportes_consumidos INT NULL,
    reportes_sobre_facturados INT NULL,
    monto_plan NUMERIC(14,0) NULL,
    monto_sobre_facturado NUMERIC(14,0) NULL,
    monto_total NUMERIC(14,0) NULL,
    monto_pagado NUMERIC(14,0) NULL,
    saldo_pendiente NUMERIC(14,0) NULL,
    estado VARCHAR(20) NULL,
    CONSTRAINT PK_periodos_facturacion PRIMARY KEY (id)
);
GO

-- Tabla: consumo_reportes
CREATE TABLE consumo_reportes (
    id INT IDENTITY(1,1) NOT NULL,
    empresa_id INT NOT NULL,
    usuario_id INT NOT NULL,
    evaluacion_id INT NOT NULL,
    periodo_facturacion_id INT NOT NULL,
    tipo_consumo VARCHAR(20) NOT NULL,
    precio_unitario NUMERIC(14,0) NOT NULL,
    fecha_consumo DATETIME NULL,
    CONSTRAINT PK_consumo_reportes PRIMARY KEY (id)
);
GO

-- Tabla: pagos
CREATE TABLE pagos (
    id INT IDENTITY(1,1) NOT NULL,
    empresa_id INT NOT NULL,
    periodo_facturacion_id INT NOT NULL,
    monto NUMERIC(14,0) NOT NULL,
    proveedor VARCHAR(50) NULL,
    referencia_externa VARCHAR(100) NULL,
    estado VARCHAR(20) NULL,
    metodo_pago VARCHAR(50) NULL,
    observacion VARCHAR(255) NULL,
    fecha_inicio DATETIME NULL,
    fecha_confirmacion DATETIME NULL,
    CONSTRAINT PK_pagos PRIMARY KEY (id)
);
GO

-- Tabla: historial_empresa_planes
CREATE TABLE historial_empresa_planes (
    id INT IDENTITY(1,1) NOT NULL,
    empresa_id INT NOT NULL,
    plan_id INT NOT NULL,
    plan_nombre VARCHAR(50) NOT NULL,
    precio_plan NUMERIC(14,0) NOT NULL,
    cantidad_reportes INT NOT NULL,
    precio_sobre_fact NUMERIC(14,0) NOT NULL,
    fecha_desde DATETIME NOT NULL,
    fecha_hasta DATETIME NULL,
    cambiado_por INT NULL,
    fecha_cambio DATETIME NULL,
    CONSTRAINT PK_historial_empresa_planes PRIMARY KEY (id)
);
GO

-- Tabla: auditoria
CREATE TABLE auditoria (
    id INT IDENTITY(1,1) NOT NULL,
    usuario_id INT NULL,
    usuario_nombre VARCHAR(150) NULL,
    id_empresa INT NULL,
    tipo_evento VARCHAR(30) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    modulo VARCHAR(50) NULL,
    entidad VARCHAR(50) NULL,
    registro_id VARCHAR(50) NULL,
    resultado VARCHAR(20) NULL,
    ip VARCHAR(50) NULL,
    info_adicional VARCHAR(MAX) NULL,
    valores_anteriores VARCHAR(MAX) NULL,
    valores_nuevos VARCHAR(MAX) NULL,
    fecha DATETIME NULL,
    CONSTRAINT PK_auditoria PRIMARY KEY (id)
);
GO

-- Tabla: lista_negra_onu
CREATE TABLE lista_negra_onu (
    id INT IDENTITY(1,1) NOT NULL,
    registro VARCHAR(20) NULL,
    nombre VARCHAR(150) NULL,
    apellido VARCHAR(150) NULL,
    cargo VARCHAR(500) NULL,
    fecha_nacimiento VARCHAR(200) NULL,
    nacionalidad VARCHAR(200) NULL,
    num_identidad VARCHAR(300) NULL,
    num_pasaporte VARCHAR(500) NULL,
    otros VARCHAR(MAX) NULL,
    CONSTRAINT PK_lista_negra_onu PRIMARY KEY (id)
);
GO

-- ---------- RESTRICCIONES UNIQUE ----------
ALTER TABLE historial_crediticio ADD CONSTRAINT UQ_historial_crediticio_cliente_id UNIQUE (cliente_id);
ALTER TABLE planes ADD CONSTRAINT UQ_planes_nombre UNIQUE (nombre);
ALTER TABLE periodos_facturacion ADD CONSTRAINT UQ_periodos_facturacion_empresa_id_anio_mes UNIQUE (empresa_id, anio, mes);
ALTER TABLE consumo_reportes ADD CONSTRAINT UQ_consumo_reportes_evaluacion_id_empresa_id UNIQUE (evaluacion_id, empresa_id);
ALTER TABLE usuarios ADD CONSTRAINT UQ_usuarios_email UNIQUE (email);
ALTER TABLE clientes ADD CONSTRAINT UQ_clientes_num_doc UNIQUE (num_doc);
ALTER TABLE empresas ADD CONSTRAINT UQ_empresas_ruc UNIQUE (ruc);
ALTER TABLE cliente_empresa ADD CONSTRAINT UQ_cliente_empresa_id_cliente_id_empresa UNIQUE (id_cliente, id_empresa);
GO

-- ---------- CLAVES FORANEAS (FOREIGN KEY) ----------
ALTER TABLE ciudad ADD CONSTRAINT FK__ciudad__id_depar__45BE5BA9 FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento);
ALTER TABLE cliente_empresa ADD CONSTRAINT FK__cliente_e__id_cl__690797E6 FOREIGN KEY (id_cliente) REFERENCES clientes(id);
ALTER TABLE cliente_empresa ADD CONSTRAINT FK__cliente_e__id_em__69FBBC1F FOREIGN KEY (id_empresa) REFERENCES empresas(id);
ALTER TABLE clientes ADD CONSTRAINT FK_clientes_creado_por FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE clientes ADD CONSTRAINT FK_clientes_paises FOREIGN KEY (nacionalidad) REFERENCES paises(id_pais);
ALTER TABLE consumo_reportes ADD CONSTRAINT FK_consumo_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id);
ALTER TABLE consumo_reportes ADD CONSTRAINT FK__consumo_r__perio__27F8EE98 FOREIGN KEY (periodo_facturacion_id) REFERENCES periodos_facturacion(id);
ALTER TABLE detalle_operacion ADD CONSTRAINT FK__detalle_o__evalu__3C34F16F FOREIGN KEY (evaluacion_id) REFERENCES evaluacion_riesgo(id);
ALTER TABLE documentos ADD CONSTRAINT FK_documentos_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id);
ALTER TABLE documentos ADD CONSTRAINT FK_documentos_usuario FOREIGN KEY (subido_por) REFERENCES usuarios(id);
ALTER TABLE empresa_planes ADD CONSTRAINT FK_empplanes_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id);
ALTER TABLE empresa_planes ADD CONSTRAINT FK__empresa_p__plan___2057CCD0 FOREIGN KEY (plan_id) REFERENCES planes(id);
ALTER TABLE evaluacion_detalle ADD CONSTRAINT FK_eval_detalle_evaluacion FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id);
ALTER TABLE evaluacion_detalle ADD CONSTRAINT FK_eval_detalle_criterio FOREIGN KEY (criterio_id) REFERENCES criterios(id);
ALTER TABLE evaluacion_riesgo ADD CONSTRAINT FK__evaluacio__clien__0C85DE4D FOREIGN KEY (cliente_id) REFERENCES clientes(id);
ALTER TABLE evaluacion_riesgo ADD CONSTRAINT FK__evaluacio__motor__0D7A0286 FOREIGN KEY (motor_id) REFERENCES motor_reglas(id);
ALTER TABLE evaluacion_riesgo ADD CONSTRAINT FK__evaluacio__usuar__0E6E26BF FOREIGN KEY (usuario_id) REFERENCES usuarios(id);
ALTER TABLE evaluacion_riesgo ADD CONSTRAINT FK__evaluacio__regla__0F624AF8 FOREIGN KEY (regla_determinante_id) REFERENCES reglas(id);
ALTER TABLE evaluaciones ADD CONSTRAINT FK_evaluaciones_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id);
ALTER TABLE evaluaciones ADD CONSTRAINT FK_evaluaciones_evaluador FOREIGN KEY (evaluador_id) REFERENCES usuarios(id);
ALTER TABLE historial_crediticio ADD CONSTRAINT FK__historial__clien__06CD04F7 FOREIGN KEY (cliente_id) REFERENCES clientes(id);
ALTER TABLE historial_empresa_planes ADD CONSTRAINT FK_histempplan_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id);
ALTER TABLE historial_empresa_planes ADD CONSTRAINT FK_histempplan_plan FOREIGN KEY (plan_id) REFERENCES planes(id);
ALTER TABLE historial_empresa_planes ADD CONSTRAINT FK_histempplan_usuario FOREIGN KEY (cambiado_por) REFERENCES usuarios(id);
ALTER TABLE motor_reglas ADD CONSTRAINT FK__motor_reg__cread__02FC7413 FOREIGN KEY (creado_por) REFERENCES usuarios(id);
ALTER TABLE pagos ADD CONSTRAINT FK_pagos_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id);
ALTER TABLE pagos ADD CONSTRAINT FK__pagos__periodo_f__2AD55B43 FOREIGN KEY (periodo_facturacion_id) REFERENCES periodos_facturacion(id);
ALTER TABLE periodos_facturacion ADD CONSTRAINT FK_periodos_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id);
ALTER TABLE periodos_facturacion ADD CONSTRAINT FK__periodos___empre__24285DB4 FOREIGN KEY (empresa_plan_id) REFERENCES empresa_planes(id);
ALTER TABLE reglas ADD CONSTRAINT FK__reglas__motor_id__09A971A2 FOREIGN KEY (motor_id) REFERENCES motor_reglas(id);
ALTER TABLE resultado_detalle ADD CONSTRAINT FK__resultado__evalu__123EB7A3 FOREIGN KEY (evaluacion_id) REFERENCES evaluacion_riesgo(id);
ALTER TABLE resultado_detalle ADD CONSTRAINT FK__resultado__regla__1332DBDC FOREIGN KEY (regla_id) REFERENCES reglas(id);
ALTER TABLE scoring_catalogo ADD CONSTRAINT FK__scoring_c__facto__7FEAFD3E FOREIGN KEY (factor_id) REFERENCES scoring_factor(id);
ALTER TABLE scoring_detalle ADD CONSTRAINT FK__scoring_d__evalu__05A3D694 FOREIGN KEY (evaluacion_id) REFERENCES scoring_evaluacion(id);
ALTER TABLE scoring_evaluacion ADD CONSTRAINT FK_scoreval_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id);
ALTER TABLE scoring_evaluacion ADD CONSTRAINT FK__scoring_e__model__7D0E9093 FOREIGN KEY (modelo_id) REFERENCES scoring_modelo(id);
ALTER TABLE scoring_factor ADD CONSTRAINT FK__scoring_f__model__7755B73D FOREIGN KEY (modelo_id) REFERENCES scoring_modelo(id);
ALTER TABLE scoring_regla ADD CONSTRAINT FK__scoring_r__facto__02C769E9 FOREIGN KEY (factor_id) REFERENCES scoring_factor(id);
ALTER TABLE scoring_umbral ADD CONSTRAINT FK__scoring_u__model__7A3223E8 FOREIGN KEY (modelo_id) REFERENCES scoring_modelo(id);
GO


-- ============================================================
-- TRIGGERS DE AUDITORIA (a nivel base de datos)
-- ============================================================

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
