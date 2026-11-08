"""A39 : page d'accueil publique, avant la connexion."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_accueil_public_sans_connexion(client):
    reponse = client.get("/")
    assert reponse.status_code == 200
    contenu = reponse.content.decode()
    assert "Carnet de stage" in contenu
    assert f'href="{reverse("comptes:connexion")}' in contenu
    assert "Se connecter" in contenu


@pytest.mark.django_db
def test_accueil_propose_l_inscription_avec_un_code(client):
    contenu = client.get("/").content.decode()
    assert f'href="{reverse("comptes:inscription")}' in contenu
    assert "Créer un compte" in contenu
    assert "pas d'inscription libre" not in contenu
    assert "code d'invitation" in contenu


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
    contenu = client.get(reverse("comptes:connexion")).content.decode()
    assert 'href="/"' in contenu
    assert "Découvrir le Carnet" in contenu


@pytest.mark.django_db
def test_accueil_sans_tiret_cadratin(client):
    """Charte éditoriale de la page : aucun tiret cadratin ni demi-cadratin visible."""
    contenu = client.get("/").content.decode()
    assert "—" not in contenu and "–" not in contenu


# --- Fiches de formation publiées sur l'accueil (A40) -------------------------------------------

import datetime

from django.contrib.staticfiles import finders

from carnet.formation import FICHES, fiche_a_la_une


def test_chaque_fiche_a_son_pdf_et_sa_couverture():
    for fiche in FICHES:
        assert finders.find(fiche.pdf), fiche.pdf
        assert finders.find(fiche.couverture), fiche.couverture


@pytest.mark.parametrize("jour, numero", [
    (datetime.date(2026, 11, 6), 1),   # veille du premier samedi
    (datetime.date(2026, 11, 7), 1),   # le jour même
    (datetime.date(2026, 11, 8), 2),
    (datetime.date(2026, 11, 21), 3),
    (datetime.date(2026, 11, 22), 4),
])
def test_la_fiche_a_la_une_est_celle_du_prochain_samedi(jour, numero):
    assert fiche_a_la_une(jour).numero == numero


def test_apres_la_derniere_fiche_publiee_la_derniere_reste_a_la_une():
    lendemain = FICHES[-1].date + datetime.timedelta(days=1)
    assert fiche_a_la_une(lendemain) == FICHES[-1]


@pytest.mark.django_db
def test_accueil_propose_les_fiches_a_telecharger(client):
    contenu = client.get("/").content.decode()
    assert "Se former, samedi après samedi" in contenu
    for fiche in FICHES:
        assert f"carnet/formation/samedi-{fiche.numero:02d}" in contenu and ".pdf" in contenu
    assert contenu.count("Télécharger la fiche") == len(FICHES)
