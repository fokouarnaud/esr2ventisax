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

if (-not $SansPresentation) {
    Write-Host '== 5. Presentation'
    # Le venv de l'application n'a pas PyMuPDF : on cherche un Python qui a fitz et pptx
    $py = $null
    foreach ($candidat in 'python', 'py', 'python3') {
        if (Get-Command $candidat -ErrorAction SilentlyContinue) {
            & $candidat -c 'import fitz, pptx' 2>$null
            if ($LASTEXITCODE -eq 0) { $py = $candidat; break }
        }
    }
    if (-not $py) {
        Write-Host 'Aucun Python avec PyMuPDF et python-pptx : python -m pip install python-pptx PyMuPDF'; exit 2
    }
    $pptx = Join-Path $Dossier 'presentation.pptx'
    & $py (Join-Path $Depot 'tex_export_src\outils\build_presentation.py') $Dossier $pptx | Out-Host
    if ($LASTEXITCODE -ne 0) { Write-Host 'Generation de la presentation en echec.'; exit 1 }
}

Write-Host '== Bilan'
Write-Host "PDF          : $Dossier\main.pdf"
if (-not $SansPresentation) { Write-Host "Presentation : $Dossier\presentation.pptx" }
Write-Host "\AC restants : $restants"
if ($restants -gt 0) { exit 4 }
