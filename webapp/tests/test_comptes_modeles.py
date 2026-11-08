"""Modèle de données des comptes ouverts (PRD incrément 4, P4-3)."""

import datetime
import uuid

import pytest
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.utils import timezone

from comptes.models import CodeInvitation, EchecConnexion, LimiteInscription, Profil

ALPHABET_INTERDIT = set("0O1IL")


@pytest.fixture
def formateur(db):
    user = User.objects.create_user("prof", password="x", is_staff=True)
    user.groups.add(Group.objects.get_or_create(name="Formateur")[0])
    return user


def test_profil_cree_automatiquement_pour_tout_user(db):
    user = User.objects.create_user("zoe", password="x")
    assert isinstance(user.profil.id, uuid.UUID)
    assert user.profil.email_verifie is False
    assert user.profil.inscrit_par_formulaire is False
    assert user.profil.code_utilise is None


def test_code_genere_de_8_caracteres_sans_ambiguite(formateur):
    codes = {CodeInvitation.objects.create(formateur=formateur).code for _ in range(30)}
    assert len(codes) == 30
    for code in codes:
        assert len(code) == 8
        assert not set(code) & ALPHABET_INTERDIT


def test_code_valeurs_par_defaut(formateur):
    code = CodeInvitation.objects.create(formateur=formateur)
    assert code.usages_max == 5
    assert code.usages == 0
    assert code.actif is True
    assert code.expire_le.date() == (timezone.now() + datetime.timedelta(days=90)).date()


def test_code_unique(formateur):
    CodeInvitation.objects.create(formateur=formateur, code="ABCDEFGH")
    with pytest.raises(IntegrityError):
        CodeInvitation.objects.create(formateur=formateur, code="ABCDEFGH")


@pytest.mark.parametrize("modif, utilisable", [
    ({}, True),
    ({"actif": False}, False),
    ({"usages": 5}, False),
    ({"expire_le": timezone.now() - datetime.timedelta(minutes=1)}, False),
])
def test_code_utilisable(formateur, modif, utilisable):
    code = CodeInvitation.objects.create(formateur=formateur, **modif)
    assert code.est_utilisable() is utilisable


def test_echec_et_limite_ont_un_horodatage(db):
    echec = EchecConnexion.objects.create(identifiant="awa")
    limite = LimiteInscription.objects.create(ip_hachee="f" * 64)
    assert echec.survenu_le and limite.survenu_le
