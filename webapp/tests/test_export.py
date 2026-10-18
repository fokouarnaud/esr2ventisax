"""US-27, US-28 : zip « dossier terrain » (contrat P4), sauvegarde et restauration."""

import datetime
import io
import json
import uuid
import zipfile
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image

from carnet.models import (
    DonneeTechnique, EntreeJournal, Personne, Photo, Reference, Rubrique, Stage,
)
from carnet.services.export import ExportImpossible, ecrire_zip, restaurer

D = datetime.date


def jpeg():
    tampon = io.BytesIO()
    Image.new("RGB", (40, 30), (200, 10, 10)).save(tampon, "JPEG")
    return tampon.getvalue()


@pytest.fixture(autouse=True)
def media_temporaire(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def stage_rempli(stage):
    stage.fiche_entreprise.historique = "Créée en 2009 à Douala."
    stage.fiche_entreprise.save()
    note = EntreeJournal.objects.create(stage=stage, date=D(2026, 3, 3), texte="Le DG raconte la création.")
    note.etiqueter([Rubrique.objects.get(code="entreprise.historique")])
    Personne.objects.create(stage=stage, nom="M. Secret", fonction="chef de chantier", telephone="699000000",
                            nom_publiable=False, a_remercier=True)
    ref = Reference.objects.create(stage=stage, type="norme", auteur="AFNOR", titre="NF DTU 60.11", annee=2013)
    DonneeTechnique.objects.create(stage=stage, grandeur="Débit lavabo", valeur=Decimal("0.20"), unite="L/s",
                                   nature="reference", date=D(2026, 3, 3), reference=ref)
    corps = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg()), slug="colonne", legende="Colonne montante",
                          destination=Photo.Destination.CORPS)
    corps.rubriques.add(Rubrique.objects.get(code="mission.poste"))
    Photo.ajouter(stage, SimpleUploadedFile("b.jpg", jpeg()), destination=Photo.Destination.PREUVE)
    return stage


def exporter(stage):
    flux = io.BytesIO()
    ecrire_zip(stage, flux)
    flux.seek(0)
    return zipfile.ZipFile(flux)


# --- Contenu du zip (US-27, P4) --------------------------------------------------

def test_zip_contient_les_fichiers_du_contrat(stage_rempli):
    noms = set(exporter(stage_rempli).namelist())
    assert {"manifest.json", "terrain.json", "terrain.md", "config/infos.tex", "bib/references.bib",
            "img/fig_colonne.jpg"} <= noms


def test_seules_les_photos_corps_et_annexe_vont_dans_img(stage_rempli):
    images = [n for n in exporter(stage_rempli).namelist() if n.startswith("img/")]
    assert images == ["img/fig_colonne.jpg"]


def test_toutes_les_photos_sont_sauvegardees(stage_rempli):
    sauvegardes = [n for n in exporter(stage_rempli).namelist() if n.startswith("sauvegarde/")]
    assert len(sauvegardes) == 2


def test_manifeste_somme_de_controle(stage_rempli):
    import hashlib

    z = exporter(stage_rempli)
    manifeste = json.loads(z.read("manifest.json"))
    assert manifeste["stage"] == str(stage_rempli.pk)
    assert manifeste["fichiers"]["config/infos.tex"] == hashlib.sha256(z.read("config/infos.tex")).hexdigest()


def test_telephone_jamais_exporte(stage_rempli):
    z = exporter(stage_rempli)
    for nom in z.namelist():
        if nom.endswith((".json", ".md", ".tex", ".bib")):
            assert "699000000" not in z.read(nom).decode()


def test_nom_non_publiable_remplace_par_la_fonction_dans_terrain_md(stage_rempli):
    md = exporter(stage_rempli).read("terrain.md").decode()
    assert "M. Secret" not in md
    assert "le chef de chantier" in md


def test_terrain_md_classe_les_notes_sous_leur_rubrique(stage_rempli):
    md = exporter(stage_rempli).read("terrain.md").decode()
    section = md.split("### Historique de l'entreprise", 1)[1].split("\n### ", 1)[0]
    assert "Créée en 2009 à Douala." in section
    assert "03/03/2026" in section and "Le DG raconte la création." in section


def test_terrain_md_donnee_technique_avec_sa_source(stage_rempli):
    md = exporter(stage_rempli).read("terrain.md").decode()
    assert "Débit lavabo = 0.2 L/s" in md and "afnor2013" in md


def test_export_refuse_si_photo_du_corps_sans_legende(stage_rempli):
    photo = Photo.objects.get(slug="colonne")
    photo.legende = ""
    photo.save()
    with pytest.raises(ExportImpossible) as exc:
        exporter(stage_rempli)
    assert "légende manquante" in str(exc.value)


def test_export_met_a_jour_la_derniere_sauvegarde(stage_rempli):
    avant = timezone.now()
    exporter(stage_rempli)
    stage_rempli.refresh_from_db()
    assert stage_rempli.derniere_sauvegarde >= avant


# --- Restauration (US-28) --------------------------------------------------------

def test_rubriques_du_cours_ont_un_identifiant_stable_entre_bases(db):
    r = Rubrique.objects.get(code="entreprise.historique")
    assert r.pk == uuid.uuid5(uuid.NAMESPACE_URL, "carnet-de-stage:rubrique:entreprise.historique")


def test_restauration_dans_une_base_videe_redonne_les_memes_entites(stage_rempli, apprenant, tmp_path, settings):
    z = exporter(stage_rempli)
    pk, note_pk = stage_rempli.pk, EntreeJournal.objects.get().pk
    stage_rempli.delete()
    import shutil
    shutil.rmtree(settings.MEDIA_ROOT)

    restaure = restaurer(z, proprietaire=apprenant)

    assert restaure.pk == pk
    assert restaure.fiche_entreprise.historique == "Créée en 2009 à Douala."
    note = EntreeJournal.objects.get(pk=note_pk)
    assert list(note.rubriques.values_list("code", flat=True)) == ["entreprise.historique"]
    photo = Photo.objects.get(slug="colonne")
    assert photo.fichier.size > 0
    assert DonneeTechnique.objects.get().reference.cle_bibtex == "afnor2013"


def test_restaurer_deux_fois_ne_cree_pas_de_doublons(stage_rempli, apprenant):
    z = exporter(stage_rempli)
    restaurer(z, proprietaire=apprenant)
    restaurer(z, proprietaire=apprenant)
    assert Stage.objects.count() == 1
    assert Photo.objects.count() == 2
    assert EntreeJournal.objects.count() == 1


def test_restauration_attribue_le_proprietaire_donne(stage_rempli, autre_apprenant):
    z = exporter(stage_rempli)
    stage_rempli.delete()
    assert restaurer(z, proprietaire=autre_apprenant).proprietaire == autre_apprenant


def test_logo_exporte_en_png_au_nom_attendu_par_la_couverture(stage):
    stage.logo_cfp = SimpleUploadedFile("logo.jpg", jpeg())
    stage.save()
    z = exporter(stage)
    assert Image.open(io.BytesIO(z.read("img/logo_cfp.png"))).format == "PNG"
