from django.db import migrations

from carnet.referentiel import RUBRIQUES_AUTRES, RUBRIQUES_ENTREPRISE, RUBRIQUES_MISSION, uuid_rubrique_cours


def precharger(apps, schema_editor):
    Rubrique = apps.get_model("carnet", "Rubrique")
    lignes = [("entreprise", c, l) for c, l in RUBRIQUES_ENTREPRISE]
    lignes += [("mission", c, l) for c, l in RUBRIQUES_MISSION]
    lignes += RUBRIQUES_AUTRES
    for ordre, (partie, code, libelle) in enumerate(lignes):
        Rubrique.objects.update_or_create(
            id=uuid_rubrique_cours(code),
            defaults={"code": code, "stage": None, "libelle": libelle, "partie": partie, "ordre": ordre},
        )


def retirer(apps, schema_editor):
    apps.get_model("carnet", "Rubrique").objects.filter(stage__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("carnet", "0002_rubrique")]

    operations = [migrations.RunPython(precharger, retirer)]
