# Inserta el PNG del Canvas en un documento Word nuevo
$ErrorActionPreference = 'Stop'
$png = "C:\Users\RYZEN\Documents\Github\sistema_experto_tesis_bkp\V.0.1\docs\canvas_business_model_actualizado.png"
$outDocx = "C:\Users\RYZEN\Documents\TESIS 2026_DOCUMENTOS\TESIS 2026 ALIANY\Canvas_Actualizado_para_pegar.docx"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()
$sel = $word.Selection

# Titulo
$sel.ParagraphFormat.Alignment = 1
$sel.Font.Bold = $true
$sel.Font.Size = 14
$sel.TypeText("Business Model Canvas actualizado (corregido)")
$sel.TypeParagraph()
$sel.Font.Bold = $false
$sel.Font.Size = 10
$sel.TypeText("Selecciona la imagen de abajo, copiala (Ctrl+C) y pegala en tu tesis reemplazando la Ilustracion 26.")
$sel.TypeParagraph()
$sel.TypeParagraph()

# Pagina horizontal para que entre mejor
$doc.PageSetup.Orientation = 1  # wdOrientLandscape

# Insertar imagen
$sel.ParagraphFormat.Alignment = 1
$img = $sel.InlineShapes.AddPicture($png)
# Ajustar ancho a ~24 cm
$img.LockAspectRatio = -1
$img.Width = 680  # puntos (~24 cm)

$sel.TypeParagraph()
$sel.TypeParagraph()
$sel.Font.Italic = $true
$sel.Font.Size = 10
$sel.ParagraphFormat.Alignment = 0
$sel.TypeText("Nota: Business Model Canvas con los nueve bloques del modelo de negocio del sistema. Elaboracion propia.")

$doc.SaveAs([ref]$outDocx, [ref]16)
$doc.Close()
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($sel) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Output ("DOCX_OK -> " + $outDocx)
