"""US-24 : jours travaillés, absences, fériés, jours sans note, taux de présence (A30).

Semaine de référence : lundi 27/04/2026 → samedi 02/05/2026 ; le 1er mai 2026 est un vendredi (férié fixe).
"""

import datetime

import pytest

from carnet.models import Absence, EntreeJournal, Stage
from carnet.services.calendrier import jours_prevus, jours_sans_note, taux_presence

D = datetime.date


@pytest.fixture
def semaine(apprenant):
    return Stage.objects.create(proprietaire=apprenant, intitule="S", date_debut=D(2026, 4, 27), date_fin=D(2026, 5, 2))


def test_feries_fixes_du_cameroun_precharges(db):
    assert Absence.objects.filter(stage__isnull=True, motif=Absence.Motif.FERIE).count() == 6


def test_jours_prevus_excluent_le_1er_mai(semaine):
    assert jours_prevus(semaine) == [D(2026, 4, 27), D(2026, 4, 28), D(2026, 4, 29), D(2026, 4, 30), D(2026, 5, 2)]


def test_jours_prevus_respectent_les_jours_travailles(semaine):
    semaine.jours_travailles = [0, 1, 2, 3, 4]  # sans le samedi
    assert D(2026, 5, 2) not in jours_prevus(semaine)


def test_ferie_mobile_du_stage_exclu(semaine):
    Absence.objects.create(stage=semaine, date_debut=D(2026, 4, 29), date_fin=D(2026, 4, 29), motif=Absence.Motif.FERIE)
    assert D(2026, 4, 29) not in jours_prevus(semaine)


def test_taux_de_presence_avec_un_jour_de_maladie(semaine):
    Absence.objects.create(stage=semaine, date_debut=D(2026, 4, 28), date_fin=D(2026, 4, 28), motif=Absence.Motif.MALADIE)
    assert taux_presence(semaine) == pytest.approx(4 / 5)


def test_jours_sans_note_ignorent_absences_et_feries(semaine):
    Absence.objects.create(stage=semaine, date_debut=D(2026, 4, 28), date_fin=D(2026, 4, 28), motif=Absence.Motif.MALADIE)
    for jour in (D(2026, 4, 27), D(2026, 4, 30)):
        EntreeJournal.objects.create(stage=semaine, date=jour, texte="x")
    assert jours_sans_note(semaine, jusqu_au=D(2026, 5, 2)) == [D(2026, 4, 29), D(2026, 5, 2)]


def test_jours_sans_note_s_arretent_a_aujourd_hui(semaine):
    assert jours_sans_note(semaine, jusqu_au=D(2026, 4, 28)) == [D(2026, 4, 27), D(2026, 4, 28)]


def test_absence_d_un_autre_stage_ignoree(semaine, autre_apprenant):
    autre = Stage.objects.create(proprietaire=autre_apprenant, intitule="B", date_debut=semaine.date_debut,
                                 date_fin=semaine.date_fin)
    Absence.objects.create(stage=autre, date_debut=D(2026, 4, 28), date_fin=D(2026, 4, 28), motif=Absence.Motif.MALADIE)
    assert taux_presence(semaine) == 1.0
