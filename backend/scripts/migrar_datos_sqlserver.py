"""
Migración de DATOS desde SQL Server (inmobiliaria_db) a PostgreSQL.

Lee cada tabla de SQL Server con sqlcmd usando 'FOR JSON PATH' (maneja tipos,
NULL y escapado de forma robusta) y hace INSERT en PostgreSQL preservando los IDs.
Al final, reajusta las secuencias de identidad y verifica los conteos.

Uso (desde backend/, con el venv activado):
    python scripts/migrar_datos_sqlserver.py

Requisitos:
    - SQL Server SQLEXPRESS corriendo con la base inmobiliaria_db (solo se LEE).
    - PostgreSQL con el esquema ya creado (python seed.py ejecutado).
    - backend/.env con DATABASE_URL de PostgreSQL.

NO modifica SQL Server. Vacía (TRUNCATE) las tablas de PostgreSQL antes de cargar.
"""
import os
import sys
import json
import base64
import subprocess
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import psycopg

# ── Configuración SQL Server (origen) ──
SQLCMD = r"C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\SQLCMD.EXE"
MSSQL_SERVER = os.getenv("MSSQL_SERVER", r"localhost\SQLEXPRESS")
MSSQL_DB = os.getenv("MSSQL_DB", "inmobiliaria_db")

# ── PostgreSQL (destino) ──
def pg_dsn():
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        # psycopg (v3) acepta el formato "postgresql://"; quitar el "+psycopg"
        return url.replace("postgresql+psycopg://", "postgresql://").replace(
            "postgres://", "postgresql://"
        )
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "inmobiliaria_db")
    user = os.getenv("DB_USER", "inmobiliaria")
    pwd = os.getenv("DB_PASSWORD", "")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{name}"


# ── Orden de carga (padres antes que hijos por las FK) ──
#    Se omite 'sysdiagrams' (metadatos de SSMS, no del dominio).
ORDEN_TABLAS = [
    "usuarios",
    "empresas",
    "paises",
    "departamento",
    "ciudad",
    "clientes",
    "cliente_empresa",
    "criterios",
    "evaluaciones",
    "evaluacion_detalle",
    "documentos",
    "motor_reglas",
    "reglas",
    "historial_crediticio",
    "evaluacion_riesgo",
    "resultado_detalle",
    "detalle_operacion",
    "lista_negra_onu",
    "planes",
    "empresa_planes",
    "periodos_facturacion",
    "consumo_reportes",
    "pagos",
    "historial_empresa_planes",
    "auditoria",
    "scoring_modelo",
    "scoring_factor",
    "scoring_catalogo",
    "scoring_regla",
    "scoring_umbral",
    "scoring_evaluacion",
    "scoring_detalle",
]

# Columnas de tipo boolean en PostgreSQL (en SQL Server eran BIT 0/1).
# Se usa para convertir 0/1 -> False/True al insertar.
BOOL_COLS = {
    "usuarios": {"activo"},
    "empresas": {"activo", "consultas_habilitadas"},
    "reglas": {"es_determinante", "activo"},
    "motor_reglas": {"activo"},
    "historial_crediticio": {"en_lista_negra"},
    "resultado_detalle": {"cumplido"},
    "criterios": {"activo"},
    "planes": {"activo"},
    "scoring_modelo": {"activo"},
    "scoring_factor": {"obligatorio", "activo"},
}


MARCADOR = "@@@TABLA:"


def leer_todo_mssql():
    """
    Lee TODAS las tablas en una sola conexión de sqlcmd (evita timeouts de login
    intermitentes al abrir muchas conexiones seguidas). Devuelve {tabla: [filas]}.

    Cada tabla se emite como:
        @@@TABLA:<nombre>
        <json en una línea>   (o vacío si no hay filas)
    """
    lineas = ["SET NOCOUNT ON;"]
    for tabla in ORDEN_TABLAS:
        lineas.append(f"PRINT '{MARCADOR}{tabla}';")
        # FOR JSON PATH -> columnas y tipos correctos; INCLUDE_NULL_VALUES
        # muestra las columnas NULL de forma explícita.
        lineas.append(
            f"SELECT * FROM dbo.[{tabla}] FOR JSON PATH, INCLUDE_NULL_VALUES;"
        )
    script = "\n".join(lineas)

    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="ascii") as f:
        f.write(script)
        qfile = f.name
    out_file = qfile + ".out"
    try:
        subprocess.run(
            [
                SQLCMD, "-S", MSSQL_SERVER, "-E", "-C",
                "-l", "60",            # login timeout amplio
                "-t", "120",           # query timeout
                "-f", "65001",         # code page UTF-8 (preserva acentos/ñ)
                "-d", MSSQL_DB, "-y", "0", "-i", qfile, "-o", out_file,
            ],
            capture_output=True, text=True, timeout=300,
        )
        # utf-8-sig descarta el BOM que sqlcmd escribe al usar -f 65001
        with open(out_file, "r", encoding="utf-8-sig", errors="replace") as fh:
            texto = fh.read()
    finally:
        for p in (qfile, out_file):
            try:
                os.remove(p)
            except OSError:
                pass

    if "Login timeout" in texto or "Unable to complete login" in texto:
        raise RuntimeError(
            "SQL Server rechazó la conexión por timeout de login. "
            "Reintente (a veces la instancia SQLEXPRESS tarda en responder)."
        )

    # Parsear por marcadores
    resultado = {t: [] for t in ORDEN_TABLAS}
    tabla_actual = None
    buffer = []

    def _volcar():
        if tabla_actual is None:
            return
        raw = "".join(buffer).strip()
        if raw and raw not in ("NULL", "null"):
            try:
                resultado[tabla_actual] = json.loads(raw)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"No se pudo parsear el JSON de '{tabla_actual}': {e}\nInicio: {raw[:200]}"
                )

    for linea in texto.splitlines():
        s = linea.rstrip("\n")
        if s.startswith(MARCADOR):
            _volcar()
            tabla_actual = s[len(MARCADOR):].strip()
            buffer = []
        else:
            buffer.append(s)
    _volcar()
    return resultado


