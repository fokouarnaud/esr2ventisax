"""US-25, US-26 : indicateurs du tableau de bord et occupation globale du disque."""

import datetime

import pytest
from django.utils import timezone

from carnet.models import EntreeJournal, Photo, Rubrique
from carnet.services.tableau_de_bord import occupation_globale, rubriques_vides, sauvegarde, synthese_photos

D = datetime.date


def test_toutes_les_rubriques_entreprise_et_mission_vides_au_depart(stage):
    assert len(rubriques_vides(stage)) == 20


def test_rubrique_remplie_par_le_formulaire_n_est_plus_vide(stage):
    stage.fiche_entreprise.historique = "Créée en 2009."
    stage.fiche_entreprise.save()
    assert "entreprise.historique" not in rubriques_vides(stage)


def test_rubrique_alimentee_par_une_note_etiquetee_n_est_plus_vide(stage):
    note = EntreeJournal.objects.create(stage=stage, date=D(2026, 3, 3), texte="Le DG a fondé…")
    note.etiqueter([Rubrique.objects.get(code="mission.poste")])
    assert "mission.poste" not in rubriques_vides(stage)


def test_texte_fait_d_espaces_compte_comme_vide(stage):
    stage.mission.resultats = "   \n"
    stage.mission.save()
    assert "mission.resultats" in rubriques_vides(stage)


def _photo(stage, destination):
    return Photo.objects.create(stage=stage, fichier="x.jpg", destination=destination)


def test_synthese_photos_par_destination_et_alerte_corps(stage):
    for _ in range(26):
        _photo(stage, Photo.Destination.CORPS)
    _photo(stage, Photo.Destination.ANNEXE)
    synthese = synthese_photos(stage)
    assert synthese["par_destination"]["corps"] == 26
    assert synthese["par_destination"]["annexe"] == 1
    assert synthese["par_destination"]["a_trier"] == 0
    assert synthese["trop_dans_le_corps"] is True


def test_pas_d_alerte_a_25_photos_dans_le_corps(stage):
    for _ in range(25):
        _photo(stage, Photo.Destination.CORPS)
    assert synthese_photos(stage)["trop_dans_le_corps"] is False


def test_jamais_sauvegarde_est_en_alerte(stage):
    assert sauvegarde(stage) == {"jours": None, "alerte": True}


def test_sauvegarde_de_7_jours_sans_alerte_8_jours_en_alerte(stage):
    maintenant = timezone.now()
    stage.derniere_sauvegarde = maintenant - datetime.timedelta(days=7)
    assert sauvegarde(stage, maintenant) == {"jours": 7, "alerte": False}
    stage.derniere_sauvegarde = maintenant - datetime.timedelta(days=8)
    assert sauvegarde(stage, maintenant)["alerte"] is True


def test_occupation_globale_compte_tous_les_fichiers(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.bin").write_bytes(b"0" * 300)
    (tmp_path / "y.bin").write_bytes(b"0" * 200)
    occ = occupation_globale([tmp_path], total_octets=1000)
    assert occ == {"octets": 500, "ratio": 0.5, "alerte": False}


def test_occupation_globale_alerte_au_dela_de_80_pourcent(tmp_path):
    (tmp_path / "y.bin").write_bytes(b"0" * 801)
    assert occupation_globale([tmp_path], total_octets=1000)["alerte"] is True


def test_occupation_globale_ignore_un_dossier_absent(tmp_path):
    assert occupation_globale([tmp_path / "absent"], total_octets=1000)["octets"] == 0


def test_occupation_globale_compte_un_fichier_isole(tmp_path):
    base = tmp_path / "db.sqlite3"
    base.write_bytes(b"0" * 120)
    assert occupation_globale([base], total_octets=1000)["octets"] == 120
