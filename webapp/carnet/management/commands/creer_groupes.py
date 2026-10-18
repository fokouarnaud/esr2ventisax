from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from carnet.acces import GROUPE_APPRENANT, GROUPE_FORMATEUR


class Command(BaseCommand):
    help = "Crée ou met à jour les groupes Apprenant et Formateur et leurs permissions (idempotent)."

    def handle(self, *args, **options):
        carnet = Permission.objects.filter(content_type__app_label="carnet")
        droits = {
            # le cloisonnement par stage est appliqué par l'admin et les vues (carnet.acces)
            GROUPE_APPRENANT: carnet,
            GROUPE_FORMATEUR: carnet.filter(codename__startswith="view_")
            | carnet.filter(codename="change_entreejournal"),
        }
        for nom, permissions in droits.items():
            groupe, cree = Group.objects.get_or_create(name=nom)
            groupe.permissions.set(permissions)
            self.stdout.write(f"{nom} : {'créé' if cree else 'mis à jour'} ({permissions.count()} permissions)")
