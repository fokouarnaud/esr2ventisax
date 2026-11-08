"""Un profil vérifié pour chaque compte créé avant l'inscription publique (B10, US-43)."""

from django.db import migrations


def creer_profils_existants(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Profil = apps.get_model("comptes", "Profil")
    for user in User.objects.all():
        profil, _ = Profil.objects.get_or_create(user=user)
        if not profil.inscrit_par_formulaire and not profil.email_verifie:
            profil.email_verifie = True
            profil.save(update_fields=["email_verifie"])


class Migration(migrations.Migration):
    dependencies = [("comptes", "0001_comptes"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [migrations.RunPython(creer_profils_existants, migrations.RunPython.noop)]
