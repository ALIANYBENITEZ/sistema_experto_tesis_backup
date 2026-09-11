/* ============================================================================
   07_fk_faltantes.sql
   Agrega las claves foraneas (FOREIGN KEY) que faltaban en la base de datos
   para dejar el modelo fisico consistente con el modelo logico.

   Se agregan solo relaciones que corresponden segun las reglas de negocio.
   Las tablas 'auditoria' y 'lista_negra_onu' NO llevan FK a proposito:
     - auditoria: es una bitacora historica; debe conservar los registros
       aunque el usuario/empresa original se elimine (por eso guarda copias).
     - lista_negra_onu: es una tabla de referencia externa (ONU/OFAC); la
       comparacion con clientes se hace por nombre/documento (LIKE), no por ID.
   ============================================================================ */

-- ── Asegurar PRIMARY KEY en paises.id_pais (requisito para la FK) ──
IF NOT EXISTS (
    SELECT 1 FROM sys.key_constraints
    WHERE type = 'PK' AND parent_object_id = OBJECT_ID('paises')
)
BEGIN
    -- id_pais debe ser NOT NULL para ser PK
    ALTER TABLE paises ALTER COLUMN id_pais VARCHAR(3) NOT NULL;
    ALTER TABLE paises ADD CONSTRAINT PK_paises PRIMARY KEY (id_pais);
END
GO

-- ── Cliente -> Pais (nacionalidad) ──
-- Nota: clientes.nacionalidad es VARCHAR(10); se ajusta a VARCHAR(3) para
-- coincidir con paises.id_pais y permitir la FK.
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_clientes_paises')
BEGIN
    ALTER TABLE clientes ALTER COLUMN nacionalidad VARCHAR(3) NULL;
    ALTER TABLE clientes
        ADD CONSTRAINT FK_clientes_paises
        FOREIGN KEY (nacionalidad) REFERENCES paises(id_pais);
END
GO

-- ── Historial de planes de empresa -> Empresa ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_histempplan_empresa')
BEGIN
    ALTER TABLE historial_empresa_planes
        ADD CONSTRAINT FK_histempplan_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id);
END
GO

-- ── Historial de planes de empresa -> Plan ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_histempplan_plan')
BEGIN
    ALTER TABLE historial_empresa_planes
        ADD CONSTRAINT FK_histempplan_plan
        FOREIGN KEY (plan_id) REFERENCES planes(id);
END
GO

-- ── Historial de planes de empresa -> Usuario que realizo el cambio ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_histempplan_usuario')
BEGIN
    ALTER TABLE historial_empresa_planes
        ADD CONSTRAINT FK_histempplan_usuario
        FOREIGN KEY (cambiado_por) REFERENCES usuarios(id);
END
GO

-- ── Empresa_planes -> Empresa (relacion logica que faltaba) ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_empplanes_empresa')
BEGIN
    ALTER TABLE empresa_planes
        ADD CONSTRAINT FK_empplanes_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id);
END
GO

-- ── Periodos_facturacion -> Empresa ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_periodos_empresa')
BEGIN
    ALTER TABLE periodos_facturacion
        ADD CONSTRAINT FK_periodos_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id);
END
GO

-- ── Consumo_reportes -> Empresa ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_consumo_empresa')
BEGIN
    ALTER TABLE consumo_reportes
        ADD CONSTRAINT FK_consumo_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id);
END
GO

-- ── Pagos -> Empresa ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_pagos_empresa')
BEGIN
    ALTER TABLE pagos
        ADD CONSTRAINT FK_pagos_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id);
END
GO

-- ── Scoring_evaluacion -> Cliente ──
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_scoreval_cliente')
BEGIN
    ALTER TABLE scoring_evaluacion
        ADD CONSTRAINT FK_scoreval_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes(id);
END
GO

PRINT 'FK faltantes agregadas correctamente';
GO
