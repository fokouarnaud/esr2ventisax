"""B15 à B18 : droits portés par le profil, plus de compte formateur, l'accueil guide le premier pas."""

import importlib
import io
import json
import zipfile

import pytest
from django.apps import apps
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse

from carnet.models import EntreeJournal, Stage
from comptes.models import Profil


@pytest.fixture(autouse=True)
def groupes(db):
    call_command("creer_groupes")


def compte(nom, role, **extra):
    user = User.objects.create_user(nom, password="x", **extra)
    user.profil.role = role
    user.profil.save()
    return user


# --- B15 : le profil porte les droits ---

def test_deux_profils_seulement():
    assert [r for r, _ in Profil.Role.choices] == ["apprenant", "administrateur"]


@pytest.mark.parametrize("role, groupes_attendus, superuser", [
    (Profil.Role.APPRENANT, ["Apprenant"], False),
    (Profil.Role.ADMINISTRATEUR, [], True),
])
def test_le_role_du_profil_regle_groupes_et_statuts(db, role, groupes_attendus, superuser):
    user = compte("zoe", role)
    user.refresh_from_db()
    assert sorted(user.groups.values_list("name", flat=True)) == groupes_attendus
    assert (user.is_staff, user.is_superuser) == (True, superuser)


def test_retrograder_un_administrateur(db):
    user = compte("zoe", Profil.Role.ADMINISTRATEUR)
    user.profil.role = Profil.Role.APPRENANT
    user.profil.save()
    user.refresh_from_db()
    assert user.is_superuser is False
    assert list(user.groups.values_list("name", flat=True)) == ["Apprenant"]


def test_role_par_defaut_apprenant(db):
    assert User.objects.create_user("lea", password="x").profil.role == Profil.Role.APPRENANT


def etat_historique():
    """Modèles tels que la migration les voit (sans Profil.save() personnalisé)."""
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    return MigrationExecutor(connection).loader.project_state(("comptes", "0004_role_depuis_les_droits")).apps


def test_migration_deduit_le_role_et_fait_des_anciens_formateurs_des_apprenants(db):
    migration = importlib.import_module("comptes.migrations.0004_role_depuis_les_droits")
    racine = User.objects.create_superuser("root", password="x")
    ancien_prof = User.objects.create_user("prof", password="x", is_staff=True)
    ancien_prof.groups.add(Group.objects.get_or_create(name="Formateur")[0])
    Profil.objects.filter(user=racine).update(role=Profil.Role.APPRENANT)
    migration.role_depuis_les_droits(etat_historique(), None)
    assert Profil.objects.get(user=racine).role == Profil.Role.ADMINISTRATEUR
    assert Profil.objects.get(user=ancien_prof).role == Profil.Role.APPRENANT
    assert list(User.objects.get(pk=ancien_prof.pk).groups.values_list("name", flat=True)) == ["Apprenant"]


def test_migration_applique_les_droits_du_profil(db):
    migration = importlib.import_module("comptes.migrations.0004_role_depuis_les_droits")
    sans_droits = User.objects.create_user("lea", password="x")  # ni groupe ni statut équipe
    migration.role_depuis_les_droits(etat_historique(), None)
    sans_droits.refresh_from_db()
    assert sans_droits.is_staff is True
    assert list(sans_droits.groups.values_list("name", flat=True)) == ["Apprenant"]


def test_creer_groupes_supprime_le_groupe_formateur(db):
    Group.objects.get_or_create(name="Formateur")
    call_command("creer_groupes")
    assert not Group.objects.filter(name="Formateur").exists()
    assert Group.objects.filter(name="Apprenant").exists()


def test_admin_utilisateur_un_seul_champ_profil(client, db):
    racine = compte("root", Profil.Role.ADMINISTRATEUR)
    client.force_login(racine)
    for url in (reverse("admin:auth_user_add"), reverse("admin:auth_user_change", args=[racine.pk])):
        html = client.get(url).content.decode()
        assert 'name="role"' in html, url
        for interdit in ('name="groups"', 'name="user_permissions"', 'name="is_staff"', 'name="is_superuser"'):
            assert interdit not in html, (url, interdit)
        assert "Formateur" not in html, url


@pytest.mark.parametrize("role, superuser", [(Profil.Role.APPRENANT, False), (Profil.Role.ADMINISTRATEUR, True)])
def test_admin_ajoute_un_utilisateur_avec_son_profil(client, db, role, superuser):
    client.force_login(compte("root", Profil.Role.ADMINISTRATEUR))
    reponse = client.post(reverse("admin:auth_user_add"), {
        "username": "nouveau", "password1": "Mot-de-passe-solide-9", "password2": "Mot-de-passe-solide-9",
        "role": role, "usable_password": "true"})
    assert reponse.status_code == 302
    user = User.objects.get(username="nouveau")
    assert (user.profil.role, user.is_staff, user.is_superuser) == (role, True, superuser)


