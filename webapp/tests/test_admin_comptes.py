"""US-32 (utilisateurs dans Unfold), US-43 (verrou démo) — B10, B12, B15, B19 (plus de codes)."""

import pytest
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm


@pytest.fixture(autouse=True)
def groupes(db):
    call_command("creer_groupes")


@pytest.fixture
def racine(db):
    return User.objects.create_superuser("root", password="x")


@pytest.fixture
def awa(db):
    user = User.objects.create_user("awa", password="x")
    user.profil.save()  # profil Apprenant : droits appliqués
    return user


# --- US-32 ---

def test_user_et_group_utilisent_les_classes_unfold():
    assert isinstance(admin.site._registry[User], UnfoldModelAdmin)
    assert isinstance(admin.site._registry[Group], UnfoldModelAdmin)
    assert issubclass(admin.site._registry[User].form, UserChangeForm)
    assert issubclass(admin.site._registry[User].add_form, UserCreationForm)


def test_liste_des_utilisateurs_a_un_bouton_ajouter(client, racine):
    client.force_login(racine)
    contenu = client.get(reverse("admin:auth_user_changelist")).content.decode()
    assert reverse("admin:auth_user_add") in contenu
    assert ">Ajouter un utilisateur</span>" in contenu  # libellé visible, pas seulement une icône « + »


def test_colonnes_et_filtres_de_la_liste():
    modele_admin = admin.site._registry[User]
    for colonne in ("username", "nom_complet", "email", "profil_role", "courriel_verifie", "is_active",
                    "date_joined"):
        assert colonne in modele_admin.list_display
    assert {"profil__role", "is_active", "profil__email_verifie"} <= set(modele_admin.list_filter)


def test_liste_affiche_le_profil(client, racine, awa):
    client.force_login(racine)
    contenu = client.get(reverse("admin:auth_user_changelist")).content.decode()
    assert "Apprenant" in contenu and "Administrateur" in contenu


def test_utilisateurs_interdits_aux_apprenants(client, awa):
    client.force_login(awa)
    assert client.get(reverse("admin:auth_user_changelist")).status_code == 403
    assert client.get(reverse("admin:auth_group_changelist")).status_code == 403


# --- US-43 : verrou du compte démo ---

def test_compte_demo_ne_peut_pas_changer_son_mot_de_passe(client, settings):
    demo = User.objects.create_user(settings.COMPTE_DEMO, password="x")
    demo.profil.save()
    client.force_login(demo)
    assert client.get(reverse("admin:password_change")).status_code == 403
    reponse = client.post(reverse("admin:password_change"), {
        "old_password": "x", "new_password1": "Pirate-mot-de-passe-1", "new_password2": "Pirate-mot-de-passe-1"})
    assert reponse.status_code == 403
    demo.refresh_from_db()
    assert demo.check_password("x")


def test_autre_apprenant_peut_changer_son_mot_de_passe(client, awa):
    client.force_login(awa)
    assert client.get(reverse("admin:password_change")).status_code == 200
