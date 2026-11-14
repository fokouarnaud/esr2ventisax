"""Une note rattachée à une tâche le dit dans terrain.md, et le journal se filtre par tâche (US-14)."""

import datetime

import pytest

from carnet.admin import EntreeJournalAdmin
from carnet.models import EntreeJournal, Tache
from carnet.services.terrain_md import terrain_md

D = datetime.date


@pytest.mark.django_db
def test_terrain_md_indique_la_tache_de_la_note(stage):
    tache = Tache.objects.create(stage=stage, libelle="Canalisations étages hauts", date_debut=D(2026, 3, 16))
    EntreeJournal.objects.create(stage=stage, date=D(2026, 3, 18), texte="Soudure de 14 raccords au R+4",
                                 tache=tache)
    assert "  - Tâche : Canalisations étages hauts" in terrain_md(stage)


def test_journal_filtre_par_tache():
    assert "tache" in [f[0] if isinstance(f, tuple) else f for f in EntreeJournalAdmin.list_filter]


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/admin/carnet/entreejournal/", "/admin/carnet/photo/"])
def test_filtres_du_journal_cloisonnes(client, apprenant, autre_apprenant, stage, url):
    """Les filtres « tâche » et « rubrique » ne révèlent rien du stage d'un autre apprenant (A1)."""
    from carnet.models import Rubrique, Stage

    autre = Stage.objects.create(proprietaire=autre_apprenant, intitule="Autre", date_debut=D(2026, 3, 2),
                                 date_fin=D(2026, 6, 26))
    Tache.objects.create(stage=autre, libelle="Tâche secrète de Bruno", date_debut=D(2026, 3, 2))
    Rubrique.objects.create(stage=autre, code="secret", libelle="Chapitre secret de Bruno",
                            ordre=1)
    mienne = Tache.objects.create(stage=stage, libelle="Tâche d'Awa", date_debut=D(2026, 3, 2))
    EntreeJournal.objects.create(stage=stage, date=D(2026, 3, 3), texte="Note", tache=mienne)
    client.force_login(apprenant)
    page = client.get(url).content.decode()
    assert "secrète de Bruno" not in page and "secret de Bruno" not in page
