"""US-36 (inscription par code), US-42 (garde-fous du disque) — B1, B2, B8, B9."""

import datetime
import smtplib

import pytest
from django.contrib.auth.models import Group, User
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from comptes.models import CodeInvitation, LimiteInscription

URL = "/inscription/"


@pytest.fixture(autouse=True)
def _reglages(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.CARNET_DISQUE_TOTAL_MO = 100000
    settings.MAX_APPRENANTS = 6
    settings.INSCRIPTIONS_MAX_PAR_HEURE = 5
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def formateur(db):
    user = User.objects.create_user("prof", password="x", is_staff=True)
    user.groups.add(Group.objects.get_or_create(name="Formateur")[0])
    return user


@pytest.fixture
def code(formateur):
    return CodeInvitation.objects.create(formateur=formateur, code="ABCDEFGH")


def donnees(**modif):
    base = {
        "first_name": "Awa", "last_name": "Ndongo", "username": "awa.ndongo", "email": "awa@exemple.cm",
        "password1": "Chantier-R10-solide", "password2": "Chantier-R10-solide", "code": "ABCDEFGH",
        "avertissement_photos": "on", "site_web": "",
    }
    base.update(modif)
    return {k: v for k, v in base.items() if v is not None}


def test_page_inscription_affiche_le_formulaire(client, db):
    reponse = client.get(URL)
    assert reponse.status_code == 200
    for champ in ("first_name", "last_name", "username", "email", "password1", "password2", "code",
                  "avertissement_photos", "site_web"):
        assert f'name="{champ}"' in reponse.content.decode()


def test_inscription_reussie_cree_un_compte_inactif_apprenant(client, code):
    reponse = client.post(URL, donnees())

    assert reponse.status_code == 302
    assert reponse["Location"] == reverse("comptes:inscription_envoyee")
    user = User.objects.get(username="awa.ndongo")
    assert user.is_active is False
    assert user.is_staff is True
    assert list(user.groups.values_list("name", flat=True)) == ["Apprenant"]
    assert user.profil.inscrit_par_formulaire is True
    assert user.profil.email_verifie is False
    assert user.profil.code_utilise == code
    code.refresh_from_db()
    assert code.usages == 1
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ["awa@exemple.cm"]


def test_code_insensible_a_la_casse_et_aux_espaces(client, code):
    client.post(URL, donnees(code=" abcdefgh "))
    assert User.objects.filter(username="awa.ndongo").exists()


@pytest.mark.parametrize("modif", [
    {"actif": False},
    {"usages": 5},
    {"expire_le": timezone.now() - datetime.timedelta(days=1)},
])
def test_code_inutilisable_refuse(client, code, modif):
    CodeInvitation.objects.filter(pk=code.pk).update(**modif)
    reponse = client.post(URL, donnees())
    assert reponse.status_code == 200
    assert "code" in reponse.context["form"].errors
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_code_inconnu_refuse(client, code):
    reponse = client.post(URL, donnees(code="ZZZZZZZZ"))
    assert "code" in reponse.context["form"].errors


def test_courriel_deja_confirme_refuse_sans_tenir_compte_de_la_casse(client, code):
    User.objects.create_user("autre", email="AWA@exemple.cm", password="x")
    reponse = client.post(URL, donnees())
    assert "email" in reponse.context["form"].errors


@pytest.mark.parametrize("champ", ["first_name", "last_name", "email", "avertissement_photos"])
def test_champs_obligatoires(client, code, champ):
    reponse = client.post(URL, donnees(**{champ: None}))
    assert champ in reponse.context["form"].errors
    assert not User.objects.exists() or not User.objects.filter(username="awa.ndongo").exists()


def test_mot_de_passe_faible_refuse(client, code):
    reponse = client.post(URL, donnees(password1="12345678", password2="12345678"))
    assert "password2" in reponse.context["form"].errors


def test_pot_de_miel_simule_la_reussite_sans_rien_creer(client, code):
    reponse = client.post(URL, donnees(site_web="http://spam.example"))
    assert reponse.status_code == 302
    assert not User.objects.filter(username="awa.ndongo").exists()
    assert mail.outbox == []


def test_limite_par_ip_repond_429(client, code):
    for i in range(5):
        client.post(URL, donnees(username=f"u{i}", email=f"u{i}@exemple.cm"))
    reponse = client.post(URL, donnees(username="u9", email="u9@exemple.cm"))
    assert reponse.status_code == 429
    assert not User.objects.filter(username="u9").exists()


def test_ip_jamais_stockee_en_clair(client, code):
    client.post(URL, donnees(), REMOTE_ADDR="41.202.10.7")
    trace = LimiteInscription.objects.get()
    assert "41.202" not in trace.ip_hachee and len(trace.ip_hachee) == 64


def test_erreur_smtp_supprime_le_compte(client, code, monkeypatch):
    def panne(*args, **kwargs):
        raise smtplib.SMTPException("panne")

    monkeypatch.setattr("comptes.inscription.send_mail", panne)
    reponse = client.post(URL, donnees())
    assert reponse.status_code == 200
    assert reponse.context["form"].non_field_errors()
    assert not User.objects.filter(username="awa.ndongo").exists()
    code.refresh_from_db()
    assert code.usages == 0


def test_nouvelle_inscription_remplace_un_compte_jamais_confirme(client, code):
    client.post(URL, donnees())
    premier = User.objects.get(username="awa.ndongo")
    client.post(URL, donnees(first_name="Awa-Marie"))
    assert User.objects.filter(username="awa.ndongo").count() == 1
    assert User.objects.get(username="awa.ndongo").pk != premier.pk


# --- US-42 : garde-fous du disque (B8) ---

def test_inscription_fermee_quand_le_disque_depasse_80_pourcent(client, code, settings, tmp_path):
    (tmp_path / "gros.bin").write_bytes(b"0" * 1024 * 1024)
    settings.CARNET_DISQUE_TOTAL_MO = 1
    reponse = client.get(URL)
    assert reponse.context["inscription_fermee"] is True
    assert 'name="code"' not in reponse.content.decode()
    client.post(URL, donnees())
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_inscription_fermee_quand_max_apprenants_atteint(client, code, settings):
    settings.MAX_APPRENANTS = 2
    apprenant = Group.objects.get_or_create(name="Apprenant")[0]
    for nom in ("a1", "a2"):
        User.objects.create_user(nom, password="x").groups.add(apprenant)
    reponse = client.post(URL, donnees())
    assert reponse.context["inscription_fermee"] is True
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_apprenants_inactifs_ne_comptent_pas_dans_le_plafond(client, code, settings):
    settings.MAX_APPRENANTS = 1
    apprenant = Group.objects.get_or_create(name="Apprenant")[0]
    User.objects.create_user("vieux", password="x", is_active=False).groups.add(apprenant)
    client.post(URL, donnees())
    assert User.objects.filter(username="awa.ndongo").exists()
