"""Captures sources propres aux fiches de formation (docs/formation/img/), prises avec le compte de démonstration.

Prérequis : `manage.py charger_demo` puis `manage.py runserver 127.0.0.1:8765` depuis webapp/.
Lancement (Python système, avec Playwright) :  python docs/formation/capturer_sources.py
Les fiches les recadrent ensuite (generer_pdf.py, RECADRAGES). Les captures du manuel viennent de
docs/manuel/capturer_ecrans.py. Rien n'est enregistré dans la base : les formulaires sont seulement ouverts,
ou soumis avec une erreur volontaire.
"""

import json
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ICI = Path(__file__).resolve().parent
WEBAPP = ICI.parents[1] / "webapp"
PYTHON = WEBAPP / ".venv" / "Scripts" / "python.exe"
URL = "http://127.0.0.1:8765"
A = f"{URL}/admin/carnet"


def ids():
    code = ("import json; from carnet.models import Photo, Stage; s = Stage.objects.get(slug='stage-demo'); "
            "print(json.dumps({'stage': str(s.pk), 'photo': str(Photo.objects.get(stage=s, slug='manometre').pk)}))")
    sortie = subprocess.run([str(PYTHON), "manage.py", "shell", "-c", code], cwd=WEBAPP, capture_output=True,
                            text=True, encoding="utf-8", check=True)
    return json.loads(sortie.stdout.strip().splitlines()[-1])


def capture(page, nom):
    page.wait_for_timeout(400)
    page.screenshot(path=str(ICI / "img" / f"{nom}.jpg"), type="jpeg", quality=85)
    print("  ", nom)


def main():
    cles = ids()
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_context(viewport={"width": 1280, "height": 860}, locale="fr-FR", color_scheme="light").new_page()
        page.goto(f"{URL}/connexion/")
        page.fill("#id_username", "demo.apprenant")
        page.fill("#id_password", "demo-local-2026")
        page.click("form.form-auth button[type=submit]")
        page.wait_for_load_state("networkidle")

        page.goto(f"{A}/stage/{cles['stage']}/change/")
        page.get_by_text("Suivi", exact=True).first.click()
        capture(page, "onglet_suivi")

        page.goto(f"{A}/donneetechnique/add/")
        page.select_option("#id_stage", label="Stage de démonstration : plomberie sanitaire")
        page.fill("#id_date", "17/08/2026")
        page.fill("#id_grandeur", "Pression d'essai d'étanchéité")
        page.fill("#id_valeur", "10")
        page.fill("#id_unite", "bar")
        page.select_option("#id_nature", "reference")
        page.click("button[name=_save]")
        page.wait_for_load_state("networkidle")
        capture(page, "refus_sans_source")

        for nom, url in [("equipement_ajout", "equipement/add/"), ("rubrique_ajout", "rubrique/add/"),
                         ("photo_fiche", f"photo/{cles['photo']}/change/"), ("absence_ajout", "absence/add/"),
                         ("note_ajout", "entreejournal/add/"), ("donnees_references", "donneetechnique/?nature__exact=reference"),
                         ("lieux_liste", "lieu/")]:
            page.goto(f"{A}/{url}")
            page.wait_for_load_state("networkidle")
            capture(page, nom)
        nav.close()


if __name__ == "__main__":
    main()
