"""Catalogue de vérification (US-30) : un document qui inclut chaque fragment généré, pour vérifier qu'il compile
et pour que la personne qui rédige voie d'un coup tout le matériau disponible."""

from pathlib import Path

from .latex import echapper

ENTETE = r"""% Généré par importer_dossier : à compiler depuis la racine du rapport (latexmk -pdf catalogue.tex)
\documentclass[12pt,a4paper,oneside]{report}
\input{config/preambule}
\input{config/style}
\input{config/infos}
\begin{document}
"""
FIN = r"""\nocite{*}
\printbibliography
\end{document}
"""


def _figure(contenu, legende):
    return "\\begin{figure}[H]\\centering\n" + contenu + "\n\\caption{" + legende + "}\n\\end{figure}\n"


def _image(chemin, legende):
    return _figure(r"\includegraphics[width=0.6\linewidth]{" + chemin + "}", echapper(legende))


def ecrire_catalogue(dossier, donnees):
    dossier = Path(dossier)
    morceaux = [ENTETE]
    for figure in ("organigramme", "gantt"):
        if (dossier / "figures" / f"{figure}.tex").exists():
            morceaux.append(_figure(r"\input{figures/" + figure + "}", f"{figure.capitalize()} (généré)"))
    if (dossier / "tableaux").exists():
        for tableau in sorted((dossier / "tableaux").glob("*.tex")):
            morceaux.append(r"\input{tableaux/" + tableau.stem + "}" + "\n")
    for objet in donnees:
        champs = objet["fields"]
        if objet["model"] == "carnet.photo" and champs["destination"] in ("corps", "annexe"):
            morceaux.append(_image(f"img/fig_{champs['slug']}.jpg", champs["legende"]))
    if (dossier / "img").exists():
        for plan in sorted((dossier / "img").glob("plan_situation_*.png")):
            nom = plan.stem.removeprefix("plan_situation_")
            morceaux.append(_image(f"img/{plan.name}", f"Plan de situation : {nom}"))
    morceaux.append(FIN)
    sortie = dossier / "donnees_terrain" / "catalogue.tex"
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text("".join(morceaux), encoding="utf-8")
