"""A10 et A11 : l'admin Unfold parle français et suit la charte (DoD P5 §4)."""

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse

ANGLAIS = ["Welcome back to", "Return to site", "Type to search", ">Filters<", "Toggle sidebar"]


@pytest.fixture
def client_apprenant(client, db, stage):
    call_command("creer_groupes")
    stage.proprietaire.is_staff = True
    stage.proprietaire.save()
    stage.proprietaire.groups.add(Group.objects.get(name="Apprenant"))
    client.force_login(stage.proprietaire)
    return client


def test_connexion_en_francais(client, db):
    html = client.get(reverse("admin:login")).content.decode()
    assert "Bon retour sur" in html
    assert "Retour au site" in html
    for chaine in ANGLAIS:
        assert chaine not in html


def test_liste_admin_en_francais(client_apprenant):
    html = client_apprenant.get(reverse("admin:carnet_entreejournal_changelist")).content.decode()
    assert "Rechercher" in html
    assert "Filtres" in html
    for chaine in ANGLAIS:
        assert chaine not in html


def test_bouton_primaire_aux_couleurs_de_la_charte(settings):
    # Le blanc sur #0d665e atteint le contraste AA ; l'ancien #12867a restait sous 4,5:1
    assert settings.UNFOLD["COLORS"]["primary"]["600"] == "#0d665e"


def test_modeles_classes_sans_tenir_compte_des_accents(client_apprenant):
    html = client_apprenant.get(reverse("admin:index")).content.decode()
    noms = ["Données techniques", "Équipements", "Fiches entreprise", "Références", "Rubriques"]
    positions = [html.index(n) for n in noms]
    assert positions == sorted(positions)
