"""US-36 (inscription libre, en tant qu'apprenant), US-42 (garde-fous du disque) — B8, B9, B19."""

import smtplib

import pytest
from django.contrib.auth.models import Group, User
from django.core import mail
from django.urls import reverse

from comptes.models import LimiteInscription, Profil

URL = "/inscription/"


@pytest.fixture(autouse=True)
def _reglages(settings, tmp_path, db):
    settings.MEDIA_ROOT = tmp_path
    settings.CARNET_DISQUE_TOTAL_MO = 100000
    settings.MAX_APPRENANTS = 6
    settings.INSCRIPTIONS_MAX_PAR_HEURE = 5
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


def donnees(**modif):
    base = {
        "first_name": "Awa", "last_name": "Ndongo", "username": "awa.ndongo", "email": "awa@exemple.cm",
        "password1": "Chantier-R10-solide", "password2": "Chantier-R10-solide",
        "avertissement_photos": "on", "site_web": "",
    }
    base.update(modif)
    return {k: v for k, v in base.items() if v is not None}


def test_page_inscription_sans_code(client):
    contenu = client.get(URL).content.decode()
    for champ in ("first_name", "last_name", "username", "email", "password1", "password2",
                  "avertissement_photos", "site_web"):
        assert f'name="{champ}"' in contenu
    assert 'name="code"' not in contenu and "code d'invitation" not in contenu.lower()


def test_inscription_libre_cree_un_compte_inactif_apprenant(client):
    reponse = client.post(URL, donnees())

    assert reponse.status_code == 302
    assert reponse["Location"] == reverse("comptes:inscription_envoyee")
    user = User.objects.get(username="awa.ndongo")
    assert user.is_active is False
    assert user.is_staff is True and user.is_superuser is False
    assert user.profil.role == Profil.Role.APPRENANT
    assert list(user.groups.values_list("name", flat=True)) == ["Apprenant"]
    assert user.profil.inscrit_par_formulaire is True
    assert user.profil.email_verifie is False
    assert len(mail.outbox) == 1 and mail.outbox[0].to == ["awa@exemple.cm"]


def test_courriel_deja_confirme_refuse_sans_tenir_compte_de_la_casse(client):
    User.objects.create_user("autre", email="AWA@exemple.cm", password="x")
    reponse = client.post(URL, donnees())
    assert "email" in reponse.context["form"].errors


@pytest.mark.parametrize("champ", ["first_name", "last_name", "email", "avertissement_photos"])
def test_champs_obligatoires(client, champ):
    reponse = client.post(URL, donnees(**{champ: None}))
    assert champ in reponse.context["form"].errors
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_mot_de_passe_faible_refuse(client):
    reponse = client.post(URL, donnees(password1="12345678", password2="12345678"))
    assert "password2" in reponse.context["form"].errors


def test_pot_de_miel_simule_la_reussite_sans_rien_creer(client):
    reponse = client.post(URL, donnees(site_web="http://spam.example"))
    assert reponse.status_code == 302
    assert not User.objects.filter(username="awa.ndongo").exists()
    assert mail.outbox == []


def test_limite_par_ip_repond_429(client):
    for i in range(5):
        client.post(URL, donnees(username=f"u{i}", email=f"u{i}@exemple.cm"))
    reponse = client.post(URL, donnees(username="u9", email="u9@exemple.cm"))
    assert reponse.status_code == 429
    assert not User.objects.filter(username="u9").exists()


def test_ip_jamais_stockee_en_clair(client):
    client.post(URL, donnees(), REMOTE_ADDR="41.202.10.7")
    trace = LimiteInscription.objects.get()
    assert "41.202" not in trace.ip_hachee and len(trace.ip_hachee) == 64


def test_erreur_smtp_supprime_le_compte(client, monkeypatch):
    def panne(*args, **kwargs):
        raise smtplib.SMTPException("panne")

    monkeypatch.setattr("comptes.inscription.send_mail", panne)
    reponse = client.post(URL, donnees())
    assert reponse.status_code == 200
    assert reponse.context["form"].non_field_errors()
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_nouvelle_inscription_remplace_un_compte_jamais_confirme(client):
    client.post(URL, donnees())
    premier = User.objects.get(username="awa.ndongo")
    client.post(URL, donnees(first_name="Awa-Marie"))
    assert User.objects.filter(username="awa.ndongo").count() == 1
    assert User.objects.get(username="awa.ndongo").pk != premier.pk


# --- US-42 : garde-fous du disque (B8), indispensables sans code d'invitation ---

def test_inscription_fermee_quand_le_disque_depasse_80_pourcent(client, settings, tmp_path):
    (tmp_path / "gros.bin").write_bytes(b"0" * 1024 * 1024)
    settings.CARNET_DISQUE_TOTAL_MO = 1
    reponse = client.get(URL)
    assert reponse.context["inscription_fermee"] is True
    assert 'name="username"' not in reponse.content.decode()
    client.post(URL, donnees())
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_inscription_fermee_quand_max_apprenants_atteint(client, settings):
    settings.MAX_APPRENANTS = 2
    apprenant = Group.objects.get_or_create(name="Apprenant")[0]
    for nom in ("a1", "a2"):
        User.objects.create_user(nom, password="x").groups.add(apprenant)
    reponse = client.post(URL, donnees())
    assert reponse.context["inscription_fermee"] is True
    assert not User.objects.filter(username="awa.ndongo").exists()


def test_apprenants_inactifs_ne_comptent_pas_dans_le_plafond(client, settings):
    settings.MAX_APPRENANTS = 1
    apprenant = Group.objects.get_or_create(name="Apprenant")[0]
    User.objects.create_user("vieux", password="x", is_active=False).groups.add(apprenant)
    client.post(URL, donnees())
    assert User.objects.filter(username="awa.ndongo").exists()


def test_le_compte_demo_ne_compte_pas_dans_le_plafond(client, settings):
    settings.MAX_APPRENANTS = 1
    apprenant = Group.objects.get_or_create(name="Apprenant")[0]
    User.objects.create_user(settings.COMPTE_DEMO, password="x").groups.add(apprenant)
    client.post(URL, donnees())
    assert User.objects.filter(username="awa.ndongo").exists()
