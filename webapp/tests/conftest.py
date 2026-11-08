import datetime

import pytest
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def _hachage_rapide(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


def _apprenant(nom):
    """Comme dans l'application : le profil Apprenant applique ses droits (B15)."""
    from django.core.management import call_command

    call_command("creer_groupes", verbosity=0)
    user = User.objects.create_user(nom, password="x")
    user.profil.save()
    return user


@pytest.fixture
def apprenant(db):
    return _apprenant("awa")


@pytest.fixture
def autre_apprenant(db):
    return _apprenant("bruno")


@pytest.fixture
def stage(apprenant):
    from carnet.models import Stage

    return Stage.objects.create(
        proprietaire=apprenant,
        intitule="Stage plomberie",
        date_debut=datetime.date(2026, 3, 2),
        date_fin=datetime.date(2026, 6, 26),
    )
