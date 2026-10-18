"""US-04 (stage actif), US-25 (agrégat des indicateurs), US-28 (commande restaurer_dossier)."""

import datetime

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import RequestFactory

from carnet.models import EntreeJournal, Stage
from carnet.services.export import ecrire_zip
from carnet.services.stage_actif import choisir_stage_actif, stage_actif
from carnet.services.tableau_de_bord import indicateurs


def requete(user):
    r = RequestFactory().get("/")
    SessionMiddleware(lambda _: None).process_request(r)
    r.user = user
    return r


@pytest.fixture
def second_stage(apprenant):
    return Stage.objects.create(proprietaire=apprenant, intitule="Second", date_debut=datetime.date(2026, 7, 1),
                                date_fin=datetime.date(2026, 8, 1))


# --- Stage actif (US-04) ------------------------------------------------------------

def test_sans_choix_le_stage_le_plus_recent_est_actif(stage, second_stage, apprenant):
    assert stage_actif(requete(apprenant)) == second_stage


def test_le_choix_est_memorise_en_session(stage, second_stage, apprenant):
    r = requete(apprenant)
    choisir_stage_actif(r, stage)
    assert stage_actif(r) == stage


def test_impossible_de_choisir_le_stage_d_un_autre(stage, autre_apprenant):
    with pytest.raises(PermissionDenied):
        choisir_stage_actif(requete(autre_apprenant), stage)


def test_session_pointant_vers_un_stage_supprime(stage, second_stage, apprenant):
    r = requete(apprenant)
    choisir_stage_actif(r, stage)
    stage.delete()
    assert stage_actif(r) == second_stage


def test_aucun_stage(apprenant):
    assert stage_actif(requete(apprenant)) is None


# --- Indicateurs (US-25) ----------------------------------------------------------

def test_indicateurs_compte_les_notes_non_completees(stage):
    EntreeJournal.objects.create(stage=stage, date=stage.date_debut, texte="a")
    EntreeJournal.objects.create(stage=stage, date=stage.date_debut, texte="b", completee=True)
    resultat = indicateurs(stage, aujourd_hui=datetime.date(2026, 3, 3))
    assert resultat["notes_non_completees"] == 1
    assert resultat["jours_sans_note"] == [datetime.date(2026, 3, 3)]  # le 2 a une note
    assert resultat["quota"]["quota_mo"] == 80
    assert len(resultat["rubriques_vides"]) == 20


# --- Commande restaurer_dossier (US-28) ----------------------------------------------

def test_commande_restaurer_dossier(stage, apprenant, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"
    chemin = tmp_path / "d.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    pk = stage.pk
    stage.delete()
    call_command("restaurer_dossier", str(chemin), "--proprietaire", "awa")
    assert Stage.objects.get(pk=pk).proprietaire == apprenant
