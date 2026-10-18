"""US-17 : lieux et rattachement automatique à moins de 200 m (A31)."""

import pytest
from django.core.exceptions import ValidationError

from carnet.models import Lieu

# Yaoundé, poste centrale ; 0,001° de latitude ≈ 111 m
LAT, LON = 3.8667, 11.5167


@pytest.fixture
def siege(stage):
    return Lieu.objects.create(stage=stage, nom="Siège", type=Lieu.Type.SIEGE, latitude=LAT, longitude=LON)


def test_lieu_le_plus_proche_a_moins_de_200_m(stage, siege):
    Lieu.objects.create(stage=stage, nom="Chantier", type=Lieu.Type.CHANTIER, latitude=LAT + 0.01, longitude=LON)
    assert Lieu.le_plus_proche(stage, LAT + 0.001, LON) == siege  # ≈ 111 m


def test_aucun_lieu_au_dela_de_200_m(stage, siege):
    assert Lieu.le_plus_proche(stage, LAT + 0.002, LON) is None  # ≈ 222 m


def test_les_lieux_d_un_autre_stage_sont_ignores(stage, siege, autre_apprenant):
    from carnet.models import Stage

    autre = Stage.objects.create(proprietaire=autre_apprenant, intitule="B",
                                 date_debut=stage.date_debut, date_fin=stage.date_fin)
    assert Lieu.le_plus_proche(autre, LAT, LON) is None


@pytest.mark.parametrize("lat,lon", [(91, 0), (-91, 0), (0, 181), (0, -181)])
def test_coordonnees_hors_bornes_refusees(stage, lat, lon):
    with pytest.raises(ValidationError):
        Lieu(stage=stage, nom="X", latitude=lat, longitude=lon).full_clean()
