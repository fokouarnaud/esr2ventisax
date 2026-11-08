from django.apps import AppConfig


class ComptesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "comptes"
    verbose_name = "Comptes"

    def ready(self):
        from . import checks, signaux  # noqa: F401  (contrôle SMTP, profil créé pour tout User)
