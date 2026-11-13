"""Coordonnées affichées avec leur hémisphère : N/S pour la latitude, E/O pour la longitude."""

import pytest

from carnet.admin import EntreeJournalAdmin, LieuAdmin, PhotoAdmin
from carnet.coordonnees import formater_position
from carnet.models import EntreeJournal, Lieu, Photo
from carnet.services.terrain_md import terrain_md


@pytest.mark.parametrize("lat, lon, attendu", [
    (4.0255, 9.6941, "4,02550° N ; 9,69410° E"),
    (-3.8667, -11.5167, "3,86670° S ; 11,51670° O"),
    (0, 0, "0,00000° N ; 0,00000° E"),
])
def test_position_porte_son_hemisphere(lat, lon, attendu):
    assert formater_position(lat, lon) == attendu


def test_position_absente():
    assert formater_position(None, 9.7) == ""


@pytest.mark.parametrize("modele", [Lieu, EntreeJournal, Photo])
def test_champs_expliquent_le_signe(modele):
    assert "nord" in modele._meta.get_field("latitude").help_text.lower()
    assert "est ou ouest" in modele._meta.get_field("longitude").help_text.lower()


def test_admin_affiche_la_position():
    assert "position" in LieuAdmin.list_display
    assert "position" in PhotoAdmin.readonly_fields
    assert "position" in EntreeJournalAdmin.readonly_fields


@pytest.mark.django_db
def test_terrain_md_donne_l_hemisphere(stage):
    Lieu.objects.create(stage=stage, nom="Chantier", type=Lieu.Type.CHANTIER, latitude=4.0255, longitude=9.6941)
    assert "4,02550° N ; 9,69410° E" in terrain_md(stage)


# --- Saisie : valeur sans signe + hémisphère choisi dans une liste ---------------------------------

from django.contrib import admin  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402

from carnet.coordonnees import ChampCoordonnee  # noqa: E402


@pytest.mark.parametrize("axe, saisie, attendu", [
    ("latitude", ["4.0255", "N"], 4.0255),
    ("latitude", ["3,8667", "S"], -3.8667),
    ("longitude", ["9.6941", "E"], 9.6941),
    ("longitude", ["11.5167", "O"], -11.5167),
])
def test_saisie_avec_hemisphere(axe, saisie, attendu):
    assert ChampCoordonnee(axe).clean(saisie) == pytest.approx(attendu)


@pytest.mark.parametrize("axe, saisie", [
    ("latitude", ["91", "N"]), ("longitude", ["181", "E"]), ("latitude", ["-4", "N"]), ("latitude", ["4", "E"]),
])
def test_saisie_refusee(axe, saisie):
    with pytest.raises(ValidationError):
        ChampCoordonnee(axe).clean(saisie)


def test_saisie_facultative_vide():
    assert ChampCoordonnee("latitude", required=False).clean(["", "N"]) is None


def test_valeur_enregistree_redonne_l_hemisphere():
    widget = ChampCoordonnee("longitude").widget
    assert widget.decompress(-11.5167) == ["11,5167", "O"]
    assert widget.decompress(None) == [None, "E"]


@pytest.mark.parametrize("modele", [Lieu, EntreeJournal])
def test_admin_saisit_avec_hemisphere(modele, rf):
    modele_admin = admin.site._registry[modele]
    for nom in ("latitude", "longitude"):
        champ = modele_admin.formfield_for_dbfield(modele._meta.get_field(nom), request=rf.get("/"))
        assert isinstance(champ, ChampCoordonnee)


@pytest.mark.django_db
def test_admin_enregistre_un_lieu_au_sud_et_a_l_ouest(client, apprenant, stage):
    client.force_login(apprenant)
    reponse = client.post("/admin/carnet/lieu/add/", {
        "stage": stage.pk, "nom": "Chantier", "type": "chantier",
        "latitude_0": "3,8667", "latitude_1": "S", "longitude_0": "11.5167", "longitude_1": "O",
    })
    assert reponse.status_code == 302, reponse.content.decode()[:2000]
    lieu = Lieu.objects.get(stage=stage)
    assert (lieu.latitude, lieu.longitude) == (pytest.approx(-3.8667), pytest.approx(-11.5167))
    liste = client.get("/admin/carnet/lieu/").content.decode()
    assert "3,86670° S ; 11,51670° O" in liste
    formulaire = client.get(f"/admin/carnet/lieu/{lieu.pk}/change/").content.decode()
    assert "Utiliser ma position" in formulaire and "carnet/js/coordonnees.js" in formulaire
