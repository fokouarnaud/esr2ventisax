"""US-04, US-10, US-16, US-18, US-27 : vues hors admin."""

import datetime
import io
import zipfile

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from carnet.models import EntreeJournal, Lieu, Photo, Rubrique, Stage

D = datetime.date


def jpeg(nom="a.jpg"):
    tampon = io.BytesIO()
    Image.new("RGB", (40, 30), (10, 10, 200)).save(tampon, "JPEG")
    return SimpleUploadedFile(nom, tampon.getvalue(), content_type="image/jpeg")


@pytest.fixture(autouse=True)
def media_temporaire(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def connecte(client, apprenant, stage):
    client.force_login(apprenant)
    return client


@pytest.fixture
def stage_bruno(autre_apprenant):
    return Stage.objects.create(proprietaire=autre_apprenant, intitule="B", date_debut=D(2026, 3, 2),
                                date_fin=D(2026, 6, 26))


# --- Note rapide (US-10, US-18) -------------------------------------------------

def test_note_rapide_exige_une_connexion(client, db):
    reponse = client.get(reverse("carnet:note_rapide"))
    assert reponse.status_code == 302 and "login" in reponse["Location"]


def test_formulaire_note_rapide_affiche(connecte):
    assert connecte.get(reverse("carnet:note_rapide")).status_code == 200


def test_note_rapide_cree_note_photos_et_gps(connecte, stage):
    historique = Rubrique.objects.get(code="entreprise.historique")
    connecte.post(reverse("carnet:note_rapide"), {
        "texte": "Pose du collecteur", "latitude": "4.05", "longitude": "9.7",
        "rubriques": [historique.pk], "photos": [jpeg("a.jpg"), jpeg("b.jpg")],
    })
    note = EntreeJournal.objects.get(stage=stage)
    assert note.texte == "Pose du collecteur" and note.latitude == 4.05
    assert list(note.rubriques.all()) == [historique]
    assert note.photos.count() == 2
    assert all(p.latitude == 4.05 for p in note.photos.all())


def test_note_rapide_rattachee_au_lieu_proche(connecte, stage):
    lieu = Lieu.objects.create(stage=stage, nom="Chantier", latitude=4.05, longitude=9.7)
    connecte.post(reverse("carnet:note_rapide"), {"texte": "x", "latitude": "4.0505", "longitude": "9.7"})
    assert EntreeJournal.objects.get().lieu == lieu


def test_note_rapide_refusee_entierement_si_quota_depasse(connecte, stage):
    stage.quota_mo = 0
    stage.save()
    reponse = connecte.post(reverse("carnet:note_rapide"), {"texte": "x", "photos": [jpeg()]})
    assert reponse.status_code == 200
    assert "Quota" in reponse.content.decode()
    assert EntreeJournal.objects.count() == 0


def test_note_rapide_texte_obligatoire(connecte):
    connecte.post(reverse("carnet:note_rapide"), {"texte": "  "})
    assert EntreeJournal.objects.count() == 0


def test_note_rapide_refuse_une_etiquette_d_un_autre_stage(connecte, stage_bruno):
    etrangere = Rubrique.objects.create(stage=stage_bruno, libelle="X", partie="theme")
    connecte.post(reverse("carnet:note_rapide"), {"texte": "x", "rubriques": [etrangere.pk]})
    assert EntreeJournal.objects.count() == 0


# --- Stage actif (US-04) ---------------------------------------------------------

def test_choisir_le_stage_actif(connecte, apprenant, stage):
    autre = Stage.objects.create(proprietaire=apprenant, intitule="Récent", date_debut=D(2026, 9, 1),
                                 date_fin=D(2026, 12, 1))
    connecte.post(reverse("carnet:stage_actif"), {"stage": stage.pk})
    connecte.post(reverse("carnet:note_rapide"), {"texte": "x"})
    assert EntreeJournal.objects.get().stage == stage
    assert autre.entreejournal_set.count() == 0


def test_choisir_le_stage_d_un_autre_interdit(connecte, stage_bruno):
    assert connecte.post(reverse("carnet:stage_actif"), {"stage": stage_bruno.pk}).status_code == 403


# --- Tri des photos (US-16) --------------------------------------------------------

def test_tri_des_photos_ne_montre_que_les_siennes(connecte, stage, stage_bruno):
    mienne = Photo.ajouter(stage, jpeg(), legende="Ma photo")
    Photo.ajouter(stage_bruno, jpeg(), legende="Photo de Bruno")
    page = connecte.get(reverse("carnet:tri_photos")).content.decode()
    assert "Ma photo" in page and "Photo de Bruno" not in page
    assert str(mienne.pk) in page


def test_changer_la_destination_d_une_photo(connecte, stage):
    photo = Photo.ajouter(stage, jpeg())
    connecte.post(reverse("carnet:destination_photo", args=[photo.pk]), {"destination": "annexe"})
    photo.refresh_from_db()
    assert photo.destination == "annexe"


def test_destination_invalide_refusee(connecte, stage):
    photo = Photo.ajouter(stage, jpeg())
    assert connecte.post(reverse("carnet:destination_photo", args=[photo.pk]),
                         {"destination": "poubelle"}).status_code == 400


def test_changer_la_photo_d_un_autre_introuvable(connecte, stage_bruno):
    photo = Photo.ajouter(stage_bruno, jpeg())
    assert connecte.post(reverse("carnet:destination_photo", args=[photo.pk]),
                         {"destination": "corps"}).status_code == 404


# --- Export (US-27) -------------------------------------------------------------------

def test_export_telecharge_un_zip_valide(connecte, stage):
    reponse = connecte.get(reverse("carnet:export", args=[stage.pk]))
    assert reponse.status_code == 200
    assert reponse["Content-Type"] == "application/zip"
    assert f"{stage.slug}" in reponse["Content-Disposition"]
    z = zipfile.ZipFile(io.BytesIO(b"".join(reponse.streaming_content)))
    assert "config/infos.tex" in z.namelist()


def test_export_du_stage_d_un_autre_introuvable(connecte, stage_bruno):
    assert connecte.get(reverse("carnet:export", args=[stage_bruno.pk])).status_code == 404


def test_export_impossible_explique_pourquoi(connecte, stage):
    Photo.ajouter(stage, jpeg(), destination=Photo.Destination.CORPS)
    reponse = connecte.get(reverse("carnet:export", args=[stage.pk]), follow=True)
    assert "slug manquant" in reponse.content.decode()


def test_superutilisateur_voit_l_occupation_globale(client, stage):
    admin = User.objects.create_superuser("root", password="x")
    client.force_login(admin)
    assert "Occupation du disque" in client.get(reverse("admin:index")).content.decode()
