"""US-37 : vérification du courriel et purge des comptes jamais confirmés (B4, B10)."""

import datetime
import re

import pytest
from django.contrib.auth.models import Group, User
from django.core import mail
from django.utils import timezone

from comptes import inscription as svc


@pytest.fixture(autouse=True)
def _reglages(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.CARNET_DISQUE_TOTAL_MO = 100000
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    svc.reinitialiser_maintenance()


@pytest.fixture
def code(db):
    """Plus de code d'invitation (B19) : la fixture ne sert qu'à ouvrir l'accès à la base."""


def inscrire(client, nom="awa"):
    client.post("/inscription/", {
        "first_name": "Awa", "last_name": "Ndongo", "username": nom, "email": f"{nom}@exemple.cm",
        "password1": "Chantier-R10-solide", "password2": "Chantier-R10-solide",
        "avertissement_photos": "on",
    })
    lien = re.search(r"https?://\S+/inscription/verifier/\S+/", mail.outbox[-1].body).group(0)
    return User.objects.get(username=nom), lien


def test_le_courriel_contient_un_lien_absolu(client, code):
    _, lien = inscrire(client)
    assert lien.startswith("http://testserver/inscription/verifier/")
    assert mail.outbox[0].subject == "Confirmez votre inscription au Carnet de stage"


def test_lien_valide_active_le_compte(client, code):
    user, lien = inscrire(client)
    reponse = client.get(lien)
    assert reponse.status_code == 302
    assert reponse["Location"] == "/connexion/"
    user.refresh_from_db()
    assert user.is_active is True
    assert user.profil.email_verifie is True


def test_lien_ne_sert_qu_une_fois(client, code):
    _, lien = inscrire(client)
    client.get(lien)
    assert client.get(lien).status_code == 400


def test_lien_falsifie_refuse(client, code):
    user, lien = inscrire(client)
    assert client.get(lien[:-3] + "zz/").status_code == 400
    user.refresh_from_db()
    assert user.is_active is False


def test_purge_des_comptes_non_confirmes_apres_7_jours(client, code):
    user, _ = inscrire(client)
    User.objects.filter(pk=user.pk).update(date_joined=timezone.now() - datetime.timedelta(days=8))
    assert svc.purger_comptes_non_confirmes() == 1
    assert not User.objects.filter(pk=user.pk).exists()


def test_purge_epargne_les_comptes_recents_actifs_ou_crees_par_l_admin(client, code):
    recent, _ = inscrire(client, "recent")
    vieux = timezone.now() - datetime.timedelta(days=30)
    admin_inactif = User.objects.create_user("desactive", password="x", is_active=False)
    User.objects.filter(pk=admin_inactif.pk).update(date_joined=vieux)
    assert svc.purger_comptes_non_confirmes() == 0
    assert User.objects.filter(pk__in=[recent.pk, admin_inactif.pk]).count() == 2


def test_maintenance_par_middleware_au_plus_une_fois_par_heure(client, code, monkeypatch):
    appels = []
    monkeypatch.setattr(svc, "purger_comptes_non_confirmes", lambda: appels.append(1) or 0)
    client.get("/")
    client.get("/")
    assert appels == [1]
