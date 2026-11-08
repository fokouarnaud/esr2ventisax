"""Droits portés par le profil (B15) : un rôle, et tout le reste en découle.

Les permissions du profil Apprenant sont définies par `creer_groupes` ; l'Administrateur est superutilisateur.
Il n'y a plus de compte formateur (B17) : son nom est un simple libellé de la couverture du stage.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from carnet.acces import GROUPE_APPRENANT, GROUPE_DEMONSTRATION

GROUPES_PAR_ROLE = {"apprenant": [GROUPE_APPRENANT], "administrateur": [],
                    "demonstration": [GROUPE_DEMONSTRATION]}  # B21 : droits de consultation seuls


def appliquer_role(user, role):
    user.groups.set([Group.objects.get_or_create(name=nom)[0] for nom in GROUPES_PAR_ROLE[role]])
    staff, superuser = True, role == "administrateur"
    get_user_model().objects.filter(pk=user.pk).update(is_staff=staff, is_superuser=superuser)
    user.is_staff, user.is_superuser = staff, superuser


def role_deduit(user):
    """Rôle d'un compte créé autrement que par un profil (createsuperuser, anciens comptes)."""
    return "administrateur" if user.is_superuser else "apprenant"
