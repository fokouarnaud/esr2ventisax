"""Comptes ouverts (PRD incrément 4, P4-3) : profil (porteur des droits), traces anti-abus.

Inscription libre en tant qu'apprenant (B19) : plus de code d'invitation ni de compte formateur (B17)."""

from django.conf import settings
from django.db import models

from carnet.models.base import ModeleBase


# --- Conservés pour l'historique des migrations (0001 : ancien modèle CodeInvitation, retiré par B19) ---

def generer_code():
    import secrets

    return "".join(secrets.choice("ABCDEFGHJKMNPQRSTUVWXYZ23456789") for _ in range(8))


def expiration_par_defaut():
    import datetime

    from django.utils import timezone

    return timezone.now() + datetime.timedelta(days=90)


class Profil(ModeleBase):
    """Le profil porte les droits (B15) : groupes, statut équipe et superutilisateur en découlent."""

    class Role(models.TextChoices):
        APPRENANT = "apprenant", "Apprenant"
        ADMINISTRATEUR = "administrateur", "Administrateur"
        DEMONSTRATION = "demonstration", "Démonstration"  # consultation seule (B21)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil")
    role = models.CharField("profil", max_length=20, choices=Role.choices, default=Role.APPRENANT)
    email_verifie = models.BooleanField("courriel vérifié", default=False)
    inscrit_par_formulaire = models.BooleanField("inscrit par le formulaire", default=False)

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profils"

    def __str__(self):
        return f"{self.get_role_display()} : {self.user}"

    def save(self, *args, synchroniser=True, **kwargs):
        super().save(*args, **kwargs)
        if synchroniser:
            from .droits import appliquer_role

            appliquer_role(self.user, self.role)


class EchecConnexion(ModeleBase):
    identifiant = models.CharField(max_length=150, db_index=True)
    survenu_le = models.DateTimeField(auto_now_add=True, db_index=True)


class LimiteInscription(ModeleBase):
    ip_hachee = models.CharField(max_length=64, db_index=True)  # HMAC-SHA256, jamais l'IP en clair
    survenu_le = models.DateTimeField(auto_now_add=True, db_index=True)
