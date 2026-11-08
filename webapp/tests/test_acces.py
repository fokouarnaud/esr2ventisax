"""US-01 à US-03 : comptes, groupes et cloisonnement."""

import datetime

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command

from carnet.acces import stages_modifiables, stages_visibles
from carnet.models import Stage


@pytest.fixture
def stage_de_bruno(autre_apprenant):
    return Stage.objects.create(
        proprietaire=autre_apprenant,
        intitule="Stage froid",
        date_debut=datetime.date(2026, 3, 2),
        date_fin=datetime.date(2026, 6, 26),
    )


def test_creer_groupes_est_idempotent(db):
    call_command("creer_groupes")
    call_command("creer_groupes")
    assert sorted(Group.objects.values_list("name", flat=True)) == ["Apprenant"]


def test_apprenant_ne_voit_que_ses_stages(stage, stage_de_bruno, apprenant):
    assert list(stages_visibles(apprenant)) == [stage]


def test_superutilisateur_voit_tout(stage, stage_de_bruno):
    admin = User.objects.create_superuser("admin", password="x")
    assert set(stages_visibles(admin)) == {stage, stage_de_bruno}
