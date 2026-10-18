"""US-12, US-13 : rubriques du cours et chapitres du thème (A24)."""

import datetime

import pytest
from django.core.exceptions import ValidationError

from carnet.models import Rubrique, Stage


def test_rubriques_du_cours_sont_prechargees(db):
    cours = Rubrique.objects.filter(stage__isnull=True)
    assert cours.filter(partie=Rubrique.Partie.ENTREPRISE).count() == 11
    assert cours.filter(partie=Rubrique.Partie.MISSION).count() == 9
    assert cours.filter(code="entreprise.historique").exists()


def test_rubriques_pour_un_stage_excluent_les_chapitres_des_autres(stage, autre_apprenant):
    autre = Stage.objects.create(
        proprietaire=autre_apprenant, intitule="Autre",
        date_debut=datetime.date(2026, 1, 1), date_fin=datetime.date(2026, 2, 1),
    )
    mien = Rubrique.objects.create(stage=stage, libelle="Mode opératoire", partie=Rubrique.Partie.THEME)
    sien = Rubrique.objects.create(stage=autre, libelle="Chambre froide", partie=Rubrique.Partie.THEME)

    disponibles = Rubrique.pour_stage(stage)

    assert mien in disponibles
    assert sien not in disponibles
    assert disponibles.filter(code="mission.poste").exists()


def test_un_chapitre_de_theme_n_a_qu_un_niveau_de_sous_chapitres(stage):
    chapitre = Rubrique.objects.create(stage=stage, libelle="Matériel", partie=Rubrique.Partie.THEME)
    sous = Rubrique.objects.create(stage=stage, libelle="Tubes", partie=Rubrique.Partie.THEME, parent=chapitre)
    petit = Rubrique(stage=stage, libelle="Cuivre", partie=Rubrique.Partie.THEME, parent=sous)
    with pytest.raises(ValidationError):
        petit.full_clean()


def test_un_sous_chapitre_doit_appartenir_au_meme_stage(stage, autre_apprenant):
    autre = Stage.objects.create(
        proprietaire=autre_apprenant, intitule="Autre",
        date_debut=datetime.date(2026, 1, 1), date_fin=datetime.date(2026, 2, 1),
    )
    chapitre = Rubrique.objects.create(stage=autre, libelle="X", partie=Rubrique.Partie.THEME)
    intrus = Rubrique(stage=stage, libelle="Y", partie=Rubrique.Partie.THEME, parent=chapitre)
    with pytest.raises(ValidationError):
        intrus.full_clean()


def test_un_chapitre_cree_par_l_apprenant_est_forcement_du_theme(stage):
    r = Rubrique(stage=stage, libelle="Historique bis", partie=Rubrique.Partie.ENTREPRISE)
    with pytest.raises(ValidationError):
        r.full_clean()
