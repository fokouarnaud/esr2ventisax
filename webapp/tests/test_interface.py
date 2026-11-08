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
    html = client.get(reverse("comptes:connexion")).content.decode()  # page publique unique (B6)
    assert "Bon retour sur" in html
    assert "Découvrir le Carnet" in html
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


def test_modeles_classes_sans_tenir_compte_des_accents(rf, db):
    # Le menu de gauche suit désormais l'ordre des groupes de B11 ; la liste des applications garde le tri A37.
    from django.contrib import admin
    from django.contrib.auth.models import User

    requete = rf.get("/admin/")
    requete.user = User.objects.create_superuser("root", password="x")
    carnet = next(a for a in admin.site.get_app_list(requete) if a["app_label"] == "carnet")
    noms = [str(m["name"]) for m in carnet["models"]]
    attendus = ["Données techniques", "Équipements", "Fiches entreprise", "Références", "Rubriques"]
    assert [n for n in noms if n in attendus] == attendus
