# Genera el Business Model Canvas corregido como PNG (coordenadas nativas, Y hacia abajo)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$W = 1500
$H = 900
$outPng = "C:\Users\RYZEN\Documents\Github\sistema_experto_tesis_bkp\V.0.1\docs\canvas_business_model_actualizado.png"

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

function C([int]$r,[int]$gr,[int]$b){ return [System.Drawing.Color]::FromArgb($r,$gr,$b) }

$paper   = C 252 250 245
$navy    = C 16 42 71
$gold    = C 191 145 30
$grayTxt = C 98 98 98
$purple  = C 239 229 242; $purpleL = C 128 101 143
$aqua    = C 223 244 241; $aquaL   = C 25 165 160
$blue    = C 229 239 250; $blueL   = C 59 127 181
$yellow  = C 255 242 200; $yellowL = C 237 189 54
$pink    = C 252 228 225; $pinkL   = C 240 109 98
$teal    = C 224 243 239; $tealL   = C 40 167 159
$red     = C 252 233 228; $redL    = C 238 112 95

$g.FillRectangle((New-Object System.Drawing.SolidBrush($paper)), 0, 0, $W, $H)

$family = "Segoe UI"
function Font([single]$size,[int]$style=0){ return New-Object System.Drawing.Font($family, $size, [System.Drawing.FontStyle]$style, [System.Drawing.GraphicsUnit]::Pixel) }

function DrawTextLeft([string]$t,[single]$x,[single]$y,[System.Drawing.Font]$f,[System.Drawing.Color]$col){
    $brush = New-Object System.Drawing.SolidBrush($col)
    $g.DrawString($t, $f, $brush, $x, $y)
    $brush.Dispose()
}

# Dibuja un bloque: titulo centrado arriba + cuerpo alineado a la izquierda con wrap
function Block([single]$x,[single]$y,[single]$w,[single]$h,[string]$title,[string]$body,[System.Drawing.Color]$fill,[System.Drawing.Color]$stroke,[single]$bodySize){
    $g.FillRectangle((New-Object System.Drawing.SolidBrush($fill)), $x, $y, $w, $h)
    $pen = New-Object System.Drawing.Pen($stroke, 1.4)
    $g.DrawRectangle($pen, $x, $y, $w, $h)
    $pen.Dispose()

    # Titulo
    $tf = Font 15 1
    $fmtC = New-Object System.Drawing.StringFormat
    $fmtC.Alignment = [System.Drawing.StringAlignment]::Center
    $trect = New-Object System.Drawing.RectangleF($x, ($y+8), $w, 26)
    $tb = New-Object System.Drawing.SolidBrush($navy)
    $g.DrawString($title, $tf, $tb, $trect, $fmtC)

    # Linea bajo titulo
    $g.DrawLine((New-Object System.Drawing.Pen($stroke, 0.8)), ($x+10), ($y+34), ($x+$w-10), ($y+34))

    # Cuerpo (izquierda, con wrap)
    $bf = Font $bodySize 0
    $pad = 10
    $brect = New-Object System.Drawing.RectangleF(($x+$pad), ($y+40), ($w-2*$pad), ($h-46))
    $fmtL = New-Object System.Drawing.StringFormat
    $fmtL.Alignment = [System.Drawing.StringAlignment]::Near
    $g.DrawString($body, $bf, $tb, $brect, $fmtL)
    $tb.Dispose()
}

# ===== Cabecera =====
DrawTextLeft "Business Model Canvas: mapa visual del modelo" 40 24 (Font 30 1) $navy
DrawTextLeft "El Canvas representa la logica del negocio del sistema experto web de scoring. Elaboracion propia." 40 64 (Font 13 0) $grayTxt
$g.DrawLine((New-Object System.Drawing.Pen($gold,2.0)), 40, 90, 1460, 90)

# ===== Grilla superior =====
# Fila principal entre y=110 y y=560
$topY = 110
$rowH = 450
$col1 = 40;   $w1 = 240   # Socios clave
$col2 = 292;  $w2 = 300   # Actividades (arriba) + Recursos (abajo)
$col3 = 604;  $w3 = 250   # Propuesta de valor
$col4 = 866;  $w4 = 250   # Relacion (arriba) + Canales (abajo)
$col5 = 1128; $w5 = 332   # Segmentos

Block $col1 $topY $w1 $rowH "Socios clave" "No se definen alianzas comerciales ni socios estrategicos.`n`nProveedores de tecnologia e infraestructura (recursos necesarios, no socios):`n  - OnRender: alojamiento.`n  - GitHub: repositorio y versiones.`n  - Pagopar: pasarela de pagos.`n`nONU / OFAC: fuentes externas de informacion, no socios comerciales." $purple $purpleL 13

