-- ============================================================================
--  02_functions_triggers.sql  (PostgreSQL)
--  Auditoría a nivel BASE DE DATOS.
--
--  PROPÓSITO
--  ---------
--  Complementa la auditoría a nivel servicio (backend Python). Captura cambios
--  hechos DIRECTAMENTE sobre la base (DBeaver, psql, scripts, ETL, etc.), es
--  decir, por fuera de la aplicación.
--
--  EVITAR DUPLICADOS
--  -----------------
--  La aplicación marca su sesión con un parámetro de sesión (GUC):
--        SET app.origen = 'APP';
--  (lo hace automáticamente el backend en cada checkout de conexión).
--  Si app.origen = 'APP', los triggers NO vuelven a registrar lo que ya audita
--  el servicio. Si NO está marcado, se asume operación DIRECTA en BD y el
--  trigger registra el evento con origen 'BD_DIRECTO'.
--
--  Equivalencias respecto a la versión SQL Server:
--    CONTEXT_INFO           -> current_setting('app.origen', true)
--    tablas inserted/deleted-> NEW / OLD  (triggers FOR EACH ROW)
--    SUSER_SNAME()          -> current_user
--    HOST_NAME()            -> host de inet_client_addr()
--    PROGRAM_NAME()         -> current_setting('application_name', true)
--    STRING_ESCAPE(...,json)-> jsonb_build_object(...)::text (escapado seguro)
--    SYSUTCDATETIME()       -> now() AT TIME ZONE 'utc'
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Helper: ¿la operación viene de la aplicación?
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_auditoria_es_app()
RETURNS boolean
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN COALESCE(current_setting('app.origen', true), '') = 'APP';
END;
$$;


-- ----------------------------------------------------------------------------
-- Helper: metadatos de sesión (login/host/programa) como texto JSON.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_auditoria_info()
RETURNS text
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN jsonb_build_object(
        'origen',   'BD_DIRECTO',
        'login',    current_user,
        'host',     COALESCE(host(inet_client_addr()), ''),
        'programa', COALESCE(current_setting('application_name', true), '')
    )::text;
END;
$$;


-- ============================================================================
--  TABLA: usuarios
-- ============================================================================
CREATE OR REPLACE FUNCTION trg_fn_aud_usuarios()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_accion text;
    v_row    record;
BEGIN
    IF fn_auditoria_es_app() THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    IF    TG_OP = 'INSERT' THEN v_accion := 'BD_INSERT_USUARIO'; v_row := NEW;
    ELSIF TG_OP = 'UPDATE' THEN v_accion := 'BD_UPDATE_USUARIO'; v_row := NEW;
    ELSE                        v_accion := 'BD_DELETE_USUARIO'; v_row := OLD;
    END IF;

    INSERT INTO auditoria
        (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
         entidad, registro_id, resultado, ip, info_adicional, fecha)
    VALUES
        (NULL, 'BD: ' || current_user, v_row.id_empresa, 'USUARIOS', v_accion, 'BD',
         'Usuario', v_row.id::text, 'EXITO', NULL, fn_auditoria_info(),
         now() AT TIME ZONE 'utc');

    RETURN COALESCE(NEW, OLD);
END;
$$;

DROP TRIGGER IF EXISTS trg_aud_usuarios ON usuarios;
CREATE TRIGGER trg_aud_usuarios
    AFTER INSERT OR UPDATE OR DELETE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION trg_fn_aud_usuarios();


-- ============================================================================
--  TABLA: clientes
-- ============================================================================
CREATE OR REPLACE FUNCTION trg_fn_aud_clientes()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_accion text;
    v_row    record;
