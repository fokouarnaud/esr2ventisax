"""US-38 : le premier stage connaît le nom de l'apprenant (B9). Plus de formateur prérempli (B17)."""

import datetime

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse

from carnet.models import Stage


@pytest.fixture
def awa(db):
    call_command("creer_groupes")
    user = User.objects.create_user("awa", password="x", first_name="Awa", last_name="Ndongo")
    user.profil.save()  # profil Apprenant : droits appliqués
    return user


def formulaire_initial(client, user):
    client.force_login(user)
    return client.get(reverse("admin:carnet_stage_add")).context["adminform"].form.initial


def test_premier_stage_prerempli_avec_le_nom(client, awa):
    assert formulaire_initial(client, awa)["apprenant_nom"] == "Awa Ndongo"


def test_deuxieme_stage_non_prerempli(client, awa):
    Stage.objects.create(proprietaire=awa, intitule="Premier", date_debut=datetime.date(2026, 1, 5),
                         date_fin=datetime.date(2026, 3, 27))
    assert "apprenant_nom" not in formulaire_initial(client, awa)
