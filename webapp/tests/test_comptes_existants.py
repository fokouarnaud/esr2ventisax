"""US-43 : comptes existants et compte démo (B10)."""

import importlib

from django.apps import apps
from django.contrib.auth.models import User

from comptes.models import Profil

migration = importlib.import_module("comptes.migrations.0002_profils_existants")


def test_migration_cree_un_profil_verifie_pour_chaque_compte_existant(db):
    ancien = User.objects.create_user("fokou", password="x")
    Profil.objects.filter(user=ancien).delete()  # état d'avant l'incrément 4
    deja = User.objects.create_user("awa", password="x")

    migration.creer_profils_existants(apps, None)

    assert Profil.objects.get(user=ancien).email_verifie is True
    assert Profil.objects.get(user=deja).email_verifie is True
    assert Profil.objects.count() == 2
