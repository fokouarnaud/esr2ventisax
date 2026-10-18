"""Quota disque par stage (A33)."""

from django.db.models import Sum

OCTETS_PAR_MO = 1024 * 1024


class QuotaDepasse(Exception):
    pass


def octets_utilises(stage):
    from carnet.models import Photo

    return Photo.objects.filter(stage=stage).aggregate(total=Sum("taille_octets"))["total"] or 0


def octets_restants(stage):
    return max(stage.quota_mo * OCTETS_PAR_MO - octets_utilises(stage), 0)


def verifier_quota(stage, nouveaux_octets):
    if nouveaux_octets > octets_restants(stage):
        raise QuotaDepasse(
            f"Quota de {stage.quota_mo} Mo atteint pour ce stage : supprimez ou triez des photos, "
            "ou demandez une augmentation à l'administrateur."
        )
