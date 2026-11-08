"""US-33 (menu court en groupes), US-34 (déconnexion toujours visible) — B11."""

import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse

DECONNEXION = 'action="/deconnexion/"'


@pytest.fixture(autouse=True)
def groupes(db):
    call_command("creer_groupes")


def compte(nom, groupe):
    user = User.objects.create_user(nom, password="x", is_staff=True)
    user.groups.add(Group.objects.get(name=groupe))
    return user


def page(client, user, url=None):
    client.force_login(user)
    return client.get(url or reverse("admin:index")).content.decode()


def test_menu_defini_a_la_main_sans_liste_automatique():
    barre = settings.UNFOLD["SIDEBAR"]
    assert barre["show_all_applications"] is False
    titres = [str(g["title"]) for g in barre["navigation"]]
    assert titres == ["Mon stage", "Journal", "Données", "Références", "Administration"]
    assert all(g.get("collapsible") for g in barre["navigation"][1:])


def test_chaque_modele_de_l_admin_a_son_entree(db):
    liens = {str(i["link"]) for g in settings.UNFOLD["SIDEBAR"]["navigation"] for i in g["items"]}
    for modele in admin.site._registry:
        if modele._meta.app_label in ("carnet", "comptes", "auth"):
            url = reverse(f"admin:{modele._meta.app_label}_{modele._meta.model_name}_changelist")
            assert url in liens, f"{modele.__name__} absent du menu"


def test_apprenant_ne_voit_ni_utilisateurs_ni_codes(client):
    html = page(client, compte("awa", "Apprenant"))
    assert reverse("admin:carnet_stage_changelist") in html
    assert reverse("admin:auth_user_changelist") not in html
    assert reverse("admin:comptes_codeinvitation_changelist") not in html


def test_formateur_voit_ses_codes_mais_pas_les_utilisateurs(client):
    html = page(client, compte("prof", "Formateur"))
    assert reverse("admin:comptes_codeinvitation_changelist") in html
    assert reverse("admin:auth_user_changelist") not in html


def test_superutilisateur_voit_l_administration(client):
    html = page(client, User.objects.create_superuser("root", password="x"))
    assert reverse("admin:auth_user_changelist") in html
    assert reverse("admin:auth_group_changelist") in html


def test_deconnexion_dans_l_en_tete_de_l_admin(client):
    html = page(client, compte("awa", "Apprenant"))
    entete = html.split('id="header-inner"', 1)[1]
    assert DECONNEXION in entete
    assert "Se déconnecter" in entete


@pytest.mark.parametrize("nom_url", ["carnet:note_rapide", "carnet:tri_photos"])
def test_deconnexion_dans_les_pages_publiques(client, nom_url):
    from carnet.models import Stage
    import datetime

    awa = compte("awa", "Apprenant")
    Stage.objects.create(proprietaire=awa, intitule="S", date_debut=datetime.date(2026, 1, 5),
                         date_fin=datetime.date(2026, 3, 27))
    html = page(client, awa, reverse(nom_url))
    assert DECONNEXION in html
    assert "Se déconnecter" in html
