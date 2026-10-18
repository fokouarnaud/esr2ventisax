import datetime

from django.db import migrations

from carnet.referentiel import FERIES_FIXES_CAMEROUN


def precharger(apps, schema_editor):
    Absence = apps.get_model("carnet", "Absence")
    for mois, jour, libelle in FERIES_FIXES_CAMEROUN:
        date = datetime.date(2000, mois, jour)  # l'année est ignorée : annuel=True
        Absence.objects.get_or_create(
            stage=None, libelle=libelle,
            defaults={"date_debut": date, "date_fin": date, "motif": "ferie", "annuel": True},
        )


def retirer(apps, schema_editor):
    apps.get_model("carnet", "Absence").objects.filter(stage__isnull=True, annuel=True).delete()


class Migration(migrations.Migration):
    dependencies = [("carnet", "0008_calendrier")]

    operations = [migrations.RunPython(precharger, retirer)]
