"""US-10, US-11, US-14, US-20 à US-23 : journal et entités rattachées."""

import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from carnet.models import (
    Abreviation, DonneeTechnique, EntreeJournal, Personne, Reference, Rubrique, Stage, Tache,
)


@pytest.fixture
def entree(stage):
    return EntreeJournal.objects.create(stage=stage, date=datetime.date(2026, 3, 3), texte="Pose du PER")


# --- Note rapide et complétion (US-10, US-11) --------------------------------

def test_une_note_rapide_n_est_pas_completee(entree):
    assert entree.completee is False


def test_plusieurs_notes_le_meme_jour(stage, entree):
    EntreeJournal.objects.create(stage=stage, date=entree.date, texte="Essai d'étanchéité")
    assert EntreeJournal.objects.filter(stage=stage, date=entree.date).count() == 2


# --- Étiquetage (US-12, US-14) -----------------------------------------------

def test_etiqueter_avec_rubrique_du_cours_et_chapitre_du_stage(stage, entree):
    chapitre = Rubrique.objects.create(stage=stage, libelle="Mode opératoire", partie=Rubrique.Partie.THEME)
    historique = Rubrique.objects.get(code="entreprise.historique")
    entree.etiqueter([chapitre, historique])
    assert set(entree.rubriques.all()) == {chapitre, historique}


def test_etiqueter_avec_le_chapitre_d_un_autre_stage_est_refuse(stage, entree, autre_apprenant):
    autre = Stage.objects.create(proprietaire=autre_apprenant, intitule="B",
                                 date_debut=stage.date_debut, date_fin=stage.date_fin)
    etranger = Rubrique.objects.create(stage=autre, libelle="X", partie=Rubrique.Partie.THEME)
    with pytest.raises(ValidationError):
        entree.etiqueter([etranger])
    assert entree.rubriques.count() == 0


# --- Tâches (US-23) -----------------------------------------------------------

def test_tache_sans_fin_s_arrete_a_la_fin_du_stage(stage):
    t = Tache.objects.create(stage=stage, libelle="Colonne montante", date_debut=datetime.date(2026, 4, 1))
    assert t.fin_effective == datetime.date(2026, 6, 26)


def test_tache_finissant_avant_de_commencer_est_refusee(stage):
    t = Tache(stage=stage, libelle="X", date_debut=datetime.date(2026, 4, 2), date_fin=datetime.date(2026, 4, 1))
    with pytest.raises(ValidationError):
        t.full_clean()


# --- Personnes (US-22) --------------------------------------------------------

def test_personne_non_publiable_exportee_par_sa_fonction(stage):
    p = Personne(stage=stage, nom="M. Ekotto", fonction="chef de chantier", nom_publiable=False)
    assert p.nom_exporte == "le chef de chantier"


def test_personne_publiable_exportee_par_son_nom(stage):
    p = Personne(stage=stage, nom="M. Ekotto", fonction="chef de chantier")
    assert p.nom_exporte == "M. Ekotto"


# --- Références et données techniques (US-20, US-21) --------------------------

def test_cle_bibtex_generee_auteur_annee(stage):
    r = Reference.objects.create(stage=stage, auteur="AFNOR", titre="NF DTU 60.11 P1-1", annee=2013)
    assert r.cle_bibtex == "afnor2013"


def test_cle_bibtex_unique_par_stage(stage):
    Reference.objects.create(stage=stage, auteur="Ndjock, Paul", titre="A", annee=2020)
    r2 = Reference.objects.create(stage=stage, auteur="Ndjock, Paul", titre="B", annee=2020)
    assert r2.cle_bibtex == "ndjock2020b"


def test_cle_bibtex_sans_auteur_ni_annee(stage):
    r = Reference.objects.create(stage=stage, titre="Guide Armaflex")
    assert r.cle_bibtex == "guide"


def test_valeur_de_reference_sans_source_refusee(stage):
    d = DonneeTechnique(stage=stage, grandeur="Débit de base lavabo", valeur=Decimal("0.20"), unite="L/s",
                        nature=DonneeTechnique.Nature.REFERENCE, date=datetime.date(2026, 3, 3))
    with pytest.raises(ValidationError) as exc:
        d.full_clean()
    assert "reference" in exc.value.message_dict


def test_releve_sans_note_de_journal_refuse(stage):
    d = DonneeTechnique(stage=stage, grandeur="Pression", valeur=Decimal("3.5"), unite="bar",
                        nature=DonneeTechnique.Nature.RELEVE, date=datetime.date(2026, 3, 3))
    with pytest.raises(ValidationError) as exc:
        d.full_clean()
    assert "entree" in exc.value.message_dict


def test_releve_rattache_a_une_note_accepte(stage, entree):
    d = DonneeTechnique(stage=stage, grandeur="Pression", valeur=Decimal("3.5"), unite="bar",
                        nature=DonneeTechnique.Nature.RELEVE, date=entree.date, entree=entree)
    d.full_clean()


def _donnee_sourcee(stage):
    ref = Reference.objects.create(stage=stage, auteur="AFNOR", titre="DTU", annee=2013)
    DonneeTechnique.objects.create(stage=stage, grandeur="Débit", valeur=Decimal("0.2"), unite="L/s",
                                   nature=DonneeTechnique.Nature.REFERENCE, date=datetime.date(2026, 3, 3),
                                   reference=ref)
    return ref


def test_supprimer_une_reference_encore_citee_est_refuse(stage):
    from django.db.models import RestrictedError

    ref = _donnee_sourcee(stage)
    with pytest.raises(RestrictedError):
        ref.delete()


def test_supprimer_un_stage_avec_donnees_sourcees(stage):
    _donnee_sourcee(stage)
    stage.delete()
    assert DonneeTechnique.objects.count() == 0


# --- Abréviations -------------------------------------------------------------

def test_sigle_unique_par_stage(stage):
    Abreviation.objects.create(stage=stage, sigle="PER", signification="Polyéthylène réticulé")
    with pytest.raises(IntegrityError):
        Abreviation.objects.create(stage=stage, sigle="PER", signification="Doublon")
