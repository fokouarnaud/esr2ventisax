"""Modèle de données des comptes ouverts (PRD incrément 4, P4-3)."""

import datetime
import uuid

import pytest
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from django.utils import timezone

from comptes.models import EchecConnexion, LimiteInscription, Profil

ALPHABET_INTERDIT = set("0O1IL")


def test_profil_cree_automatiquement_pour_tout_user(db):
    user = User.objects.create_user("zoe", password="x")
    assert isinstance(user.profil.id, uuid.UUID)
    assert user.profil.email_verifie is False
    assert user.profil.inscrit_par_formulaire is False


def test_echec_et_limite_ont_un_horodatage(db):
    echec = EchecConnexion.objects.create(identifiant="awa")
    limite = LimiteInscription.objects.create(ip_hachee="f" * 64)
    assert echec.survenu_le and limite.survenu_le
