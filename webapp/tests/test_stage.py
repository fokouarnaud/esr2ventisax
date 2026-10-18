"""US-05 à US-08 : stage, couverture et formulaires du cours."""

import datetime
import uuid

import pytest
from django.core.exceptions import ValidationError


def test_stage_a_une_cle_uuid(stage):
    assert isinstance(stage.pk, uuid.UUID)


def test_creer_un_stage_cree_fiche_mission_et_bilan(stage):
    assert stage.fiche_entreprise.historique == ""
    assert stage.mission.poste == ""
    assert stage.bilan.critiques == ""


def test_date_de_fin_avant_debut_est_refusee(stage):
    stage.date_fin = datetime.date(2026, 3, 1)
    with pytest.raises(ValidationError) as exc:
        stage.full_clean()
    assert "date_fin" in exc.value.message_dict


def test_quota_par_defaut_80_mo(stage):
    assert stage.quota_mo == 80


def test_jours_travailles_par_defaut_lundi_a_samedi(stage):
    # 0 = lundi … 6 = dimanche (datetime.weekday)
    assert stage.jours_travailles == [0, 1, 2, 3, 4, 5]
