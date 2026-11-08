"""Cloisonnement (A1, A13, B17) : point unique de décision sur ce que voit chaque compte.

Deux profils seulement : l'apprenant voit ses stages, l'administrateur voit tout. Plus de compte formateur.
"""

from .models import Stage

GROUPE_APPRENANT = "Apprenant"
GROUPE_DEMONSTRATION = "Démonstration"


def peut_ecrire(user):
    """Faux pour le profil Démonstration (B21) : il consulte tout son stage mais n'écrit rien."""
    return user.has_perm("carnet.add_entreejournal")


def stages_visibles(user):
    if user.is_superuser:
        return Stage.objects.all()
    return Stage.objects.filter(proprietaire=user)


def stages_modifiables(user):
    return stages_visibles(user)


def filtrer_visibles(user, queryset):
    """Restreint un queryset d'entités propres à un stage (champ `stage`)."""
    return queryset.filter(stage__in=stages_visibles(user))


def filtrer_modifiables(user, queryset):
    return queryset.filter(stage__in=stages_modifiables(user))
