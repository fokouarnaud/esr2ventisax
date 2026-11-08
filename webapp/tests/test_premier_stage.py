"""US-38 : le premier stage connaît le nom de l'apprenant et le formateur de son code (B2, B9)."""

import datetime

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse

from carnet.models import Stage
from comptes.models import CodeInvitation


@pytest.fixture
def inscrit(db):
    call_command("creer_groupes")
    prof = User.objects.create_user("prof", password="x", is_staff=True, first_name="Paul", last_name="Mbia")
    prof.groups.add(Group.objects.get(name="Formateur"))
    code = CodeInvitation.objects.create(formateur=prof)
    awa = User.objects.create_user("awa", password="x", is_staff=True, first_name="Awa", last_name="Ndongo")
    awa.groups.add(Group.objects.get(name="Apprenant"))
    awa.profil.code_utilise = code
    awa.profil.save()
    return awa, prof


def formulaire_initial(client, user):
    client.force_login(user)
    return client.get(reverse("admin:carnet_stage_add")).context["adminform"].form.initial


def test_premier_stage_prerempli(client, inscrit):
    awa, prof = inscrit
    initial = formulaire_initial(client, awa)
    assert initial["apprenant_nom"] == "Awa Ndongo"
    assert initial["formateur_referent"] == prof.pk


def test_deuxieme_stage_non_prerempli(client, inscrit):
    awa, _ = inscrit
    Stage.objects.create(proprietaire=awa, intitule="Premier", date_debut=datetime.date(2026, 1, 5),
                         date_fin=datetime.date(2026, 3, 27))
    initial = formulaire_initial(client, awa)
    assert "apprenant_nom" not in initial and "formateur_referent" not in initial


def test_compte_sans_code_garde_un_formulaire_vierge(client, db):
    call_command("creer_groupes")
    lea = User.objects.create_user("lea", password="x", is_staff=True, first_name="Léa", last_name="Eto")
    lea.groups.add(Group.objects.get(name="Apprenant"))
    initial = formulaire_initial(client, lea)
    assert initial["apprenant_nom"] == "Léa Eto"
    assert "formateur_referent" not in initial