def test_admin_change_le_profil_d_un_utilisateur(client, db):
    racine = compte("root", Profil.Role.ADMINISTRATEUR)
    eleve = compte("eleve", Profil.Role.APPRENANT)
    client.force_login(racine)
    reponse = client.post(reverse("admin:auth_user_change", args=[eleve.pk]), {
        "username": "eleve", "role": Profil.Role.ADMINISTRATEUR, "is_active": "on"})
    assert reponse.status_code == 302, reponse.context["adminform"].form.errors
    eleve.refresh_from_db()
    assert eleve.profil.role == Profil.Role.ADMINISTRATEUR and eleve.is_superuser


# --- B16 : connexion selon le profil ---

@pytest.mark.parametrize("role, destination", [
    (Profil.Role.APPRENANT, "carnet:note_rapide"),
    (Profil.Role.ADMINISTRATEUR, "admin:index"),
])
def test_destination_apres_connexion(client, db, role, destination):
    compte("u", role)
    reponse = client.post(reverse("comptes:connexion"), {"username": "u", "password": "x"})
    assert reponse["Location"] == reverse(destination)


# --- B17 : plus de compte formateur ---

def test_plus_de_champs_formateur_dans_les_modeles():
    assert "formateur_referent" not in [f.name for f in Stage._meta.get_fields()]
    assert "remarque_formateur" not in [f.name for f in EntreeJournal._meta.get_fields()]


def test_un_ancien_zip_avec_des_champs_formateur_se_restaure(db):
    from carnet.services.export import restaurer

    proprio = compte("awa", Profil.Role.APPRENANT)
    terrain = [{"model": "carnet.stage", "pk": "8a2c1f0e-3b4d-4c5e-9f60-7a8b9c0d1e2f", "fields": {
        "proprietaire": 999, "formateur_referent": 12, "intitule": "Ancien stage",
        "date_debut": "2026-03-02", "date_fin": "2026-06-26", "quota_mo": 80,
        "cree_le": "2026-03-01T08:00:00Z", "modifie_le": "2026-03-01T08:00:00Z"}}]
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w") as z:
        z.writestr("terrain.json", json.dumps(terrain))
    with zipfile.ZipFile(tampon) as z:
        stage = restaurer(z, proprio)
    assert stage.intitule == "Ancien stage" and stage.proprietaire == proprio


def test_inscription_sans_case_de_partage(client, db):
    html = client.get(reverse("comptes:inscription")).content.decode()
    assert "partage" not in html and "formateur" not in html.lower()


def test_plus_de_codes_d_invitation():
    from django.apps import apps as registre
    assert "codeinvitation" not in [m._meta.model_name for m in registre.get_app_config("comptes").get_models()]
    assert "code_utilise" not in [f.name for f in Profil._meta.get_fields()]


def test_premier_stage_message_explicite(client, db):
    client.force_login(compte("awa", Profil.Role.APPRENANT))
    reponse = client.get(reverse("carnet:note_rapide"), follow=True)
    assert "et les dates sont obligatoires, le reste se complète au fil du stage" in reponse.content.decode()


def test_couverture_explique_le_responsable_academique(client, db):
    client.force_login(compte("awa", Profil.Role.APPRENANT))
    champ = client.get(reverse("admin:carnet_stage_add")).context["adminform"].form.fields["tuteur_acad"]
    assert "formateur" in str(champ.help_text).lower() and "rapport" in str(champ.help_text)
    assert str(champ.label).startswith("Formateur")  # le formateur n'est plus qu'un libellé saisi librement


# --- B18 : l'accueil guide le premier pas ---

def test_accueil_par_ou_commencer(client, db):
    html = client.get("/").content.decode()
    assert 'id="commencer"' in html
    heros = html.split('class="heros__actions"', 1)[1].split("</div>", 1)[0]
    assert "#commencer" in heros and reverse("comptes:connexion") in heros
    commencer = html.split('id="commencer"', 1)[1].split("</section>", 1)[0]
    assert reverse("comptes:inscription") in commencer
    assert "code" not in commencer.lower()
    assert "formateur référent" not in html and "Le formateur référent" not in html


def test_libelles_des_logos_de_la_couverture():
    assert Stage._meta.get_field("logo_cfp").verbose_name == "logo du CFP"
    assert Stage._meta.get_field("logo_entreprise").verbose_name == "logo de l'entreprise"
