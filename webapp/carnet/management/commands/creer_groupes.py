from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from carnet.acces import GROUPE_APPRENANT


class Command(BaseCommand):
    help = ("Crée ou met à jour le groupe Apprenant, qui porte les droits du profil Apprenant (B15), "
            "et supprime l'ancien groupe Formateur (B17). Idempotent.")

    def handle(self, *args, **options):
        # le cloisonnement par stage est appliqué par l'admin et les vues (carnet.acces)
        permissions = Permission.objects.filter(content_type__app_label="carnet")
        groupe, cree = Group.objects.get_or_create(name=GROUPE_APPRENANT)
        groupe.permissions.set(permissions)
        self.stdout.write(f"{GROUPE_APPRENANT} : {'créé' if cree else 'mis à jour'} ({permissions.count()} permissions)")
        supprimes, _ = Group.objects.filter(name="Formateur").delete()
        if supprimes:
            self.stdout.write("Formateur : supprimé (plus de compte formateur, B17)")