$h2a = 230; $h2b = $rowH - $h2a - 12
Block $col2 $topY $w2 $h2a "Actividades clave" "Desarrollo y mantenimiento del sistema web de scoring.`nConfiguracion y actualizacion de criterios y reglas IF-THEN parametrizadas.`nProcesamiento de evaluaciones y generacion de reportes.`nValidacion funcional y actualizacion de reglas.`nSoporte de la plataforma." $aqua $aquaL 12.5
Block $col2 ($topY+$h2a+12) $w2 $h2b "Recursos clave" "Plataforma web React/Flask y base de datos PostgreSQL.`nMotor de reglas, criterios y conocimiento del dominio.`nReglas IF-THEN validadas en el proyecto.`nInfraestructura de alojamiento, seguridad y respaldos." $blue $blueL 12.5

Block $col3 $topY $w3 $rowH "Propuesta de valor" "Evaluacion automatizada del riesgo comercial.`n`nScoring con variables como ingresos, historial de pagos, endeudamiento y comportamiento financiero.`n`nSistema experto de reglas IF-THEN y ponderaciones; clasifica en Alto, Medio o Bajo. No es un modelo estadistico predictivo.`n`nCotejo contra listas de sanciones (ONU/OFAC): una coincidencia fuerza riesgo alto.`n`nReportes para apoyar la decision humana.`n`nObjetivo: reducir el tiempo de evaluacion respecto del proceso manual (sujeto a validacion)." $yellow $yellowL 12.5

$h4a = 230; $h4b = $rowH - $h4a - 12
Block $col4 $topY $w4 $h4a "Relacion con clientes" "Soporte tecnico y asistencia durante el uso.`nOrientacion inicial para la adopcion de la plataforma.`nCapacitacion basica a usuarios autorizados.`nMantenimiento y actualizaciones.`nComunicacion digital." $pink $pinkL 12.5
Block $col4 ($topY+$h4a+12) $w4 $h4b "Canales" "Plataforma web.`nContacto comercial directo con inmobiliarias.`nDemostracion del sistema.`nCanales digitales de soporte y comunicacion." $blue $blueL 12.5

Block $col5 $topY $w5 $rowH "Segmentos de clientes" "Cliente y pagador: inmobiliarias de Asuncion.`n`nUsuarios: administradores, responsables de evaluacion y otros usuarios autorizados dentro de la inmobiliaria.`n`nNecesidad: agilizar y estandarizar el analisis de clientes y apoyar las decisiones de riesgo." $teal $tealL 13

# ===== Banda inferior =====
$botY = $topY + $rowH + 15
$botH = 300
$cwL = 700
Block 40 $botY $cwL $botH "Costos" "Inversion inicial (unica): desarrollo ~Gs. 9.532.200 (RRHH 500 h, hardware y licencias). Costo ya ejecutado en el proyecto.`n`nCostos recurrentes (operacion mensual):`n  - Hosting backend (Render Starter): Gs. 51.100`n  - Base de datos PostgreSQL (Render): Gs. 51.100`n  - Frontend (Render, Free): Gs. 0`n  - Dominio (prorrateado): ~Gs. 7.300`n  - Mantenimiento del motor de scoring: ~Gs. 40.000`n  - Soporte tecnico, seguridad y respaldos: ~Gs. 30.000`n  Subtotal fijo: ~Gs. 179.600/mes (~Gs. 2.154.000/ano).`n`nCosto variable: comision de la pasarela (Pagopar) por transaccion, proporcional a las ventas." $red $redL 12.5

Block (40+$cwL+20) $botY (1460-(40+$cwL+20)) $botH "Ingresos / sostenimiento" "Quien paga: la inmobiliaria.`n`nQue paga: suscripcion mensual por planes, con facturacion por periodo (reportes incluidos).`n`n  Bronce: 15 reportes - Gs. 150.000 /mes`n  Plata: 30 reportes - Gs. 270.000 /mes`n  Oro: 50 reportes - Gs. 400.000 /mes`n`nLos reportes que superan el cupo del periodo se facturan como evaluaciones adicionales (excedentes).`n`nLos ingresos por suscripcion y excedentes sostienen infraestructura, mantenimiento, seguridad y soporte." $yellow $yellowL 12.5

$g.Dispose()
$bmp.Save($outPng, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output ("PNG_OK -> " + $outPng)
