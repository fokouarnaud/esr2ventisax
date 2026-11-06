"""Captures d'écran du manuel d'utilisation et du scénario, prises avec le compte de démonstration.

Prérequis : `manage.py charger_demo` puis `manage.py runserver 127.0.0.1:8765` depuis webapp/.
Lancement (Python système, avec Playwright) :  python docs/manuel/capturer_ecrans.py [dossier du zip]
Le zip exporté va dans ce dossier (par défaut le dossier temporaire) : jamais dans le dépôt (A14).
Le script crée une note datée du jour et un stage « premier jour » temporaire ; relancer ensuite
`manage.py charger_demo` pour retrouver la démo intacte.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

RACINE = Path(__file__).resolve().parents[2]
WEBAPP = RACINE / "webapp"
PYTHON = WEBAPP / ".venv" / "Scripts" / "python.exe"
SORTIE = Path(__file__).resolve().parent / "img"
URL = "http://127.0.0.1:8765"
IDENTIFIANT, MOT_DE_PASSE = "demo.apprenant", "demo-local-2026"
CHANTIER = {"latitude": 4.0255, "longitude": 9.6941}  # Résidence Démo (données fictives)


def django(code):
    """Exécute du code dans le shell Django et renvoie la dernière ligne, en JSON."""
    res = subprocess.run([str(PYTHON), "manage.py", "shell", "-c", code], cwd=WEBAPP, capture_output=True,
                         text=True, encoding="utf-8", check=True)
    return json.loads(res.stdout.strip().splitlines()[-1])


IDS = django("""
import json
from carnet.models import *
s = Stage.objects.get(slug='stage-demo')
n = EntreeJournal.objects.filter(stage=s).order_by('date')
print(json.dumps({
  'stage': str(s.pk), 'fiche': str(s.fiche_entreprise.pk), 'mission': str(s.mission.pk), 'bilan': str(s.bilan.pk),
  'premiere': str(n.first().pk), 'releve': str(n.filter(date='2026-08-17').first().pk), 'derniere': str(n.last().pk),
  'chantier': str(Lieu.objects.get(stage=s, type='chantier').pk),
  'donnee': str(DonneeTechnique.objects.get(stage=s, grandeur__startswith='Pression d\\'essai').pk),
  'photo': Photo.objects.get(stage=s, slug='manometre').fichier.path,
}))
""")


def capture(page, nom, plein=False):
    page.wait_for_timeout(400)
    page.screenshot(path=str(SORTIE / f"{nom}.jpg"), type="jpeg", quality=82, full_page=plein)
    print("  ", nom)


def connexion(page):
    page.goto(f"{URL}/admin/login/")
    page.fill("#id_username", IDENTIFIANT)
    page.fill("#id_password", MOT_DE_PASSE)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def onglet(page, libelle):
    el = page.get_by_text(libelle, exact=True).first
    el.click()
    el.evaluate("e => { e.scrollIntoView({block: 'start'}); window.scrollBy(0, -80); }")


def changer_stage(page, intitule):
    page.goto(f"{URL}/carnet/note/")
    if not page.locator("#choix-stage").count():  # un seul stage : pas de sélecteur
        return
    with page.expect_navigation():  # le sélecteur s'envoie seul (note_rapide.js)
        page.select_option("#choix-stage", label=intitule)


def bureau(p):
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 1280, "height": 860}, locale="fr-FR", color_scheme="light",
                          geolocation=CHANTIER, permissions=["geolocation"], accept_downloads=True)
    page = ctx.new_page()
    a = f"{URL}/admin/carnet"

    page.goto(f"{URL}/admin/login/")
    page.fill("#id_username", IDENTIFIANT)
    capture(page, "01_connexion")
    page.fill("#id_password", MOT_DE_PASSE)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    changer_stage(page, "Stage de démonstration : plomberie sanitaire")
    page.goto(f"{URL}/admin/")
    capture(page, "02_tableau_de_bord")

    page.goto(f"{a}/stage/{IDS['stage']}/change/")
    capture(page, "03_stage_general")
    onglet(page, "Couverture")
    capture(page, "03b_stage_couverture")

    page.goto(f"{a}/ficheentreprise/{IDS['fiche']}/change/")
    capture(page, "04_fiche_entreprise")
    page.goto(f"{a}/mission/{IDS['mission']}/change/")
    capture(page, "05_mission")
    page.goto(f"{a}/bilanpersonnel/{IDS['bilan']}/change/")
    capture(page, "06_bilan")

    page.goto(f"{a}/entreejournal/")
    capture(page, "07_journal_liste")
    page.goto(f"{a}/entreejournal/{IDS['releve']}/change/")
    onglet(page, "Rapport d'activité")
    capture(page, "08b_note_rapport_activite")
    page.goto(f"{a}/entreejournal/{IDS['premiere']}/change/")
    onglet(page, "Intervention")
    capture(page, "08c_note_intervention")
    onglet(page, "Liens")
    capture(page, "08d_note_liens")

    page.goto(f"{URL}/carnet/photos/")
    capture(page, "09_tri_photos")
    page.goto(f"{a}/photo/")
    capture(page, "09b_photos_liste")

    page.goto(f"{a}/lieu/{IDS['chantier']}/change/")
    page.wait_for_timeout(2500)  # tuiles OpenStreetMap
    capture(page, "10_lieu_carte")

    for nom, modele in (("11_rubriques", "rubrique"), ("12_organigramme", "noeudorganigramme"),
                        ("13_taches", "tache"), ("14_equipements", "equipement"),
                        ("15_donnees_techniques", "donneetechnique"), ("16_references", "reference"),
                        ("17_personnes", "personne"), ("18_abreviations", "abreviation"),
                        ("19_absences", "absence")):
        page.goto(f"{a}/{modele}/")
        capture(page, nom)
    page.goto(f"{a}/donneetechnique/{IDS['donnee']}/change/")
    capture(page, "15b_donnee_reference")

    page.goto(f"{URL}/admin/")
    with page.expect_download() as dl:
        page.get_by_role("link", name="Dossier terrain").click()
    zip_demo = Path(sys.argv[1] if len(sys.argv) > 1 else tempfile.gettempdir()) / dl.value.suggested_filename
    zip_demo.parent.mkdir(parents=True, exist_ok=True)
    dl.value.save_as(zip_demo)
    print("   zip :", zip_demo, zip_demo.stat().st_size // 1024, "Ko")
    page.reload()
    capture(page, "20_sauvegarde_faite")

    # Premier jour : un stage neuf, encore vide (supprimé ensuite par charger_demo)
    page.goto(f"{a}/stage/add/")
    capture(page, "21_creer_stage")
    django("""
import json, datetime
from django.contrib.auth import get_user_model
from carnet.models import Stage
u = get_user_model().objects.get(username='demo.apprenant')
Stage.objects.filter(proprietaire=u, slug='premier-jour').delete()
d = datetime.date.today()
Stage.objects.create(proprietaire=u, slug='premier-jour', intitule='Mon stage (premier jour)',
    specialite='Froid et climatisation', theme='Plomberie sanitaire', entreprise='Entreprise de démonstration',
    date_debut=d, date_fin=d + datetime.timedelta(weeks=16) - datetime.timedelta(days=2))
print(json.dumps(1))
""")
    changer_stage(page, "Mon stage (premier jour)")
    page.goto(f"{URL}/admin/")
    capture(page, "22_premier_jour_tableau")
    changer_stage(page, "Stage de démonstration : plomberie sanitaire")
    ctx.close()
    nav.close()


def mobile(p, sombre=False):
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True,
                          has_touch=True, locale="fr-FR", color_scheme="dark" if sombre else "light",
                          geolocation=CHANTIER, permissions=["geolocation"])
    page = ctx.new_page()
    connexion(page)
    changer_stage(page, "Stage de démonstration : plomberie sanitaire")
    page.goto(f"{URL}/carnet/note/")
    page.wait_for_timeout(1500)  # GPS simulé
    if sombre:
        capture(page, "30_note_rapide_sombre")
        ctx.close()
        nav.close()
        return
    capture(page, "30_note_rapide_vide")
    page.fill("textarea[name=texte]", "Essai d'étanchéité zone R+3 : 10 bar tenus 2 h, aucune chute. "
                                       "Fiche d'autocontrôle signée par le chef d'équipe.")
    page.locator("input[type=file][multiple]").set_input_files(IDS["photo"])
    page.wait_for_timeout(800)
    capture(page, "31_note_rapide_remplie")
    page.locator("details.etiquettes summary").click()
    page.get_by_label("Mise en œuvre : modes opératoires").first.check()
    page.get_by_label("Mise en œuvre : modes opératoires").first.scroll_into_view_if_needed()
    capture(page, "32_note_rapide_etiquettes")
    page.get_by_role("button", name="Enregistrer la note").click()
    page.wait_for_url("**enregistree=1")
    capture(page, "33_note_enregistree")
    page.goto(f"{URL}/carnet/photos/")
    capture(page, "34_tri_photos_mobile")
    page.goto(f"{URL}/admin/")
    capture(page, "35_tableau_de_bord_mobile")
    ctx.close()
    nav.close()


if __name__ == "__main__":
    SORTIE.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        print("Bureau (1280 px)")
        bureau(p)
        print("Mobile (390 px)")
        mobile(p)
        mobile(p, sombre=True)