def convertir_fila(tabla, fila):
    """Aplica conversiones de tipo (BIT 0/1 -> bool) por columna."""
    bools = BOOL_COLS.get(tabla, set())
    out = {}
    for col, val in fila.items():
        if col in bools and val is not None:
            out[col] = bool(val) if isinstance(val, bool) else val in (1, "1", True, "true", "True")
        else:
            out[col] = val
    return out


def main():
    dsn = pg_dsn()
    print(f"Origen  (SQL Server): {MSSQL_SERVER} / {MSSQL_DB}")
    print(f"Destino (PostgreSQL): {dsn.split('@')[-1]}")
    print("-" * 60)

    # 1) Leer todo desde SQL Server en UNA sola conexión (evita timeouts).
    #    No se toca PostgreSQL si algo falla en la lectura.
    crudo = leer_todo_mssql()
    datos = {}
    for tabla in ORDEN_TABLAS:
        filas = crudo.get(tabla, [])
        datos[tabla] = [convertir_fila(tabla, f) for f in filas]
        print(f"  leído  {tabla:<28} {len(filas):>5} filas")

    print("-" * 60)

    conn = psycopg.connect(dsn, autocommit=False)
    try:
        with conn.cursor() as cur:
            # 2) Marcar la sesión como APP para que los triggers de auditoría
            #    NO registren esta carga masiva como operaciones directas de BD.
            cur.execute("SET app.origen = 'APP'")
            # Desactivar los triggers de auditoría durante la carga. El owner de
            # las tablas puede hacer DISABLE TRIGGER (no requiere superusuario).
            for t in ("usuarios", "clientes", "empresas", "cliente_empresa"):
                cur.execute(f'ALTER TABLE "{t}" DISABLE TRIGGER USER')

            # 3) TRUNCATE de todas las tablas (orden inverso, CASCADE, reinicia identidad)
            tablas_sql = ", ".join(f'"{t}"' for t in reversed(ORDEN_TABLAS))
            cur.execute(f"TRUNCATE {tablas_sql} RESTART IDENTITY CASCADE")

            # 4) Insertar preservando IDs
            for tabla in ORDEN_TABLAS:
                filas = datos[tabla]
                if not filas:
                    continue
                columnas = list(filas[0].keys())
                cols_sql = ", ".join(f'"{c}"' for c in columnas)
                placeholders = ", ".join(["%s"] * len(columnas))
                insert = f'INSERT INTO "{tabla}" ({cols_sql}) VALUES ({placeholders})'
                valores = [[f.get(c) for c in columnas] for f in filas]
                cur.executemany(insert, valores)
                print(f"  cargado {tabla:<28} {len(filas):>5} filas")

            # 5) Reajustar las secuencias de identidad al máximo id + 1
            print("-" * 60)
            for tabla in ORDEN_TABLAS:
                cur.execute("""
                    SELECT pg_get_serial_sequence(%s, a.attname), a.attname
                    FROM pg_attribute a
                    WHERE a.attrelid = %s::regclass
                      AND a.attname = 'id'
                      AND a.attnum > 0 AND NOT a.attisdropped
                """, (tabla, tabla))
                row = cur.fetchone()
                if row and row[0]:
                    seq = row[0]
                    cur.execute(f'SELECT COALESCE(MAX(id), 0) FROM "{tabla}"')
                    maxid = cur.fetchone()[0]
                    cur.execute("SELECT setval(%s, %s, true)", (seq, max(maxid, 1)))

            # Reactivar los triggers de auditoría
            for t in ("usuarios", "clientes", "empresas", "cliente_empresa"):
                cur.execute(f'ALTER TABLE "{t}" ENABLE TRIGGER USER')

        conn.commit()
        print("Carga confirmada (COMMIT).")

        # 6) Verificación de conteos
        print("-" * 60)
        print("VERIFICACIÓN (origen vs destino):")
        ok = True
        with conn.cursor() as cur:
            for tabla in ORDEN_TABLAS:
                cur.execute(f'SELECT COUNT(*) FROM "{tabla}"')
                pg_count = cur.fetchone()[0]
                ms_count = len(datos[tabla])
                estado = "OK" if pg_count == ms_count else "DIFERENTE"
                if pg_count != ms_count:
                    ok = False
                print(f"  {tabla:<28} SQLServer={ms_count:>5}  PostgreSQL={pg_count:>5}  {estado}")
        print("-" * 60)
        print("RESULTADO:", "todos los conteos coinciden" if ok else "HAY DIFERENCIAS, revisar")

    except Exception:
        conn.rollback()
        print("ERROR: se revirtió la transacción (ROLLBACK). PostgreSQL quedó sin cambios.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
