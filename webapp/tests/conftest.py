import datetime

import pytest
from django.contrib.auth.models import User


@pytest.fixture(autouse=True)
def _hachage_rapide(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def apprenant(db):
    return User.objects.create_user("awa", password="x")


@pytest.fixture
def autre_apprenant(db):
    return User.objects.create_user("bruno", password="x")


@pytest.fixture
def stage(apprenant):
    from carnet.models import Stage

    return Stage.objects.create(
        proprietaire=apprenant,
        intitule="Stage plomberie",
        date_debut=datetime.date(2026, 3, 2),
        date_fin=datetime.date(2026, 6, 26),
    )
