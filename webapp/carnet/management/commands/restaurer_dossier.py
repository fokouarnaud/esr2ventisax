import zipfile

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from carnet.services.export import restaurer


class Command(BaseCommand):
    help = "Restaure un zip « dossier terrain » dans la base (idempotent, UUID conservés)."

    def add_arguments(self, parser):
        parser.add_argument("archive")
        parser.add_argument("--proprietaire", required=True, help="Identifiant du compte apprenant.")

    def handle(self, *args, **opts):
        try:
            proprietaire = get_user_model().objects.get(username=opts["proprietaire"])
        except get_user_model().DoesNotExist as exc:
            raise CommandError(f"Compte inconnu : {opts['proprietaire']}") from exc
        with zipfile.ZipFile(opts["archive"]) as z:
            stage = restaurer(z, proprietaire=proprietaire)
        self.stdout.write(self.style.SUCCESS(f"Stage restauré : {stage} ({stage.pk})"))
