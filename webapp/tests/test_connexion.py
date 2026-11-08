"""US-39 : connexion unique et protégée, US-34 : déconnexion (B4, B6, B11)."""

import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse

from comptes.models import EchecConnexion, Profil

URL = "/connexion/"


@pytest.fixture
def awa(db):
    user = User.objects.create_user("awa", password="Bon-mot-de-passe-1", is_staff=True)
    user.groups.add(Group.objects.get_or_create(name="Apprenant")[0])
    return user


def test_page_connexion_publique(client, db):
    reponse = client.get(URL)
    contenu = reponse.content.decode()
    assert reponse.status_code == 200
    assert 'name="username"' in contenu and 'name="password"' in contenu
    assert reverse("comptes:inscription") in contenu
    assert reverse("comptes:mdp_oublie") in contenu


def test_login_url_pointe_vers_la_page_publique(settings):
    assert reverse(settings.LOGIN_URL) == URL


def test_connexion_reussie_mene_a_la_note_rapide(client, awa):
    reponse = client.post(URL, {"username": "awa", "password": "Bon-mot-de-passe-1"})
    assert reponse.status_code == 302
    assert reponse["Location"] == reverse("carnet:note_rapide")


def test_utilisateur_deja_connecte_est_redirige(client, awa):
    client.force_login(awa)
    assert client.get(URL)["Location"] == reverse("carnet:note_rapide")


def test_admin_login_redirige_en_gardant_next(client, db):
    reponse = client.get("/admin/login/?next=/admin/carnet/stage/")
    assert reponse.status_code == 302
    assert reponse["Location"] == "/connexion/?next=/admin/carnet/stage/"


def test_admin_sans_session_mene_a_la_connexion_publique(client, db):
    reponse = client.get("/admin/", follow=True)
    assert reponse.redirect_chain[-1][0].startswith(URL)


def test_next_est_respecte(client, awa):
    reponse = client.post(URL + "?next=/admin/", {"username": "awa", "password": "Bon-mot-de-passe-1"})
    assert reponse["Location"] == "/admin/"


def test_compte_non_verifie_refuse_avec_message_generique(client, db):
    user = User.objects.create_user("zoe", password="Bon-mot-de-passe-1", is_active=False)
    Profil.objects.filter(user=user).update(inscrit_par_formulaire=True)
    reponse = client.post(URL, {"username": "zoe", "password": "Bon-mot-de-passe-1"})
    assert reponse.status_code == 200
    assert "_auth_user_id" not in client.session


def test_blocage_apres_5_echecs_meme_avec_le_bon_mot_de_passe(client, awa):
    for _ in range(5):
        client.post(URL, {"username": "AWA", "password": "faux"})
    reponse = client.post(URL, {"username": "awa", "password": "Bon-mot-de-passe-1"})
    assert reponse.status_code == 200
    assert reponse.context["form"].verrouille is True
    assert "_auth_user_id" not in client.session


def test_blocage_identique_pour_un_identifiant_inexistant(client, db):
    for _ in range(5):
        client.post(URL, {"username": "fantome", "password": "faux"})
    reponse = client.post(URL, {"username": "fantome", "password": "faux"})
    assert reponse.context["form"].verrouille is True


def test_reussite_remet_le_compteur_a_zero(client, awa):
    for _ in range(4):
        client.post(URL, {"username": "awa", "password": "faux"})
    client.post(URL, {"username": "awa", "password": "Bon-mot-de-passe-1"})
    assert EchecConnexion.objects.filter(identifiant="awa").count() == 0


def test_echecs_anciens_ne_bloquent_plus(client, awa, settings):
    import datetime

    settings.LOGIN_BLOCAGE = datetime.timedelta(seconds=0)
    for _ in range(5):
        client.post(URL, {"username": "awa", "password": "faux"})
    reponse = client.post(URL, {"username": "awa", "password": "Bon-mot-de-passe-1"})
    assert reponse.status_code == 302


def test_compte_connecte_sans_acces_admin_ne_boucle_pas(client, db):
    sans_admin = User.objects.create_user("lea", password="x")  # ni is_staff ni superutilisateur
    client.force_login(sans_admin)
    reponse = client.get("/admin/", follow=True)
    assert reponse.status_code == 403
    contenu = reponse.content.decode()
    assert "pas accès à l'administration" in contenu
    assert reverse("comptes:deconnexion") in contenu


# --- US-34 : déconnexion (POST seulement, retour à l'accueil) ---

def test_deconnexion_en_post_ramene_a_l_accueil(client, awa):
    client.force_login(awa)
    reponse = client.post("/deconnexion/")
    assert reponse.status_code == 302 and reponse["Location"] == "/"
    assert "_auth_user_id" not in client.session


def test_deconnexion_refuse_get(client, awa):
    client.force_login(awa)
    assert client.get("/deconnexion/").status_code == 405
    assert "_auth_user_id" in client.session
