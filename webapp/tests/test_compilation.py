"""US-30 : un stage importé dans le vrai modèle tex_export_src/ compile (latexmk + biber)."""

import datetime
import io
import shutil
import subprocess
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from PIL import Image

from carnet.models import DonneeTechnique, Equipement, NoeudOrganigramme, Photo, Reference, Tache
from carnet.services.export import ecrire_zip

pytestmark = pytest.mark.skipif(shutil.which("latexmk") is None, reason="latexmk absent")
MODELE = __import__("django.conf").conf.settings.BASE_DIR.parent / "tex_export_src"


def jpeg():
    tampon = io.BytesIO()
    Image.new("RGB", (400, 300), (0, 120, 60)).save(tampon, "JPEG")
    return tampon.getvalue()


@pytest.fixture
def dossier_importe(stage, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"
    stage.entreprise, stage.cfp = "B&T Sarl", "CFP 50 % pratique"
    stage.logo_cfp = SimpleUploadedFile("logo.jpg", jpeg())
    stage.save()
    dg = NoeudOrganigramme.objects.create(stage=stage, poste="Directeur général")
    NoeudOrganigramme.objects.create(stage=stage, poste="Stagiaire", parent=dg, est_stagiaire=True)
    Tache.objects.create(stage=stage, libelle="Accueil, sécurité", date_debut=datetime.date(2026, 3, 2))
    Equipement.objects.create(stage=stage, designation="Cintreuse", categorie="outillage",
                              caracteristiques="Ø 16–20 mm", role="Cintrer le PER & le cuivre")
    ref = Reference.objects.create(stage=stage, type="norme", auteur="AFNOR", titre="NF DTU 60.11", annee=2013)
    DonneeTechnique.objects.create(stage=stage, grandeur="Débit", valeur=Decimal("0.2"), unite="L/s",
                                   nature="reference", date=datetime.date(2026, 3, 3), reference=ref)
    Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg()), slug="colonne_montante", legende="Colonne 50 %",
                  destination=Photo.Destination.CORPS)
    archive = tmp_path / "d.zip"
    with open(archive, "wb") as f:
        ecrire_zip(stage, f)
    call_command("importer_dossier", str(archive), "--modele", str(MODELE),
                 "--destination", str(tmp_path / "rapports"), "--sans-carte")
    (dossier,) = (tmp_path / "rapports").iterdir()
    return dossier


def compiler(dossier, principal):
    return subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", principal],
                          cwd=dossier, capture_output=True, text=True, timeout=600)


@pytest.mark.slow
def test_rapport_importe_compile(dossier_importe):
    resultat = compiler(dossier_importe, "main.tex")
    assert resultat.returncode == 0, resultat.stdout[-3000:]
    assert (dossier_importe / "main.pdf").stat().st_size > 50_000


@pytest.mark.slow
def test_catalogue_des_fragments_generes_compile(dossier_importe):
    shutil.copy(dossier_importe / "donnees_terrain" / "catalogue.tex", dossier_importe / "catalogue.tex")
    resultat = compiler(dossier_importe, "catalogue.tex")
    assert resultat.returncode == 0, resultat.stdout[-3000:]
