"""US-40 : mot de passe oublié par courriel ; US-43 : verrou du compte démo (B4, B10)."""

import re

import pytest
from django.contrib.auth.models import User
from django.core import mail


@pytest.fixture(autouse=True)
def _courriel(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def awa(db):
    return User.objects.create_user("awa", email="awa@exemple.cm", password="Ancien-mot-de-passe-1")


def demander(client, courriel):
    return client.post("/mot-de-passe/", {"email": courriel})


def test_page_mot_de_passe_oublie_en_francais(client, db):
    reponse = client.get("/mot-de-passe/")
    assert reponse.status_code == 200
    assert "Mot de passe oublié" in reponse.content.decode()


def test_courriel_connu_recoit_un_lien_absolu(client, awa):
    reponse = demander(client, "AWA@exemple.cm")
    assert reponse["Location"] == "/mot-de-passe/envoye/"
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.to == ["awa@exemple.cm"]
    assert message.subject == "Réinitialisation de votre mot de passe du Carnet de stage"
    assert re.search(r"http://testserver/mot-de-passe/\S+/\S+/", message.body)


def test_reponse_identique_pour_un_courriel_inconnu(client, awa):
    reponse = demander(client, "inconnu@exemple.cm")
    assert reponse["Location"] == "/mot-de-passe/envoye/"
    assert mail.outbox == []


def test_lien_permet_de_choisir_un_nouveau_mot_de_passe(client, awa):
    demander(client, "awa@exemple.cm")
    lien = re.search(r"http://testserver(/mot-de-passe/\S+/\S+/)", mail.outbox[0].body).group(1)
    page = client.get(lien, follow=True)
    reponse = client.post(page.redirect_chain[-1][0], {
        "new_password1": "Nouveau-mot-de-passe-2", "new_password2": "Nouveau-mot-de-passe-2"})
    assert reponse["Location"] == "/mot-de-passe/termine/"
    awa.refresh_from_db()
    assert awa.check_password("Nouveau-mot-de-passe-2")


def test_lien_valable_24_heures(settings):
    assert settings.PASSWORD_RESET_TIMEOUT == 24 * 3600


def test_compte_demo_exclu_de_la_reinitialisation(client, db, settings):
    User.objects.create_user(settings.COMPTE_DEMO, email="demo@exemple.cm", password="demo-local-2026")
    reponse = demander(client, "demo@exemple.cm")
    assert reponse["Location"] == "/mot-de-passe/envoye/"
    assert mail.outbox == []
