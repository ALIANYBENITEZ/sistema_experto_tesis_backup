<#
============================================================
  restore_db.ps1
  Restaura la base de datos a partir de un archivo .bak.

  Uso:
      # Restaura el .bak MÁS RECIENTE de la carpeta backups/
      .\backend\scripts\restore_db.ps1

      # Restaura un archivo específico
      .\backend\scripts\restore_db.ps1 -BakFile "C:\ruta\inmobiliaria_db_20260911_201424.bak"

      # En otra PC con otra instancia
      .\backend\scripts\restore_db.ps1 -Server "MI-PC\SQLEXPRESS"

  ADVERTENCIA: si la base ya existe, se REEMPLAZA por completo
  (se pierden los datos actuales). Se pide confirmación.
============================================================
#>
param(
    [string]$Server   = "DESKTOP-8242966\SQLEXPRESS",
    [string]$Database = "inmobiliaria_db",
    [string]$BakFile  = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$backupsDir  = Join-Path $projectRoot "backups"

# 1) Determinar el .bak a restaurar
if (-not $BakFile) {
    $ultimo = Get-ChildItem $backupsDir -Filter *.bak -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $ultimo) {
        throw "No se encontró ningún .bak en $backupsDir. Indique uno con -BakFile."
    }
    $BakFile = $ultimo.FullName
}
if (-not (Test-Path $BakFile)) { throw "No existe el archivo: $BakFile" }

Write-Host "Archivo a restaurar : $BakFile"
Write-Host "Base de datos       : $Database"
Write-Host "Servidor            : $Server"
Write-Host ""
Write-Host "ADVERTENCIA: si '$Database' ya existe, se reemplazara por completo." -ForegroundColor Yellow
$conf = Read-Host "Escriba 'SI' para continuar"
if ($conf -ne "SI") { Write-Host "Operacion cancelada."; return }

# 2) SQL Server solo lee el .bak desde rutas donde tiene permisos.
#    Copiamos el .bak a la carpeta de backups de la instancia (con elevación).
$sqlBackupDir = (sqlcmd -S $Server -E -C -h -1 -W -Q `
    "SET NOCOUNT ON; SELECT CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS nvarchar(500));").Trim()
if (-not $sqlBackupDir) { throw "No se pudo determinar la carpeta de backups de SQL Server." }

$fname     = Split-Path $BakFile -Leaf
$srcDir    = Split-Path $BakFile -Parent
$sqlBak    = Join-Path $sqlBackupDir $fname

Write-Host "Copiando el .bak a la carpeta de SQL Server (acepte el aviso de administrador)..."
$p = Start-Process -FilePath "robocopy.exe" `
    -ArgumentList "`"$srcDir`" `"$sqlBackupDir`" `"$fname`" /COPY:DAT /R:1 /W:1" `
    -Verb RunAs -Wait -PassThru
if ($p.ExitCode -ge 8) { throw "La copia con robocopy falló (código $($p.ExitCode))." }

# 3) Averiguar los nombres lógicos de los archivos dentro del .bak
Write-Host "Leyendo estructura del respaldo..."
$rows = sqlcmd -S $Server -E -C -h -1 -W -s "|" -Q `
    "SET NOCOUNT ON; RESTORE FILELISTONLY FROM DISK = N'$sqlBak';"

$logicalData = $null
$logicalLog  = $null
foreach ($line in $rows) {
    $cols = $line -split "\|"
    if ($cols.Count -ge 3) {
        $logical = $cols[0].Trim()
        $type    = $cols[2].Trim()   # 'D' = datos, 'L' = log
        if ($type -eq "D" -and -not $logicalData) { $logicalData = $logical }
        if ($type -eq "L" -and -not $logicalLog)  { $logicalLog  = $logical }
    }
}
if (-not $logicalData -or -not $logicalLog) {
    throw "No se pudieron leer los nombres lógicos del .bak."
}

# 4) Carpeta de datos por defecto de la instancia destino (para MOVE)
$dataDir = (sqlcmd -S $Server -E -C -h -1 -W -Q `
    "SET NOCOUNT ON; SELECT CAST(SERVERPROPERTY('InstanceDefaultDataPath') AS nvarchar(500));").Trim()
$mdf = Join-Path $dataDir "$Database.mdf"
$ldf = Join-Path $dataDir "$Database`_log.ldf"

# 5) Restaurar con REPLACE y MOVE (single_user para cerrar conexiones activas)
Write-Host "Restaurando base de datos..."
$restore = @"
IF DB_ID(N'$Database') IS NOT NULL
BEGIN
    ALTER DATABASE [$Database] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
END
RESTORE DATABASE [$Database] FROM DISK = N'$sqlBak'
WITH REPLACE, RECOVERY, STATS = 10,
     MOVE N'$logicalData' TO N'$mdf',
     MOVE N'$logicalLog'  TO N'$ldf';
ALTER DATABASE [$Database] SET MULTI_USER;
"@
sqlcmd -S $Server -E -C -Q $restore
if ($LASTEXITCODE -ne 0) { throw "El comando RESTORE falló (código $LASTEXITCODE)." }

Write-Host ""
Write-Host "Base de datos '$Database' restaurada correctamente." -ForegroundColor Green
