"""B21 : le compte de démonstration est en lecture seule (profil Démonstration, droits de consultation seuls)."""

import datetime
import importlib

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse

from carnet.models import Absence, EntreeJournal, Photo, Stage
from comptes.models import Profil

D = datetime.date


@pytest.fixture
def demo(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    call_command("creer_groupes")
    user = User.objects.create_user(settings.COMPTE_DEMO, password="demo-local-2026")
    user.profil.role = Profil.Role.DEMONSTRATION
    user.profil.save()
    stage = Stage.objects.create(proprietaire=user, intitule="Stage démo", date_debut=D(2026, 6, 1),
                                 date_fin=D(2026, 9, 19))
    return user, stage


def test_profil_demonstration_ne_donne_que_la_consultation(demo):
    user, _ = demo
    user.refresh_from_db()
    assert user.is_staff and not user.is_superuser
    assert list(user.groups.values_list("name", flat=True)) == ["Démonstration"]
    codes = set(Group.objects.get(name="Démonstration").permissions.values_list("codename", flat=True))
    assert codes and all(c.startswith("view_") for c in codes)
    assert not user.has_perm("carnet.add_entreejournal") and user.has_perm("carnet.view_entreejournal")


def test_admin_en_lecture_seule(client, demo):
    user, stage = demo
    client.force_login(user)
    assert client.get(reverse("admin:carnet_stage_change", args=[stage.pk])).status_code == 200
    client.post(reverse("admin:carnet_stage_change", args=[stage.pk]), {
        "intitule": "Piraté", "date_debut": "2026-06-01", "date_fin": "2026-09-19", "type_rapport": "Rapport"})
    stage.refresh_from_db()
    assert stage.intitule == "Stage démo"
    for url in ("admin:carnet_absence_add", "admin:carnet_entreejournal_add", "admin:carnet_stage_add"):
        assert client.get(reverse(url)).status_code == 403
    assert client.post(reverse("admin:carnet_stage_delete", args=[stage.pk]), {"post": "yes"}).status_code == 403
    assert Stage.objects.filter(pk=stage.pk).exists()


def test_note_rapide_refusee(client, demo):
    user, _ = demo
    client.force_login(user)
    page = client.get(reverse("carnet:note_rapide")).content.decode()
    assert "lecture seule" in page
    reponse = client.post(reverse("carnet:note_rapide"), {"texte": "Intrusion"})
    assert reponse.status_code == 403
    assert not EntreeJournal.objects.exists()


def test_tri_des_photos_refuse(client, demo):
    from django.core.files.uploadedfile import SimpleUploadedFile
    import io

    from PIL import Image

    user, stage = demo
    tampon = io.BytesIO()
    Image.new("RGB", (40, 30)).save(tampon, "JPEG")
    photo = Photo.ajouter(stage, SimpleUploadedFile("a.jpg", tampon.getvalue(), content_type="image/jpeg"))
    client.force_login(user)
    assert "lecture seule" in client.get(reverse("carnet:tri_photos")).content.decode()
    reponse = client.post(reverse("carnet:destination_photo", args=[photo.pk]), {"destination": "corps"})
    assert reponse.status_code == 403
    photo.refresh_from_db()
    assert photo.destination == Photo.Destination.A_TRIER


def test_export_permis_sans_ecrire_la_date_de_sauvegarde(client, demo):
    user, stage = demo
    client.force_login(user)
    reponse = client.get(reverse("carnet:export", args=[stage.pk]))
    assert reponse.status_code == 200
    b"".join(reponse.streaming_content)
    stage.refresh_from_db()
    assert stage.derniere_sauvegarde is None


def test_un_apprenant_ordinaire_ecrit_toujours(client, db, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    call_command("creer_groupes")
    awa = User.objects.create_user("awa", password="x")
    awa.profil.save()
    Stage.objects.create(proprietaire=awa, intitule="S", date_debut=D(2026, 6, 1), date_fin=D(2026, 9, 19))
    client.force_login(awa)
    client.post(reverse("carnet:note_rapide"), {"texte": "Note normale"})
    assert EntreeJournal.objects.filter(texte="Note normale").exists()


def test_charger_demo_donne_le_profil_demonstration(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    call_command("creer_groupes")
    call_command("charger_demo")
    assert User.objects.get(username=settings.COMPTE_DEMO).profil.role == Profil.Role.DEMONSTRATION


def test_migration_passe_le_compte_demo_en_lecture_seule(db, settings):
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    migration = importlib.import_module("comptes.migrations.0005_compte_demo_lecture_seule")
    etat = MigrationExecutor(connection).loader.project_state(("comptes", "0005_compte_demo_lecture_seule")).apps
    demo = User.objects.create_user(settings.COMPTE_DEMO, password="x")
    demo.groups.add(Group.objects.get_or_create(name="Apprenant")[0])
    migration.demo_en_lecture_seule(etat, None)
    demo.refresh_from_db()
    assert Profil.objects.get(user=demo).role == "demonstration"
    assert list(demo.groups.values_list("name", flat=True)) == ["Démonstration"]


def test_tableau_de_bord_annonce_la_lecture_seule(client, demo):
    user, _ = demo
    client.force_login(user)
    assert "lecture seule" in client.get(reverse("admin:index")).content.decode()


def test_tableau_de_bord_sans_bandeau_pour_un_apprenant(client, apprenant):
    client.force_login(apprenant)
    assert "lecture seule" not in client.get(reverse("admin:index")).content.decode()


def test_seul_l_administrateur_modifie_la_demo(client, demo, apprenant):
    """B21 : la démo n'est modifiable que par l'administrateur (superutilisateur)."""
    _, stage = demo
    donnees = {"intitule": "Démo corrigée", "date_debut": "2026-06-01", "date_fin": "2026-09-19",
               "type_rapport": "Rapport de stage", "jours_travailles": "[0, 1, 2, 3, 4, 5]", "quota_mo": 80}
    url = reverse("admin:carnet_stage_change", args=[stage.pk])
    client.force_login(apprenant)  # un autre apprenant ne voit même pas la démo
    assert client.get(url).status_code == 404
    racine = User.objects.create_superuser("root", password="x")
    client.force_login(racine)
    reponse = client.post(url, donnees)
    assert reponse.status_code == 302, reponse.context["adminform"].form.errors
    stage.refresh_from_db()
    assert stage.intitule == "Démo corrigée"
