"""US-15, US-16, US-18 : photos, EXIF/GPS, quota, préparation à l'export."""

import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from carnet.models import Photo
from carnet.services.images import traiter_image
from carnet.services.quota import QuotaDepasse, octets_utilises

# 3°52'0.12" N, 11°31'0.12" E  →  3.8667, 11.5167 (calculé à la main)
GPS = {1: "N", 2: (3.0, 52.0, 0.12), 3: "E", 4: (11.0, 31.0, 0.12)}


def jpeg(largeur=4000, hauteur=3000, gps=None, date=None):
    img = Image.new("RGB", (largeur, hauteur), (30, 120, 200))
    exif = Image.Exif()
    if gps:
        exif.get_ifd(0x8825).update(gps)
    if date:
        exif.get_ifd(0x8769)[0x9003] = date
    tampon = io.BytesIO()
    img.save(tampon, "JPEG", exif=exif.tobytes())
    return tampon.getvalue()


@pytest.fixture(autouse=True)
def media_temporaire(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


# --- Traitement de l'image (US-15) --------------------------------------------

def test_grande_photo_reduite_a_1600_px_sur_le_grand_cote():
    resultat = traiter_image(io.BytesIO(jpeg(4000, 3000)))
    assert Image.open(io.BytesIO(resultat.contenu)).size == (1600, 1200)


def test_photo_portrait_reduite_aussi():
    resultat = traiter_image(io.BytesIO(jpeg(3000, 4000)))
    assert Image.open(io.BytesIO(resultat.contenu)).size == (1200, 1600)


def test_petite_photo_non_agrandie():
    resultat = traiter_image(io.BytesIO(jpeg(800, 600)))
    assert Image.open(io.BytesIO(resultat.contenu)).size == (800, 600)


def test_coordonnees_gps_lues_dans_l_exif():
    resultat = traiter_image(io.BytesIO(jpeg(gps=GPS)))
    assert resultat.latitude == pytest.approx(3.8667, abs=1e-4)
    assert resultat.longitude == pytest.approx(11.5167, abs=1e-4)


def test_hemisphere_sud_et_ouest_negatifs():
    resultat = traiter_image(io.BytesIO(jpeg(gps={**GPS, 1: "S", 3: "W"})))
    assert resultat.latitude == pytest.approx(-3.8667, abs=1e-4)
    assert resultat.longitude == pytest.approx(-11.5167, abs=1e-4)


def test_sans_gps_coordonnees_vides():
    resultat = traiter_image(io.BytesIO(jpeg()))
    assert resultat.latitude is None and resultat.longitude is None


def test_exif_conserve_dans_le_fichier_stocke():  # A22
    resultat = traiter_image(io.BytesIO(jpeg(gps=GPS)))
    assert Image.open(io.BytesIO(resultat.contenu)).getexif().get_ifd(0x8825)[1] == "N"


def test_date_de_prise_de_vue_lue():
    resultat = traiter_image(io.BytesIO(jpeg(date="2026:03:04 10:15:00")))
    assert (resultat.prise_le.day, resultat.prise_le.hour) == (4, 10)


# --- Photo et quota (US-15, US-18) --------------------------------------------

def test_ajouter_photo_nomme_le_fichier_par_uuid_et_garde_le_gps(stage):
    photo = Photo.ajouter(stage, SimpleUploadedFile("IMG_001.jpg", jpeg(gps=GPS)))
    assert photo.fichier.name == f"photos/{stage.pk}/{photo.pk}.jpg"
    assert photo.latitude == pytest.approx(3.8667, abs=1e-4)
    assert photo.taille_octets == photo.fichier.size


def test_gps_du_navigateur_utilise_si_exif_absent(stage):
    photo = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg()), latitude=4.05, longitude=9.7)
    assert (photo.latitude, photo.longitude) == (4.05, 9.7)


def test_octets_utilises_somme_les_photos_du_stage(stage):
    a = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(800, 600)))
    b = Photo.ajouter(stage, SimpleUploadedFile("b.jpg", jpeg(800, 600)))
    assert octets_utilises(stage) == a.taille_octets + b.taille_octets


def test_photo_refusee_au_dela_du_quota(stage):
    stage.quota_mo = 0
    stage.save()
    with pytest.raises(QuotaDepasse):
        Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(800, 600)))
    assert Photo.objects.count() == 0


def test_fichier_non_image_refuse(stage):
    with pytest.raises(ValidationError):
        Photo.ajouter(stage, SimpleUploadedFile("a.jpg", b"pas une image"))


# --- Destination et export (US-16) --------------------------------------------

def test_destination_par_defaut_a_trier(stage):
    assert Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(80, 60))).destination == Photo.Destination.A_TRIER


def test_photo_du_corps_sans_slug_ni_legende_bloque_l_export(stage):
    photo = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(80, 60)))
    photo.destination = Photo.Destination.CORPS
    photo.save()
    assert photo.problemes_export() == ["slug manquant", "légende manquante"]


def test_photo_preuve_jamais_bloquante(stage):
    photo = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(80, 60)))
    photo.destination = Photo.Destination.PREUVE
    assert photo.problemes_export() == []


def test_slug_unique_par_stage(stage):
    a = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(80, 60)))
    a.slug = "colonne"
    a.save()
    b = Photo.ajouter(stage, SimpleUploadedFile("b.jpg", jpeg(80, 60)))
    b.slug = "colonne"
    with pytest.raises(ValidationError):
        b.full_clean()


def test_deux_photos_sans_slug_autorisees(stage):
    Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg(80, 60)))
    b = Photo.ajouter(stage, SimpleUploadedFile("b.jpg", jpeg(80, 60)))
    b.full_clean()
