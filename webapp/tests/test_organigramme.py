"""US-09 : organigramme structuré (A25)."""

import pytest
from django.core.exceptions import ValidationError

from carnet.models import NoeudOrganigramme


def test_un_seul_noeud_stagiaire_par_stage(stage):
    NoeudOrganigramme.objects.create(stage=stage, poste="Stagiaire", est_stagiaire=True)
    doublon = NoeudOrganigramme(stage=stage, poste="Second stagiaire", est_stagiaire=True)
    with pytest.raises(ValidationError):
        doublon.full_clean()


def test_le_parent_ne_peut_pas_etre_un_descendant(stage):
    dg = NoeudOrganigramme.objects.create(stage=stage, poste="Directeur général")
    ct = NoeudOrganigramme.objects.create(stage=stage, poste="Conducteur des travaux", parent=dg)
    dg.parent = ct
    with pytest.raises(ValidationError):
        dg.full_clean()


def test_un_noeud_ne_peut_pas_etre_son_propre_parent(stage):
    dg = NoeudOrganigramme.objects.create(stage=stage, poste="DG")
    dg.parent = dg
    with pytest.raises(ValidationError):
        dg.full_clean()
