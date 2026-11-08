from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.security, deploy=True)
def smtp_configure(app_configs, **kwargs):
    """Sans SMTP, l'inscription et le mot de passe oublié échouent en ligne (US-44)."""
    if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
        return []
    return [Error(
        "Envoi des courriels non configuré : EMAIL_HOST_USER et EMAIL_HOST_PASSWORD manquent dans le .env.",
        hint="Coller le mot de passe d'application Gmail dans webapp/.env sur le serveur (DEPLOIEMENT.md).",
        id="comptes.E001",
    )]
