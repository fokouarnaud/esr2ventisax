"""B21 : profil Démonstration (consultation seule) ; le compte démo existant y passe.

Même règle que comptes.droits.appliquer_role : groupe Démonstration (droits view_ seuls) + statut équipe.
Les permissions du groupe sont posées par `creer_groupes`, lancé à chaque déploiement.
"""

from django.conf import settings
from django.db import migrations, models


def demo_en_lecture_seule(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    Profil = apps.get_model("comptes", "Profil")
    demo = User.objects.filter(username=settings.COMPTE_DEMO).first()
    if demo is None:
        return
    Profil.objects.update_or_create(user=demo, defaults={"role": "demonstration"})
    demo.groups.set([Group.objects.get_or_create(name="Démonstration")[0]])
    User.objects.filter(pk=demo.pk).update(is_staff=True, is_superuser=False)


class Migration(migrations.Migration):
    dependencies = [("comptes", "0004_role_depuis_les_droits")]
    operations = [
        migrations.AlterField(
            model_name="profil",
            name="role",
            field=models.CharField(choices=[("apprenant", "Apprenant"), ("administrateur", "Administrateur"),
                                            ("demonstration", "Démonstration")],
                                   default="apprenant", max_length=20, verbose_name="profil"),
        ),
        migrations.RunPython(demo_en_lecture_seule, migrations.RunPython.noop),
    ]
