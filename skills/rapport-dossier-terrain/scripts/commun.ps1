# Fonctions communes a preparer.ps1 et finaliser.ps1.

function Est-Depot([string]$chemin) {
    return (Test-Path (Join-Path $chemin 'webapp\manage.py')) -and (Test-Path (Join-Path $chemin 'tex_export_src\main.tex'))
}

# Racine du depot esr2ventisax : -Depot, sinon le dossier courant ou un parent, sinon l'emplacement habituel.
function Trouver-Depot([string]$depot) {
    if ($depot) {
        if (Est-Depot $depot) { return (Resolve-Path $depot).Path }
        Write-Host "Ce n'est pas le depot esr2ventisax (webapp/manage.py et tex_export_src/main.tex attendus) : $depot"; exit 2
    }
    $courant = (Get-Location).Path
    while ($courant) {
        if (Est-Depot $courant) { return $courant }
        $parent = Split-Path $courant -Parent
        if ($parent -eq $courant) { break }
        $courant = $parent
    }
    $defaut = Join-Path $HOME 'Desktop\sop_ai_coding\01_GREENFIELD\esr2ventisax'
    if (Est-Depot $defaut) { return $defaut }
    Write-Host 'Depot esr2ventisax introuvable : passer -Depot <chemin>.'; exit 2
}

# Liste les \AC{...} non commentes des .tex du rapport (hors donnees_terrain) et renvoie leur nombre.
function Lister-AC([string]$dossier) {
    $trouves = Get-ChildItem $dossier -Recurse -Filter '*.tex' |
        Where-Object { $_.FullName -notmatch '\\donnees_terrain\\' } |
        Select-String -Pattern '\\AC\{' -Encoding UTF8 |
        Where-Object { $_.Line -notmatch '^\s*%' }
    $n = @($trouves).Count
    Write-Host "Champs a completer (\AC) restants : $n"
    foreach ($t in $trouves) {
        $relatif = $t.Path.Substring($dossier.Length + 1)
        $texte = $t.Line.Trim()
        if ($texte.Length -gt 110) { $texte = $texte.Substring(0, 110) + '...' }
        Write-Host "  $($relatif):$($t.LineNumber)  $texte"
    }
    return $n
}
