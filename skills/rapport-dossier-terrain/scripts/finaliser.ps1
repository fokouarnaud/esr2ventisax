# Etapes 4 et 5 : compile le rapport redige en PDF, puis genere la presentation de soutenance.
# Usage : finaliser.ps1 -Dossier <rapports\slug-uuid8> [-Depot <racine esr2ventisax>] [-SansPresentation]
param(
    [Parameter(Mandatory = $true)][string]$Dossier,
    [string]$Depot = '',
    [switch]$SansPresentation
)
$ErrorActionPreference = 'Continue'  # les codes de retour sont verifies a la main (stderr de latexmk n'est pas une erreur)
$env:PYTHONIOENCODING = 'utf-8'
. (Join-Path $PSScriptRoot 'commun.ps1')

$Depot = Trouver-Depot $Depot
$Dossier = (Resolve-Path $Dossier).Path
$compile = Join-Path $HOME '.claude\skills\latex-pdf-soutenance\scripts\compile-latex.ps1'
if (-not (Test-Path $compile)) { Write-Host "Skill latex-pdf-soutenance introuvable : $compile"; exit 2 }

Write-Host '== 4. Compilation du rapport'
$sortie = & powershell -ExecutionPolicy Bypass -File $compile -Dir $Dossier 2>&1
$sortie | Select-Object -Last 12 | Out-Host
if (-not ($sortie -match '^OK : aucune erreur')) {
    Write-Host "Compilation en echec ou references indefinies : lire $Dossier\main.log"; exit 1
}
$restants = Lister-AC $Dossier

function Trouver-Python([string]$modules) {
    # Essaie chaque Python du PATH, pas seulement le premier : le venv de l'application (souvent active)
    # n'a ni PyMuPDF, ni python-pptx, ni python-docx.
    $chemins = Get-Command python, py, python3 -All -ErrorAction SilentlyContinue | ForEach-Object Source |
        Select-Object -Unique
    foreach ($candidat in $chemins) {
        & $candidat -c "import $modules" 2>$null
        if ($LASTEXITCODE -eq 0) { return $candidat }
    }
    return $null
}

if (-not $SansPresentation) {
    Write-Host '== 5. Presentation'
    $py = Trouver-Python 'fitz, pptx'
    if (-not $py) {
        Write-Host 'Aucun Python avec PyMuPDF et python-pptx : python -m pip install python-pptx PyMuPDF'; exit 2
    }
    $pptx = Join-Path $Dossier 'presentation.pptx'
    & $py (Join-Path $Depot 'tex_export_src\outils\build_presentation.py') $Dossier $pptx | Out-Host
    if ($LASTEXITCODE -ne 0) { Write-Host 'Generation de la presentation en echec.'; exit 1 }
}

Write-Host '== 6. Version Word'
$word = Join-Path $Dossier 'rapport.docx'
$pyWord = Trouver-Python 'fitz, docx'
if (-not (Get-Command pandoc -ErrorAction SilentlyContinue)) {
    Write-Host 'pandoc introuvable : https://pandoc.org/installing.html (version Word non produite)'; exit 2
}
if (-not $pyWord) { Write-Host 'Aucun Python avec PyMuPDF et python-docx : python -m pip install python-docx PyMuPDF'; exit 2 }
$outil = Join-Path $Dossier 'outils\build_word.py'
if (-not (Test-Path $outil)) { $outil = Join-Path $Depot 'tex_export_src\outils\build_word.py' }
& $pyWord $outil $Dossier $word | Out-Host
if ($LASTEXITCODE -ne 0) { Write-Host 'Generation de la version Word en echec.'; exit 1 }

Write-Host '== Bilan'
Write-Host "PDF          : $Dossier\main.pdf"
Write-Host "Word         : $word"
if (-not $SansPresentation) { Write-Host "Presentation : $Dossier\presentation.pptx" }
Write-Host "\AC restants : $restants"
if ($restants -gt 0) { exit 4 }
