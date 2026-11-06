"""A39 : page d'accueil publique, avant la connexion."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_accueil_public_sans_connexion(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    contenu = reponse.content.decode()
    assert "Carnet de stage" in contenu
    assert f'href="{reverse("admin:login")}' in contenu
    assert "Se connecter" in contenu


@pytest.mark.django_db
def test_accueil_donne_le_compte_de_demonstration(client):
    contenu = client.get("/").content.decode()
    assert "demo.apprenant" in contenu and "demo-local-2026" in contenu


@pytest.mark.django_db
def test_accueil_renvoie_au_manuel(client):
    contenu = client.get("/").content.decode()
    assert "docs/manuel/manuel-utilisation.md" in contenu
    assert "docs/manuel/scenario-stage.md" in contenu


def test_accueil_n_expose_aucune_donnee_d_apprenant(client, stage):
    contenu = client.get("/").content.decode()
    assert stage.intitule not in contenu
    assert stage.apprenant_nom not in contenu if stage.apprenant_nom else True


def test_apprenant_connecte_va_directement_a_la_note_rapide(client, apprenant, stage):
    client.force_login(apprenant)
    reponse = client.get("/")
    assert reponse.status_code == 302
    assert reponse["Location"] == reverse("carnet:note_rapide")


@pytest.mark.django_db
def test_page_de_connexion_renvoie_a_l_accueil(client):
    contenu = client.get(reverse("admin:login")).content.decode()
    assert 'href="/"' in contenu
    assert "Découvrir le Carnet" in contenu


@pytest.mark.django_db
def test_accueil_sans_tiret_cadratin(client):
    """Charte éditoriale de la page : aucun tiret cadratin ni demi-cadratin visible."""
    contenu = client.get("/").content.decode()
    assert "—" not in contenu and "–" not in contenu
