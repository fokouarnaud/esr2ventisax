"""Blocage temporaire après trop d'échecs pour un même identifiant (US-39).

Le compteur porte sur l'identifiant saisi, qu'il existe ou non : le blocage ne révèle pas quels comptes
existent. L'IP n'est pas utilisée : derrière le proxy de PythonAnywhere, elle serait commune à tous.
"""

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import EchecConnexion


def _cle(identifiant):
    return (identifiant or "").strip().lower()[:150]


def est_bloque(identifiant):
    depuis = timezone.now() - settings.LOGIN_BLOCAGE
    return EchecConnexion.objects.filter(identifiant=_cle(identifiant), survenu_le__gte=depuis).count() \
        >= settings.LOGIN_MAX_ECHECS


def noter_echec(identifiant):
    EchecConnexion.objects.filter(survenu_le__lt=timezone.now() - timezone.timedelta(hours=24)).delete()
    EchecConnexion.objects.create(identifiant=_cle(identifiant))


class FormulaireConnexion(AuthenticationForm):
    verrouille = False
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Identifiant ou mot de passe incorrect, ou compte pas encore confirmé.",
        "inactive": "Identifiant ou mot de passe incorrect, ou compte pas encore confirmé.",
    }

    def clean(self):
        identifiant = self.cleaned_data.get("username")
        if est_bloque(identifiant):
            self.verrouille = True
            raise ValidationError("Trop de tentatives de connexion. Réessayez dans 15 minutes.", code="verrouille")
        try:
            resultat = super().clean()
        except ValidationError:
            noter_echec(identifiant)
            raise
        EchecConnexion.objects.filter(identifiant=_cle(identifiant)).delete()
        return resultat


class FormulaireMotDePasseOublie(PasswordResetForm):
    """Le compte démo, aux identifiants publics, ne reçoit jamais de lien (B10)."""

    def get_users(self, email):
        return (u for u in super().get_users(email) if u.username != settings.COMPTE_DEMO)


class FormulaireNouveauMotDePasse(SetPasswordForm):
    """Aides courtes, comme à l'inscription : celles de Django allongent la page au téléphone."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = "8 caractères au moins, pas seulement des chiffres, ni proche de votre nom."
        self.fields["new_password2"].help_text = ""
