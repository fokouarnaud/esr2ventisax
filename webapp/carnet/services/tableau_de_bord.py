"""Indicateurs du tableau de bord (US-25, US-26)."""

from pathlib import Path

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

from carnet.models import EntreeJournal, Photo, Rubrique

SEUIL_PHOTOS_CORPS = 25
SEUIL_SAUVEGARDE_JOURS = 7


def rubriques_vides(stage):
    """Codes des rubriques Entreprise et Mission sans texte saisi ni note étiquetée (A23)."""
    formulaires = {Rubrique.Partie.ENTREPRISE: stage.fiche_entreprise, Rubrique.Partie.MISSION: stage.mission}
    etiquetees = set(
        EntreeJournal.objects.filter(stage=stage).values_list("rubriques__code", flat=True)
    )
    vides = []
    for r in Rubrique.objects.filter(stage__isnull=True, partie__in=formulaires):
        champ = r.code.split(".", 1)[1]
        if not getattr(formulaires[r.partie], champ).strip() and r.code not in etiquetees:
            vides.append(r.code)
    return vides


def synthese_photos(stage):
    comptes = dict(Photo.objects.filter(stage=stage).values_list("destination").annotate(n=Count("pk")))
    par_destination = {d.value: comptes.get(d.value, 0) for d in Photo.Destination}
    return {
        "par_destination": par_destination,
        "trop_dans_le_corps": par_destination[Photo.Destination.CORPS] > SEUIL_PHOTOS_CORPS,
    }


def sauvegarde(stage, maintenant=None):
    if stage.derniere_sauvegarde is None:
        return {"jours": None, "alerte": True}
    jours = ((maintenant or timezone.now()) - stage.derniere_sauvegarde).days
    return {"jours": jours, "alerte": jours > SEUIL_SAUVEGARDE_JOURS}


def _taille(chemin):
    if chemin.is_file():
        return chemin.stat().st_size
    if chemin.is_dir():
        return sum(f.stat().st_size for f in chemin.rglob("*") if f.is_file())
    return 0


def occupation_globale(chemins, total_octets):
    octets = sum(_taille(Path(c)) for c in chemins)
    ratio = octets / total_octets
    return {"octets": octets, "ratio": ratio, "alerte": ratio > settings.CARNET_SEUIL_ALERTE_DISQUE}



def indicateurs(stage, aujourd_hui=None):
    """Tout ce qu'affiche le tableau de bord d'un stage (US-25)."""
    from carnet.services import calendrier, quota

    return {
        "rubriques_vides": rubriques_vides(stage),
        "notes_non_completees": EntreeJournal.objects.filter(stage=stage, completee=False).count(),
        "jours_sans_note": calendrier.jours_sans_note(stage, jusqu_au=aujourd_hui),
        "photos": synthese_photos(stage),
        "quota": {"utilise": quota.octets_utilises(stage), "restant": quota.octets_restants(stage),
                  "quota_mo": stage.quota_mo},
        "sauvegarde": sauvegarde(stage),
        "taux_presence": calendrier.taux_presence(stage),
    }
