"""Version Word (.docx) du rapport LaTeX, à côté du PDF (B22).

Usage (Python système, avec PyMuPDF et python-docx ; pandoc et pdflatex dans le PATH) :
    python outils/build_word.py <dossier du rapport> [<sortie.docx>]

Le rapport n'est jamais modifié : tout se fait dans une copie temporaire.
1. Chaque schéma TikZ (\\input{figures/...}) est compilé seul avec le préambule du rapport, recadré et
   inséré en PNG : pandoc ne sait pas dessiner TikZ.
2. Les bannières, intercalaires de parties et pages titrées deviennent des titres Word ; les tables des
   matières LaTeX sont remplacées par celle de Word.
3. pandoc convertit le LaTeX ; la bibliographie (citeproc) est placée sous « BIBLIOGRAPHIE », les légendes
   reçoivent « Figure N : » et « Tableau N : ».
4. Le modèle Word reprend le vert du rapport ; les « [À COMPLÉTER : …] » sont en orange.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERT = "2E7D32"
ORANGE = "E65100"
MARQUEUR_TDM = "MARQUEURTDMWORD"
CHAMP_TDM = (  # sommaire Word (champ TOC), mis à jour à l'ouverture du document
    '<w:sdt><w:sdtPr><w:docPartObj><w:docPartGallery w:val="Table of Contents"/><w:docPartUnique/>'
    '</w:docPartObj></w:sdtPr><w:sdtContent><w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
    r'<w:r><w:instrText xml:space="preserve"> TOC \o "1-2" \h \z \u </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Clic droit, « Mettre à jour les champs » '
    'pour afficher le sommaire.</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:sdtContent></w:sdt>')
IGNORES = shutil.ignore_patterns("*.aux", "*.log", "*.toc", "*.lof", "*.lot", "*.out", "*.bbl", "*.bcf", "*.blg",
                                 "*.fls", "*.fdb_latexmk", "*.run.xml", "*.synctex.gz", "*.pdf", "*.pptx",
                                 "*.docx", "donnees_terrain", "_build")
SURCHARGES = r"""
% --- Surcharges pour pandoc (version Word) : titres simples à la place des bannières TikZ ---
\renewcommand{\banniere}[1]{\chapter*{#1}}
\renewcommand{\pageTitre}[1]{\chapter*{#1}}
\renewcommand{\partie}[2]{\chapter*{#1 : #2}}
\renewcommand{\conclusionPartielle}{\paragraph{Conclusion partielle}}
\renewcommand{\tableofcontents}{}
\renewcommand{\listoftables}{}
\renewcommand{\listoffigures}{}
\renewcommand{\printbibliography}[1][]{}
"""


def lancer(cmd, cwd, **kw):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def rendre_figures(travail):
    """Compile chaque figure TikZ seule et la remplace par son PNG ; renvoie les noms rendus."""
    import fitz  # PyMuPDF

    sources = [p for d in ("liminaires", "parties", "annexes") for p in (travail / d).glob("*.tex")]
    noms = sorted({n for p in sources for n in re.findall(r"\\input\{figures/([\w-]+)\}", p.read_text("utf-8"))})
    (travail / "word").mkdir(exist_ok=True)
    rendues = []
    for nom in noms:
        doc = travail / f"_fig_{nom}.tex"
        doc.write_text(
            "\\documentclass[12pt,a4paper]{report}\n\\input{config/preambule}\n\\input{config/style}\n"
            "\\input{config/infos}\n\\pagestyle{empty}\n\\begin{document}\n\\thispagestyle{empty}\n"
            f"\\input{{figures/{nom}}}\n\\end{{document}}\n", encoding="utf-8")
        lancer(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", doc.name], travail)
        pdf = doc.with_suffix(".pdf")
        if not pdf.exists():
            print(f"  figure {nom} : compilation impossible, laissée de côté")
            continue
        page = fitz.open(pdf)[0]
        zones = [d["rect"] for d in page.get_drawings()] + [fitz.Rect(b[:4]) for b in page.get_text("blocks")]
        if not zones:
            continue
        cadre = zones[0]
        for z in zones[1:]:
            cadre |= z
        cadre = (cadre + (-6, -6, 6, 6)) & page.rect
        page.get_pixmap(clip=cadre, dpi=220).save(travail / "word" / f"{nom}.png")
        rendues.append(nom)
    for p in sources:
        texte = p.read_text("utf-8")
        for nom in rendues:
            texte = texte.replace(f"\\input{{figures/{nom}}}",
                                  f"\\includegraphics[width=0.95\\linewidth]{{word/{nom}.png}}")
        p.write_text(texte, encoding="utf-8")
    return rendues


def _spec_simple(spec):
    """Colonnes tabularx (X, Y personnalisée, >{...}) → colonnes l que pandoc comprend."""
    spec = re.sub(r">\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", "", spec)
    spec = re.sub(r"<\{[^{}]*\}", "", spec)
    spec = re.sub(r"[pmb]\{[^{}]*\}", "l", spec)
    return re.sub(r"[XYZ]", "l", spec)


def simplifier_pour_pandoc(texte):
    """tabularx → tabular ; figures à deux minipages → deux figures (sinon pandoc perd légendes et renvois)."""
    texte = re.sub(r"\\begin\{tabularx\}\{[^{}]*\}\{((?:[^{}]|\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})*)\}",
                   lambda m: "\\begin{tabular}{" + _spec_simple(m.group(1)) + "}", texte)
    texte = texte.replace("\\end{tabularx}", "\\end{tabular}")
    # pastille TikZ d'une ligne (« Session … » de la couverture) : pandoc perdrait le texte et garderait le « ; »
    texte = re.sub(r"\\tikz\s*\\node\[[^\]]*\]\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*;", r"\\textbf{\1}", texte)

    def eclater(m):
        corps = m.group(0)
        if "\\begin{minipage}" not in corps:
            return corps
        morceaux = re.findall(r"\\begin\{minipage\}(?:\[[^\]]*\])?\{[^{}]*\}(.*?)\\end\{minipage\}", corps, re.S)
        return "\n".join(f"\\begin{{figure}}[H]\\centering{m_}\\end{{figure}}" for m_ in morceaux)

    return re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", eclater, texte, flags=re.S)


def _inlines(texte):
    mots = texte.split(" ")
    sortie = []
    for i, mot in enumerate(mots):
        if i:
            sortie.append({"t": "Space"})
        sortie.append({"t": "Str", "c": mot})
    return sortie


def _prefixer(legende, prefixe):
    blocs = legende[1]
    if blocs and blocs[0]["t"] in ("Plain", "Para"):
        contenu = blocs[0]["c"]
        if contenu and contenu[0].get("t") == "Str":  # « organigramme… » → « Organigramme… »
            contenu[0]["c"] = contenu[0]["c"][:1].upper() + contenu[0]["c"][1:]
        blocs[0]["c"] = _inlines(prefixe) + [{"t": "Space"}] + contenu
    else:
        blocs.insert(0, {"t": "Plain", "c": _inlines(prefixe)})


def retoucher(ast):
    """Numérote les légendes et place la bibliographie sous son titre."""
    compteurs = {"Figure": 0, "Table": 0}

    def parcourir(blocs):
        sortie = []
        for b in blocs:
            t = b.get("t")
            if t == "Figure":
                if b["c"][1][1]:  # seules les figures légendées sont numérotées, comme dans le PDF
                    compteurs["Figure"] += 1
                    _prefixer(b["c"][1], f"Figure {compteurs['Figure']} :")
                b["c"][2] = parcourir(b["c"][2])
            elif t == "Table" and b["c"][1][1]:  # les tableaux de mise en page (couverture) n'ont pas de légende
                compteurs["Table"] += 1
                _prefixer(b["c"][1], f"Tableau {compteurs['Table']} :")
            elif t in ("Div", "BlockQuote"):
                idx = 1 if t == "Div" else 0
                b["c"][idx] = parcourir(b["c"][idx])
            if t == "Para" and _texte(b["c"]).strip() == MARQUEUR_TDM:  # sommaire à sa place, après la couverture
                sortie.append({"t": "RawBlock", "c": ["openxml", CHAMP_TDM]})
                continue
            sortie.append(b)
            if t == "Header" and "BIBLIOGRAPHIE" in json.dumps(b["c"][2], ensure_ascii=False).upper():
                sortie.append({"t": "Div", "c": [["refs", [], []], []]})
        return sortie

    ast["blocks"] = parcourir(ast["blocks"])
    resoudre_renvois(ast)
    return compteurs


def _texte(inlines):
    morceaux = []
    for i in inlines:
        if i.get("t") == "Str":
            morceaux.append(i["c"])
        elif i.get("t") in ("Space", "SoftBreak"):
            morceaux.append(" ")
        elif isinstance(i.get("c"), list):
            morceaux.append(_texte([x for x in i["c"] if isinstance(x, dict)] or
                                   [y for x in i["c"] if isinstance(x, list) for y in x if isinstance(y, dict)]))
    return "".join(morceaux)


def resoudre_renvois(ast):
    """\\ref{fig:x} → numéro de la figure (ou du tableau) ; \\ref{sec:x} → titre de la section visée."""
    cibles, compte = {}, {"Figure": 0, "Table": 0}

    def collecter(noeud):
        if isinstance(noeud, dict):
            t = noeud.get("t")
            if t in compte and noeud["c"][1][1]:
                compte[t] += 1
                ident = noeud["c"][0][0]
                if ident:
                    cibles[ident] = str(compte[t])
            elif t == "Header" and noeud["c"][1][0]:
                cibles.setdefault(noeud["c"][1][0], "« " + _texte(noeud["c"][2]) + " »")
            for v in noeud.values():
                collecter(v)
        elif isinstance(noeud, list):
            for v in noeud:
                collecter(v)

    def remplacer(noeud):
        if isinstance(noeud, dict):
            if noeud.get("t") == "Link":
                attributs = dict(noeud["c"][0][2])
                cle = attributs.get("reference")
                if attributs.get("reference-type", "").startswith("ref"):
                    if cle in cibles:
                        noeud["c"][1] = [{"t": "Str", "c": cibles[cle]}]
                    else:  # tableau numéroté par pandoc « 0.N » (chapitres non numérotés) → « N »
                        contenu = _texte(noeud["c"][1])
                        m = re.fullmatch(r"0\.(\d+)", contenu)
                        if m:
                            noeud["c"][1] = [{"t": "Str", "c": m.group(1)}]
            for v in noeud.values():
                remplacer(v)
        elif isinstance(noeud, list):
            for v in noeud:
                remplacer(v)

    collecter(ast["blocks"])
    remplacer(ast["blocks"])


def modele_word(chemin):
    """Modèle pandoc retouché : police sans empattement, titres verts, comme le PDF."""
    from docx import Document
    from docx.shared import Pt, RGBColor

    subprocess.run(["pandoc", "-o", str(chemin), "--print-default-data-file", "reference.docx"], check=True)
    doc = Document(chemin)
    for nom in ("Normal", "Body Text", "First Paragraph", "Compact"):
        if nom in [s.name for s in doc.styles]:
            doc.styles[nom].font.name = "Arial"
            doc.styles[nom].font.size = Pt(11)
    for nom, taille in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 12), ("Title", 22)):
        if nom in [s.name for s in doc.styles]:
            police = doc.styles[nom].font
            police.name, police.size, police.bold = "Arial", Pt(taille), True
            police.color.rgb = RGBColor.from_string(VERT)
    doc.save(chemin)


def colorer_a_completer(chemin):
    from docx import Document
    from docx.shared import RGBColor

    doc = Document(chemin)
    paragraphes = list(doc.paragraphs) + [p for t in doc.tables for r in t.rows for c in r.cells for p in c.paragraphs]
    n = 0
    for p in paragraphes:
        for run in p.runs:
            if "COMPLÉTER" in run.text:
                run.font.color.rgb = RGBColor.from_string(ORANGE)
                n += 1
    doc.core_properties.title = "Rapport de stage"
    doc.save(chemin)
    return n


def construire(dossier, sortie):
    dossier, sortie = Path(dossier).resolve(), Path(sortie).resolve()
    with tempfile.TemporaryDirectory(prefix="rapport_word_") as tmp:
        travail = Path(tmp) / "rapport"
        shutil.copytree(dossier, travail, ignore=IGNORES)
        figures = rendre_figures(travail)
        for p in [p for d in ("liminaires", "parties", "annexes", "tableaux") for p in (travail / d).glob("*.tex")]:
            p.write_text(simplifier_pour_pandoc(p.read_text("utf-8")), encoding="utf-8")
        (travail / "word_surcharges.tex").write_text(SURCHARGES, encoding="utf-8")
        main = travail / "main.tex"
        texte = main.read_text("utf-8").replace("\\input{config/infos}",
                                                "\\input{config/infos}\n\\input{word_surcharges}", 1)
        # le premier \tableofcontents (SOMMAIRE) devient le champ Word ; le second (fin du PDF) disparaît
        texte = texte.replace("\\tableofcontents", f"\\chapter*{{SOMMAIRE}}\n\n{MARQUEUR_TDM}\n\n", 1)
        main.write_text(texte, encoding="utf-8")
        brut = lancer(["pandoc", "main.tex", "-f", "latex", "-t", "json"], travail)
        if brut.returncode:
            sys.exit(f"pandoc (lecture du LaTeX) a échoué :\n{brut.stderr}")
        ast = json.loads(brut.stdout)
        compteurs = retoucher(ast)
        (travail / "rapport.json").write_text(json.dumps(ast, ensure_ascii=False), encoding="utf-8")
        modele_word(travail / "modele.docx")
        cmd = ["pandoc", "rapport.json", "-f", "json", "-t", "docx", "-o", str(sortie),
               "--reference-doc", "modele.docx", "--resource-path", ".", "-M", "lang=fr-FR"]
        if (travail / "bib" / "references.bib").exists():
            cmd += ["--citeproc", "--bibliography", "bib/references.bib"]
        conv = lancer(cmd, travail)
        if conv.returncode:
            sys.exit(f"pandoc (écriture du Word) a échoué :\n{conv.stderr}")
    oranges = colorer_a_completer(sortie)
    print(f"Word : {sortie}")
    print(f"  schémas TikZ rendus : {len(figures)} ({', '.join(figures)})")
    print(f"  figures : {compteurs['Figure']} ; tableaux : {compteurs['Table']} ; « À COMPLÉTER » : {oranges}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dossier = Path(sys.argv[1])
    construire(dossier, sys.argv[2] if len(sys.argv) > 2 else dossier / "rapport.docx")
