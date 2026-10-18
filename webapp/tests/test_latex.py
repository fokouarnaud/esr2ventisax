"""A18, A34 : échappement LaTeX et Markdown minimal → LaTeX (attendus écrits à la main)."""

import pytest

from carnet.services.latex import echapper, markdown_vers_latex


@pytest.mark.parametrize("brut,attendu", [
    ("R&D", r"R\&D"),
    ("50 %", r"50 \%"),
    ("10 $", r"10 \$"),
    ("n° #3", r"n° \#3"),
    ("fig_1", r"fig\_1"),
    ("{x}", r"\{x\}"),
    ("~", r"\textasciitilde{}"),
    ("x^2", r"x\textasciicircum{}2"),
    ("C:\\tmp", r"C:\textbackslash{}tmp"),
    ("Ø 16 mm — é", "Ø 16 mm — é"),
])
def test_echapper(brut, attendu):
    assert echapper(brut) == attendu


def test_echapper_none_donne_chaine_vide():
    assert echapper(None) == ""


def test_markdown_paragraphes():
    assert markdown_vers_latex("Un.\n\nDeux.") == "Un.\n\nDeux."


def test_markdown_gras_et_echappement():
    assert markdown_vers_latex("**Attention** : 50 % & plus") == r"\textbf{Attention} : 50 \% \& plus"


def test_markdown_liste_a_puces():
    attendu = "Matériel :\n\n\\begin{itemize}\n  \\item tube PER\n  \\item raccord\n\\end{itemize}"
    assert markdown_vers_latex("Matériel :\n- tube PER\n- raccord") == attendu


def test_markdown_liste_numerotee():
    attendu = "\\begin{enumerate}\n  \\item couper\n  \\item ébavurer\n\\end{enumerate}"
    assert markdown_vers_latex("1. couper\n2. ébavurer") == attendu


def test_markdown_liste_puis_paragraphe():
    attendu = "\\begin{itemize}\n  \\item a\n\\end{itemize}\n\nFin."
    assert markdown_vers_latex("- a\n\nFin.") == attendu


def test_markdown_vide():
    assert markdown_vers_latex("  \n ") == ""


def test_markdown_retours_windows():
    assert markdown_vers_latex("Un.\r\n\r\nDeux.") == "Un.\n\nDeux."


def test_asterisque_isolee_conservee():
    assert markdown_vers_latex("note * importante") == "note * importante"
