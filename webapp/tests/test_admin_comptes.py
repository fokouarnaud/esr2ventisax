"""US-32 (utilisateurs dans Unfold), US-41 (codes du formateur), US-43 (verrou démo) — B7, B10, B12."""

import pytest
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.forms import UserChangeForm, UserCreationForm

from comptes.models import CodeInvitation


@pytest.fixture(autouse=True)
def groupes(db):
    call_command("creer_groupes")


def compte(nom, groupe=None, **extra):
    user = User.objects.create_user(nom, password="x", is_staff=True, **extra)
    if groupe:
        user.groups.add(Group.objects.get(name=groupe))
    return user


@pytest.fixture
def racine(db):
    return User.objects.create_superuser("root", password="x")


@pytest.fixture
def prof_a(db):
    return compte("prof.a", "Formateur")


@pytest.fixture
def prof_b(db):
    return compte("prof.b", "Formateur")


@pytest.fixture
def awa(db):
    return compte("awa", "Apprenant")


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


def test_bouton_ajouter_libelle_pour_les_codes(client, prof_a):
    client.force_login(prof_a)
    contenu = client.get(reverse("admin:comptes_codeinvitation_changelist")).content.decode()
    assert ">Ajouter un code</span>" in contenu


def test_colonnes_et_filtres_de_la_liste(racine):
    modele_admin = admin.site._registry[User]
    for colonne in ("username", "nom_complet", "email", "groupe", "courriel_verifie", "is_active",
                    "date_joined", "code_utilise"):
        assert colonne in modele_admin.list_display
    assert {"groups", "is_active", "profil__email_verifie"} <= set(modele_admin.list_filter)


def test_liste_affiche_le_groupe_et_le_code(client, racine, prof_a):
    code = CodeInvitation.objects.create(formateur=prof_a, code="ABCDEFGH")
    eleve = compte("eleve", "Apprenant")
    eleve.profil.code_utilise = code
    eleve.profil.save()
    client.force_login(racine)
    contenu = client.get(reverse("admin:auth_user_changelist")).content.decode()
    assert "ABCDEFGH" in contenu and "Apprenant" in contenu


@pytest.mark.parametrize("groupe", ["Apprenant", "Formateur"])
def test_ajout_avec_choix_du_groupe_regle_is_staff(client, racine, groupe):
    client.force_login(racine)
    reponse = client.post(reverse("admin:auth_user_add"), {
        "username": "nouveau", "password1": "Mot-de-passe-solide-9", "password2": "Mot-de-passe-solide-9",
        "groupe": groupe, "usable_password": "true",
    })
    assert reponse.status_code == 302, reponse.context["adminform"].form.errors if reponse.context else reponse
    user = User.objects.get(username="nouveau")
    assert user.is_staff is True
    assert list(user.groups.values_list("name", flat=True)) == [groupe]


@pytest.mark.parametrize("nom", ["awa", "prof_a"])
def test_utilisateurs_interdits_aux_apprenants_et_formateurs(client, request, nom):
    client.force_login(request.getfixturevalue(nom))
    assert client.get(reverse("admin:auth_user_changelist")).status_code == 403
    assert client.get(reverse("admin:auth_group_changelist")).status_code == 403


# --- US-41 : codes du formateur ---

def test_formateur_ne_voit_que_ses_codes(client, prof_a, prof_b):
    a = CodeInvitation.objects.create(formateur=prof_a, code="AAAAAAAA")
    b = CodeInvitation.objects.create(formateur=prof_b, code="BBBBBBBB")
    client.force_login(prof_a)
    contenu = client.get(reverse("admin:comptes_codeinvitation_changelist")).content.decode()
    assert "AAAAAAAA" in contenu and "BBBBBBBB" not in contenu
    assert client.get(reverse("admin:comptes_codeinvitation_change", args=[b.pk])).status_code == 404
    assert client.get(reverse("admin:comptes_codeinvitation_change", args=[a.pk])).status_code == 200


def test_formateur_cree_un_code_a_son_nom(client, prof_a, prof_b):
    client.force_login(prof_a)
    reponse = client.post(reverse("admin:comptes_codeinvitation_add"), {
        "usages_max": 5, "expire_le_0": "2027-02-01", "expire_le_1": "12:00:00", "actif": "on",
        "formateur": prof_b.pk,  # ignoré : un formateur ne crée que pour lui-même
    })
    assert reponse.status_code == 302
    code = CodeInvitation.objects.get()
    assert code.formateur == prof_a
    assert len(code.code) == 8


def test_superutilisateur_voit_tout_et_choisit_le_formateur(client, racine, prof_a, prof_b):
    CodeInvitation.objects.create(formateur=prof_a, code="AAAAAAAA")
    CodeInvitation.objects.create(formateur=prof_b, code="BBBBBBBB")
    client.force_login(racine)
    contenu = client.get(reverse("admin:comptes_codeinvitation_changelist")).content.decode()
    assert "AAAAAAAA" in contenu and "BBBBBBBB" in contenu
    client.post(reverse("admin:comptes_codeinvitation_add"), {
        "formateur": prof_b.pk, "usages_max": 3, "expire_le_0": "2027-02-01", "expire_le_1": "12:00:00",
        "actif": "on"})
    assert CodeInvitation.objects.filter(formateur=prof_b, usages_max=3).exists()


def test_apprenant_n_a_pas_acces_aux_codes(client, awa):
    client.force_login(awa)
    assert client.get(reverse("admin:comptes_codeinvitation_changelist")).status_code == 403


@pytest.mark.parametrize("action, avant, apres", [
    ("desactiver", {"actif": True}, {"actif": False}),
    ("activer", {"actif": False}, {"actif": True}),
])
def test_actions_activer_desactiver(client, prof_a, action, avant, apres):
    code = CodeInvitation.objects.create(formateur=prof_a, code="AAAAAAAA", **avant)
    client.force_login(prof_a)
    client.post(reverse("admin:comptes_codeinvitation_changelist"),
                {"action": action, "_selected_action": [str(code.pk)]})
    code.refresh_from_db()
    assert code.actif is apres["actif"]


def test_action_regenerer_change_le_code_et_remet_les_usages(client, prof_a):
    code = CodeInvitation.objects.create(formateur=prof_a, code="AAAAAAAA", usages=5)
    client.force_login(prof_a)
    client.post(reverse("admin:comptes_codeinvitation_changelist"),
                {"action": "regenerer", "_selected_action": [str(code.pk)]})
    code.refresh_from_db()
    assert code.code != "AAAAAAAA" and code.usages == 0


def test_action_d_un_formateur_sans_effet_sur_le_code_d_un_autre(client, prof_a, prof_b):
    autre = CodeInvitation.objects.create(formateur=prof_b, code="BBBBBBBB")
    client.force_login(prof_a)
    client.post(reverse("admin:comptes_codeinvitation_changelist"),
                {"action": "desactiver", "_selected_action": [str(autre.pk)]})
    autre.refresh_from_db()
    assert autre.actif is True


def test_colonnes_des_codes(prof_a):
    colonnes = admin.site._registry[CodeInvitation].list_display
    for c in ("code", "usages_sur_max", "expire_le", "actif", "nombre_inscrits"):
        assert c in colonnes


# --- US-43 : verrou du compte démo ---

def test_compte_demo_ne_peut_pas_changer_son_mot_de_passe(client, settings):
    demo = compte(settings.COMPTE_DEMO, "Apprenant")
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
