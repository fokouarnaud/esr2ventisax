"""B15 et B17 : rôle de chaque profil déduit des droits existants, puis droits réappliqués depuis le profil.

Les anciens formateurs deviennent apprenants. Même règle que comptes.droits.appliquer_role (les modèles
historiques n'ont pas le Profil.save() qui l'appelle) : Apprenant = groupe Apprenant + statut équipe ;
Administrateur = superutilisateur, sans groupe.
"""

from django.db import migrations


def role_depuis_les_droits(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    Profil = apps.get_model("comptes", "Profil")
    apprenant, _ = Group.objects.get_or_create(name="Apprenant")
    for user in User.objects.all():
        role = "administrateur" if user.is_superuser else "apprenant"
        Profil.objects.update_or_create(user=user, defaults={"role": role})
        user.groups.set([] if role == "administrateur" else [apprenant])
        User.objects.filter(pk=user.pk).update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [("comptes", "0003_role_sans_code")]
    operations = [migrations.RunPython(role_depuis_les_droits, migrations.RunPython.noop)]
