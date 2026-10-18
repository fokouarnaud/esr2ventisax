"""Jours ouvrés, jours sans note et taux de présence (A29, A30)."""

import datetime

from django.db.models import Q
from django.utils import timezone

from carnet.models import Absence, EntreeJournal


def _jours(debut, fin):
    jour = debut
    while jour <= fin:
        yield jour
        jour += datetime.timedelta(days=1)


def _absences(stage):
    return Absence.objects.filter(Q(stage=stage) | Q(stage__isnull=True))


def _couvre(absence, jour):
    if absence.annuel:
        return (absence.date_debut.month, absence.date_debut.day) <= (jour.month, jour.day) <= (
            absence.date_fin.month, absence.date_fin.day)
    return absence.date_debut <= jour <= absence.date_fin


def _jours_travailles(stage):
    return [j for j in _jours(stage.date_debut, stage.date_fin) if j.weekday() in stage.jours_travailles]


def jours_prevus(stage):
    """Jours travaillés du stage, hors jours fériés (communs ou propres au stage)."""
    feries = [a for a in _absences(stage) if a.motif == Absence.Motif.FERIE]
    return [j for j in _jours_travailles(stage) if not any(_couvre(f, j) for f in feries)]


def jours_presents(stage):
    perso = [a for a in _absences(stage) if a.motif != Absence.Motif.FERIE]
    return [j for j in jours_prevus(stage) if not any(_couvre(a, j) for a in perso)]


def taux_presence(stage):
    prevus = jours_prevus(stage)
    return len(jours_presents(stage)) / len(prevus) if prevus else 1.0


def jours_sans_note(stage, jusqu_au=None):
    jusqu_au = jusqu_au or timezone.localdate()
    notes = set(EntreeJournal.objects.filter(stage=stage).values_list("date", flat=True))
    return [j for j in jours_presents(stage) if j <= jusqu_au and j not in notes]
