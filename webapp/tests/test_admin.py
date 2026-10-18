"""US-01 à US-03 par HTTP : l'admin Unfold respecte le cloisonnement (DoD P5 §2)."""

import datetime

import pytest
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.urls import reverse

from carnet.models import EntreeJournal, Rubrique, Stage

D = datetime.date


@pytest.fixture(autouse=True)
def groupes(db):
    call_command("creer_groupes")


def compte(nom, groupe):
    user = User.objects.create_user(nom, password="x", is_staff=True)
    user.groups.add(Group.objects.get(name=groupe))
    return user


@pytest.fixture
def awa(db):
    return compte("awa2", "Apprenant")


@pytest.fixture
def bruno(db):
    return compte("bruno2", "Apprenant")


@pytest.fixture
def prof(db):
    return compte("prof", "Formateur")


@pytest.fixture
def stage_awa(awa, prof):
    return Stage.objects.create(proprietaire=awa, formateur_referent=prof, intitule="Stage Awa",
                                date_debut=D(2026, 3, 2), date_fin=D(2026, 6, 26))


@pytest.fixture
def stage_bruno(bruno):
    return Stage.objects.create(proprietaire=bruno, intitule="Stage Bruno", date_debut=D(2026, 3, 2),
                                date_fin=D(2026, 6, 26))


@pytest.fixture
def note_bruno(stage_bruno):
    return EntreeJournal.objects.create(stage=stage_bruno, date=D(2026, 3, 3), texte="Secret de Bruno")


@pytest.fixture
def note_awa(stage_awa):
    return EntreeJournal.objects.create(stage=stage_awa, date=D(2026, 3, 3), texte="Note d'Awa")


def url_modif(obj):
    return reverse(f"admin:carnet_{obj._meta.model_name}_change", args=[obj.pk])


def test_groupes_ont_les_bonnes_permissions(db):
    apprenant = Group.objects.get(name="Apprenant").permissions.values_list("codename", flat=True)
    formateur = Group.objects.get(name="Formateur").permissions.values_list("codename", flat=True)
    assert {"add_entreejournal", "change_stage", "delete_photo"} <= set(apprenant)
    assert {"view_stage", "change_entreejournal"} <= set(formateur)
    assert "change_stage" not in formateur and "add_entreejournal" not in formateur


def test_liste_du_journal_limitee_a_ses_notes(client, awa, note_awa, note_bruno):
    client.force_login(awa)
    page = client.get(reverse("admin:carnet_entreejournal_changelist")).content.decode()
    assert "Note d&#x27;Awa" in page or "Note d'Awa" in page
    assert "Secret de Bruno" not in page


@pytest.mark.parametrize("fabrique", ["note_bruno", "stage_bruno"])
def test_objet_d_un_autre_apprenant_introuvable_par_url(client, awa, request, fabrique):
    client.force_login(awa)
    assert client.get(url_modif(request.getfixturevalue(fabrique))).status_code == 404


def test_impossible_de_creer_une_note_dans_le_stage_d_un_autre(client, awa, stage_awa, stage_bruno):
    client.force_login(awa)
    client.post(reverse("admin:carnet_entreejournal_add"),
                {"stage": stage_bruno.pk, "date": "2026-03-04", "texte": "intrusion"})
    assert not EntreeJournal.objects.filter(texte="intrusion").exists()


def test_creer_un_stage_attribue_le_proprietaire(client, awa):
    client.force_login(awa)
    client.post(reverse("admin:carnet_stage_add"), {
        "intitule": "Nouveau", "date_debut": "2026-09-01", "date_fin": "2026-12-01", "type_rapport": "Rapport de stage",
        "jours_travailles": "[0, 1, 2, 3, 4, 5]", "quota_mo": 80,
    })
    assert Stage.objects.get(intitule="Nouveau").proprietaire == awa


def test_formateur_referent_ne_modifie_que_la_remarque(client, prof, note_awa):
    client.force_login(prof)
    assert client.get(url_modif(note_awa)).status_code == 200
    client.post(url_modif(note_awa), {"texte": "réécrit", "date": "2026-03-03",
                                      "remarque_formateur": "Préciser le diamètre."})
    note_awa.refresh_from_db()
    assert note_awa.remarque_formateur == "Préciser le diamètre."
    assert note_awa.texte == "Note d'Awa"


def test_formateur_non_referent_ne_voit_pas_la_note(client, prof, note_bruno):
    client.force_login(prof)
    assert client.get(url_modif(note_bruno)).status_code == 404


def test_rubrique_du_cours_non_modifiable_par_l_apprenant(client, awa):
    client.force_login(awa)
    rubrique = Rubrique.objects.get(code="entreprise.historique")
    client.post(url_modif(rubrique), {"libelle": "Piraté", "partie": "entreprise", "ordre": 0})
    rubrique.refresh_from_db()
    assert rubrique.libelle == "Historique de l'entreprise"


def test_tableau_de_bord_affiche_les_indicateurs_du_stage_actif(client, awa, stage_awa, note_awa):
    client.force_login(awa)
    page = client.get(reverse("admin:index")).content.decode()
    assert "Stage Awa" in page
    assert "Notes à compléter" in page
