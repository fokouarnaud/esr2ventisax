# Etapes 1 et 2 : importe un zip "dossier terrain" du Carnet de stage, puis controle les fragments generes.
# Usage : preparer.ps1 -Zip <dossier-terrain-....zip> [-Depot <racine esr2ventisax>] [-Force] [-SansCarte]
# Derniere ligne de sortie : DOSSIER=<chemin du rapport>  (a reutiliser pour la redaction et finaliser.ps1)
param(
    [Parameter(Mandatory = $true)][string]$Zip,
    [string]$Depot = '',
    [switch]$Force,
    [switch]$SansCarte
)
$ErrorActionPreference = 'Continue'  # les codes de retour sont verifies a la main (stderr de latexmk n'est pas une erreur)
$env:PYTHONIOENCODING = 'utf-8'
. (Join-Path $PSScriptRoot 'commun.ps1')

$Depot = Trouver-Depot $Depot
$Zip = (Resolve-Path $Zip).Path
$python = Join-Path $Depot 'webapp\.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host "venv introuvable : $python. Installer l'application (README, Installation locale)."; exit 2
}

# Nom du dossier cree par importer_dossier : <slug>-<uuid8>, lu dans manifest.json
$nom = & $python -c "import json,sys,zipfile; m=json.loads(zipfile.ZipFile(sys.argv[1]).read('manifest.json')); print(m['slug']+'-'+m['stage'][:8])" $Zip
if ($LASTEXITCODE -ne 0) { Write-Host "Zip illisible ou sans manifest.json : $Zip"; exit 2 }
$dossier = Join-Path $Depot "rapports\$nom"

if ((Test-Path $dossier) -and -not $Force) {
    Write-Host "Le rapport existe deja : $dossier"
    Write-Host "Il contient peut-etre des textes rediges. Relancer avec -Force pour l'ecraser (accord de l'utilisateur requis)."
    Write-Host "DOSSIER=$dossier"
    exit 3
}

Write-Host "== 1. Import ($nom)"
$options = @('importer_dossier', $Zip)
if ($Force) { $options += '--force' }
if ($SansCarte) { $options += '--sans-carte' }
& $python (Join-Path $Depot 'webapp\manage.py') @options | Out-Host
if ($LASTEXITCODE -ne 0) { Write-Host 'Import en echec (voir le message ci-dessus).'; exit 1 }

Write-Host '== 2. Controle des fragments (catalogue.tex)'
Push-Location $dossier
try {
    & latexmk -pdf -interaction=nonstopmode -halt-on-error 'donnees_terrain/catalogue.tex' *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'catalogue.tex ne compile pas : erreurs ci-dessous.'
        Select-String -Path 'catalogue.log' -Pattern '^!' -Context 0, 3 | Select-Object -First 5 | Out-Host
        exit 1
    }
    Write-Host "OK : catalogue.pdf ($dossier\catalogue.pdf)"
}
finally { Pop-Location }

$null = Lister-AC $dossier
$plans = @(Get-ChildItem (Join-Path $dossier 'img') -Filter 'plan_situation_*.png' -ErrorAction SilentlyContinue)
Write-Host "Plans de situation : $($plans.Count) ; photos importees : $(@(Get-ChildItem (Join-Path $dossier 'img') -Filter 'fig_*.jpg').Count)"
Write-Host "DOSSIER=$dossier"
