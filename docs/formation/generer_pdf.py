"""Génère les PDF des supports de formation (A4) à partir des pages HTML de ce dossier.

Usage (Python système, avec Playwright et Pillow) :  python docs/formation/generer_pdf.py [samedi-01 ...]
Sans argument, tous les fichiers samedi-*.html sont convertis.
"""

import io
import re
import shutil
import sys
from pathlib import Path

import fitz  # PyMuPDF : couverture de la fiche pour l'accueil

from PIL import Image
from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent
MANUEL = ICI.parent / "manuel" / "img"
PUBLICATION = ICI.parents[1] / "webapp" / "carnet" / "static" / "carnet" / "formation"  # accueil public (A40)
# Captures recadrées sur la zone utile : nom -> (source, boîte gauche, haut, droite, bas)
RECADRAGES = {
    "connexion": (MANUEL / "01_connexion.jpg", (440, 230, 1000, 640)),
    "creer_stage": (MANUEL / "21_creer_stage.jpg", (0, 70, 940, 470)),
    "jours_travailles": (ICI / "img" / "onglet_suivi.jpg", (0, 296, 640, 480)),
    "rapport_activite": (MANUEL / "08b_note_rapport_activite.jpg", (0, 70, 1160, 640)),
    # samedi 2
    "refus_source": (ICI / "img" / "refus_sans_source.jpg", (0, 380, 1000, 700)),
    "equipement": (ICI / "img" / "equipement_ajout.jpg", (0, 60, 960, 440)),
    "tableau_vide": (MANUEL / "22_premier_jour_tableau.jpg", (0, 70, 1280, 420)),
    "couverture": (MANUEL / "03b_stage_couverture.jpg", (0, 60, 940, 520)),
    # samedi 3
    "chapitre": (ICI / "img" / "rubrique_ajout.jpg", (0, 80, 700, 440)),
    "photo_legende": (ICI / "img" / "photo_fiche.jpg", (0, 70, 960, 300)),
    "etiquettes_note": (MANUEL / "08c_note_intervention.jpg", (0, 130, 1280, 520)),
    # samedi 4
    "absence": (ICI / "img" / "absence_ajout.jpg", (0, 80, 600, 430)),
    "note_datee": (ICI / "img" / "note_ajout.jpg", (0, 80, 600, 330)),
    # samedi 5
    "references_valeurs": (ICI / "img" / "donnees_references.jpg", (0, 140, 1280, 410)),
    "lieux": (ICI / "img" / "lieux_liste.jpg", (0, 60, 1280, 260)),
}
NBSP = " "
TIRETS_INTERDITS = ("—", "–")
PIED = ('<div style="font-family:sans-serif;font-size:7.5pt;color:#4a5d69;width:100%;padding:0 15mm;'
        'display:flex;justify-content:space-between"><span>Carnet de stage : formation de l\'apprenant</span>'
        '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')


def recadrer():
    for nom, (source, boite) in RECADRAGES.items():
        Image.open(source).crop(boite).save(ICI / "img" / f"{nom}.jpg", quality=85)


def insecables(html):
    """Typographie française : pas de guillemet ni de deux-points isolé en début de ligne."""
    html = html.replace("« ", "«" + NBSP)
    return re.sub(r" ([»:;?!])", lambda m: NBSP + m.group(1), html)


def generer(nom):
    source = ICI / f"{nom}.html"
    texte = source.read_text(encoding="utf-8")
    interdits = [c for c in TIRETS_INTERDITS if c in texte]
    if interdits:
        raise SystemExit(f"{source.name} : tiret long interdit ({interdits})")
    temporaire = ICI / f".{nom}.rendu.html"
    temporaire.write_text(insecables(texte), encoding="utf-8")
    try:
        with sync_playwright() as p:
            navigateur = p.chromium.launch()
            page = navigateur.new_page()
            page.goto(temporaire.as_uri())
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            manquantes = page.evaluate(
                "[...document.images].filter(i => !i.naturalWidth).map(i => i.getAttribute('src'))")
            if manquantes:
                raise SystemExit(f"Images introuvables : {manquantes}")
            cible = ICI / f"{nom}.pdf"
            page.pdf(path=str(cible), format="A4", print_background=True, prefer_css_page_size=True,
                     display_header_footer=True, header_template="<span></span>", footer_template=PIED)
            navigateur.close()
    finally:
        temporaire.unlink(missing_ok=True)
    publier(cible)
    print(f"{cible.name} : {cible.stat().st_size // 1024} Ko")


def publier(pdf):
    """Copie la fiche dans les fichiers statiques de l'application, avec sa couverture en WebP."""
    PUBLICATION.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, PUBLICATION / pdf.name)
    page = fitz.open(pdf)[0].get_pixmap(dpi=60)
    Image.open(io.BytesIO(page.tobytes("png"))).convert("RGB").save(
        PUBLICATION / f"{pdf.stem}.webp", "WEBP", quality=80, method=6)


if __name__ == "__main__":
    recadrer()
    for nom in sys.argv[1:] or sorted(f.stem for f in ICI.glob("samedi-*.html")):
        generer(nom)