BEGIN
    IF fn_auditoria_es_app() THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    IF    TG_OP = 'INSERT' THEN v_accion := 'BD_INSERT_CLIENTE'; v_row := NEW;
    ELSIF TG_OP = 'UPDATE' THEN v_accion := 'BD_UPDATE_CLIENTE'; v_row := NEW;
    ELSE                        v_accion := 'BD_DELETE_CLIENTE'; v_row := OLD;
    END IF;

    INSERT INTO auditoria
        (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
         entidad, registro_id, resultado, ip, info_adicional, fecha)
    VALUES
        (NULL, 'BD: ' || current_user, NULL, 'CLIENTES', v_accion, 'BD',
         'Cliente', v_row.id::text, 'EXITO', NULL, fn_auditoria_info(),
         now() AT TIME ZONE 'utc');

    RETURN COALESCE(NEW, OLD);
END;
$$;

DROP TRIGGER IF EXISTS trg_aud_clientes ON clientes;
CREATE TRIGGER trg_aud_clientes
    AFTER INSERT OR UPDATE OR DELETE ON clientes
    FOR EACH ROW EXECUTE FUNCTION trg_fn_aud_clientes();


-- ============================================================================
--  TABLA: empresas
-- ============================================================================
CREATE OR REPLACE FUNCTION trg_fn_aud_empresas()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_accion text;
    v_row    record;
BEGIN
    IF fn_auditoria_es_app() THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    IF    TG_OP = 'INSERT' THEN v_accion := 'BD_INSERT_EMPRESA'; v_row := NEW;
    ELSIF TG_OP = 'UPDATE' THEN v_accion := 'BD_UPDATE_EMPRESA'; v_row := NEW;
    ELSE                        v_accion := 'BD_DELETE_EMPRESA'; v_row := OLD;
    END IF;

    INSERT INTO auditoria
        (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
         entidad, registro_id, resultado, ip, info_adicional, fecha)
    VALUES
        (NULL, 'BD: ' || current_user, v_row.id, 'EMPRESAS', v_accion, 'BD',
         'Empresa', v_row.id::text, 'EXITO', NULL, fn_auditoria_info(),
         now() AT TIME ZONE 'utc');

    RETURN COALESCE(NEW, OLD);
END;
$$;

DROP TRIGGER IF EXISTS trg_aud_empresas ON empresas;
CREATE TRIGGER trg_aud_empresas
    AFTER INSERT OR UPDATE OR DELETE ON empresas
    FOR EACH ROW EXECUTE FUNCTION trg_fn_aud_empresas();


-- ============================================================================
--  TABLA: cliente_empresa
-- ============================================================================
CREATE OR REPLACE FUNCTION trg_fn_aud_cliente_empresa()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_accion text;
    v_row    record;
BEGIN
    IF fn_auditoria_es_app() THEN
        RETURN COALESCE(NEW, OLD);
    END IF;

    IF    TG_OP = 'INSERT' THEN v_accion := 'BD_INSERT_VINCULO'; v_row := NEW;
    ELSIF TG_OP = 'UPDATE' THEN v_accion := 'BD_UPDATE_VINCULO'; v_row := NEW;
    ELSE                        v_accion := 'BD_DELETE_VINCULO'; v_row := OLD;
    END IF;

    INSERT INTO auditoria
        (usuario_id, usuario_nombre, id_empresa, tipo_evento, accion, modulo,
         entidad, registro_id, resultado, ip, info_adicional, fecha)
    VALUES
        (NULL, 'BD: ' || current_user, v_row.id_empresa, 'CLIENTES', v_accion, 'BD',
         'ClienteEmpresa', v_row.id::text, 'EXITO', NULL, fn_auditoria_info(),
         now() AT TIME ZONE 'utc');

    RETURN COALESCE(NEW, OLD);
END;
$$;

DROP TRIGGER IF EXISTS trg_aud_cliente_empresa ON cliente_empresa;
CREATE TRIGGER trg_aud_cliente_empresa
    AFTER INSERT OR UPDATE OR DELETE ON cliente_empresa
    FOR EACH ROW EXECUTE FUNCTION trg_fn_aud_cliente_empresa();


DO $$ BEGIN
    RAISE NOTICE 'Triggers de auditoría creados: usuarios, clientes, empresas, cliente_empresa';
END $$;
