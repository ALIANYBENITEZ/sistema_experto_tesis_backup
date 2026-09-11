<#
============================================================
  backup_db.ps1
  Genera un respaldo completo (.bak) de la base de datos
  y lo copia a la carpeta 'backups/' del proyecto.

  Uso (clic derecho > "Ejecutar con PowerShell", o desde una terminal):
      .\backend\scripts\backup_db.ps1
      .\backend\scripts\backup_db.ps1 -Server "MI-PC\SQLEXPRESS" -Database "inmobiliaria_db"

  Nota: el .bak contiene datos personales, por eso la carpeta
  'backups/' está en .gitignore y NUNCA se sube a GitHub.
============================================================
#>
param(
    [string]$Server   = "DESKTOP-8242966\SQLEXPRESS",
    [string]$Database = "inmobiliaria_db"
)

$ErrorActionPreference = "Stop"

# Raíz del proyecto = dos niveles arriba de este script (backend\scripts\..\..)
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$backupsDir  = Join-Path $projectRoot "backups"
New-Item -ItemType Directory -Path $backupsDir -Force | Out-Null

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$fname = "${Database}_$stamp.bak"

Write-Host "Base de datos : $Database"
Write-Host "Servidor      : $Server"

# 1) Ubicar la carpeta de backups por defecto de la instancia (SQL Server tiene
#    permisos de escritura ahí; en Documentos suele dar 'Acceso denegado').
$sqlBackupDir = (sqlcmd -S $Server -E -C -h -1 -W -Q `
    "SET NOCOUNT ON; SELECT CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS nvarchar(500));").Trim()

if (-not $sqlBackupDir) {
    throw "No se pudo determinar la carpeta de backups de SQL Server. Verifique la conexión."
}
$sqlBak = Join-Path $sqlBackupDir $fname

# 2) Ejecutar el backup (sin COMPRESSION: no soportado en Express Edition)
Write-Host "Generando respaldo..."
$q = "BACKUP DATABASE [$Database] TO DISK = N'$sqlBak' WITH INIT, STATS = 10, NAME = N'$Database full backup';"
sqlcmd -S $Server -E -C -Q $q
if ($LASTEXITCODE -ne 0) { throw "El comando BACKUP falló (código $LASTEXITCODE)." }

# 3) Copiar el .bak a la carpeta backups/ del proyecto.
#    Program Files requiere elevación: se usa robocopy con UAC.
Write-Host "Copiando el respaldo a: $backupsDir (acepte el aviso de administrador si aparece)"
$p = Start-Process -FilePath "robocopy.exe" `
    -ArgumentList "`"$sqlBackupDir`" `"$backupsDir`" `"$fname`" /COPY:DAT /R:1 /W:1" `
    -Verb RunAs -Wait -PassThru

# robocopy: códigos 0-7 son éxito; >=8 es error
if ($p.ExitCode -ge 8) { throw "La copia con robocopy falló (código $($p.ExitCode))." }

$destino = Join-Path $backupsDir $fname
if (Test-Path $destino) {
    $mb = [math]::Round((Get-Item $destino).Length / 1MB, 2)
    Write-Host ""
    Write-Host "Respaldo creado correctamente:" -ForegroundColor Green
    Write-Host "   $destino  ($mb MB)"
    Write-Host ""
    Write-Host "Recomendacion: copie este archivo a un disco externo o nube privada." -ForegroundColor Yellow
} else {
    throw "No se encontró el archivo copiado en $destino."
}
