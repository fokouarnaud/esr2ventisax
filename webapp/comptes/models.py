"""Comptes ouverts (PRD incrément 4, P4-3) : profil, codes d'invitation, traces anti-abus."""

import datetime
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from carnet.models.base import ModeleBase

ALPHABET_CODE = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # sans 0, O, 1, I ni L (B2)
LONGUEUR_CODE = 8


def generer_code():
    while True:
        code = "".join(secrets.choice(ALPHABET_CODE) for _ in range(LONGUEUR_CODE))
        if not CodeInvitation.objects.filter(code=code).exists():
            return code


def expiration_par_defaut():
    return timezone.now() + datetime.timedelta(days=90)


class CodeInvitation(ModeleBase):
    formateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name="codes_invitation", verbose_name="formateur")
    code = models.CharField("code", max_length=LONGUEUR_CODE, unique=True, default=generer_code)
    usages_max = models.PositiveIntegerField("usages maximum", default=5)
    usages = models.PositiveIntegerField("usages", default=0)
    expire_le = models.DateTimeField("expire le", default=expiration_par_defaut)
    actif = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "code d'invitation"
        verbose_name_plural = "codes d'invitation"
        ordering = ["-cree_le"]

    def __str__(self):
        return self.code

    def est_utilisable(self, maintenant=None):
        return self.actif and self.usages < self.usages_max and self.expire_le > (maintenant or timezone.now())


class Profil(ModeleBase):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil")
    email_verifie = models.BooleanField("courriel vérifié", default=False)
    inscrit_par_formulaire = models.BooleanField("inscrit par le formulaire", default=False)
    code_utilise = models.ForeignKey(CodeInvitation, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="profils", verbose_name="code utilisé")

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profils"

    def __str__(self):
        return f"Profil de {self.user}"


class EchecConnexion(ModeleBase):
    identifiant = models.CharField(max_length=150, db_index=True)
    survenu_le = models.DateTimeField(auto_now_add=True, db_index=True)


class LimiteInscription(ModeleBase):
    ip_hachee = models.CharField(max_length=64, db_index=True)  # HMAC-SHA256, jamais l'IP en clair
    survenu_le = models.DateTimeField(auto_now_add=True, db_index=True)
