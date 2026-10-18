"""Cloisonnement (A1, A13, A32) : point unique de décision sur ce que voit chaque compte."""

from .models import Stage

GROUPE_APPRENANT = "Apprenant"
GROUPE_FORMATEUR = "Formateur"


def est_formateur(user):
    return user.groups.filter(name=GROUPE_FORMATEUR).exists()


def stages_visibles(user):
    if user.is_superuser:
        return Stage.objects.all()
    if est_formateur(user):
        return Stage.objects.filter(formateur_referent=user)
    return Stage.objects.filter(proprietaire=user)


def stages_modifiables(user):
    if user.is_superuser:
        return Stage.objects.all()
    return Stage.objects.filter(proprietaire=user)


def filtrer_visibles(user, queryset):
    """Restreint un queryset d'entités propres à un stage (champ `stage`)."""
    return queryset.filter(stage__in=stages_visibles(user))


def filtrer_modifiables(user, queryset):
    return queryset.filter(stage__in=stages_modifiables(user))
