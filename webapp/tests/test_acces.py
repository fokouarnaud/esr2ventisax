"""US-01 à US-03 : comptes, groupes et cloisonnement."""

import datetime

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command

from carnet.acces import est_formateur, stages_visibles, stages_modifiables
from carnet.models import Stage


@pytest.fixture
def formateur(db):
    call_command("creer_groupes")
    user = User.objects.create_user("prof", password="x")
    user.groups.add(Group.objects.get(name="Formateur"))
    return user


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
    assert sorted(Group.objects.values_list("name", flat=True)) == ["Apprenant", "Formateur"]


def test_apprenant_ne_voit_que_ses_stages(stage, stage_de_bruno, apprenant):
    assert list(stages_visibles(apprenant)) == [stage]


def test_formateur_ne_voit_que_les_stages_dont_il_est_referent(stage, stage_de_bruno, formateur):
    stage.formateur_referent = formateur
    stage.save()
    assert list(stages_visibles(formateur)) == [stage]


def test_formateur_ne_peut_modifier_aucun_stage(stage, formateur):
    stage.formateur_referent = formateur
    stage.save()
    assert list(stages_modifiables(formateur)) == []
    assert est_formateur(formateur)


def test_superutilisateur_voit_tout(stage, stage_de_bruno):
    admin = User.objects.create_superuser("admin", password="x")
    assert set(stages_visibles(admin)) == {stage, stage_de_bruno}
