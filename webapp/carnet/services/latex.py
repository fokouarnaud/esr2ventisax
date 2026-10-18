"""Échappement LaTeX et conversion du Markdown minimal (A34) : paragraphes, listes « - » / « 1. », **gras**."""

import re

_SPECIAUX = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_PUCE = re.compile(r"^\s*[-*]\s+(.*)$")
_NUMERO = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_GRAS = re.compile(r"\*\*(.+?)\*\*")


def echapper(texte):
    if texte is None:
        return ""
    return "".join(_SPECIAUX.get(c, c) for c in str(texte))


def _en_ligne(texte):
    return _GRAS.sub(r"\\textbf{\1}", echapper(texte))


def markdown_vers_latex(texte):
    lignes = (texte or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocs, paragraphe, liste, env = [], [], [], None

    def fermer_paragraphe():
        if paragraphe:
            blocs.append("\n".join(paragraphe))
            paragraphe.clear()

    def fermer_liste():
        nonlocal env
        if liste:
            items = "\n".join(f"  \\item {i}" for i in liste)
            blocs.append(f"\\begin{{{env}}}\n{items}\n\\end{{{env}}}")
            liste.clear()
        env = None

    for ligne in lignes:
        puce, numero = _PUCE.match(ligne), _NUMERO.match(ligne)
        if puce or numero:
            fermer_paragraphe()
            voulu = "itemize" if puce else "enumerate"
            if env and env != voulu:
                fermer_liste()
            env = voulu
            liste.append(_en_ligne((puce or numero).group(1).strip()))
        elif not ligne.strip():
            fermer_paragraphe()
            fermer_liste()
        else:
            fermer_liste()
            paragraphe.append(_en_ligne(ligne.strip()))
    fermer_paragraphe()
    fermer_liste()
    return "\n\n".join(blocs)
