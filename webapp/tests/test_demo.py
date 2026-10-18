"""Jeu de démonstration (`charger_demo`) : un stage fictif complet qui produit le rapport entier, sans \\AC{}."""

import zipfile

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from carnet.models import EntreeJournal, Lieu, NoeudOrganigramme, Photo, Reference, Stage, Tache
from carnet.services import generateurs
from carnet.services.export import verifier_exportable
from carnet.services.tableau_de_bord import rubriques_vides

# Images du modèle tex_export_src/ que la démo remplace par ses propres photos
FIGURES_DU_MODELE = {
    "condensats_split", "coupe_tube", "epi_chantier", "essai_etancheite", "facade_chantier", "flexible",
    "isolation_pose", "manometre", "polyfuseur", "reducteur_montage", "reducteur_pression",
}


@pytest.fixture(autouse=True)
def media_temporaire(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def demo(db):
    call_command("charger_demo")
    return Stage.objects.get(proprietaire__username="demo.apprenant")


def test_compte_demo_apprenant(demo):
    user = User.objects.get(username="demo.apprenant")
    assert user.check_password("demo-local-2026")
    assert user.is_staff and not user.is_superuser
    assert user.groups.filter(name="Apprenant").exists()


def test_mot_de_passe_reglable(db):
    call_command("charger_demo", "--mot-de-passe", "autre-secret")
    assert User.objects.get(username="demo.apprenant").check_password("autre-secret")


def test_infos_tex_sans_aucun_champ_a_completer(demo):
    macros = [l for l in generateurs.infos_tex(demo).splitlines() if not l.startswith("%")]
    assert not [l for l in macros if r"\AC{" in l]
    assert "Entreprise de démonstration" in generateurs.infos_tex(demo)


def test_stage_complet_et_exportable(demo):
    verifier_exportable(demo)
    assert demo.logo_entreprise and demo.logo_cfp
    assert rubriques_vides(demo) == []
    assert not EntreeJournal.objects.filter(stage=demo, completee=False).exists()
    assert NoeudOrganigramme.objects.filter(stage=demo, est_stagiaire=True).count() == 1
    assert Tache.objects.filter(stage=demo).count() == 10
    assert Reference.objects.filter(stage=demo).count() >= 5
    assert Lieu.objects.filter(stage=demo, type=Lieu.Type.SIEGE).exists()
    assert all(demo.bilan.__dict__[f] for f in ("critiques", "suggestions", "pourquoi_ce_stage"))


def test_photos_remplacent_les_figures_du_modele(demo):
    slugs = set(Photo.objects.filter(stage=demo, destination__in=["corps", "annexe"]).values_list("slug", flat=True))
    assert FIGURES_DU_MODELE <= slugs


def test_idempotent(demo):
    avant = (Stage.objects.count(), Photo.objects.count(), EntreeJournal.objects.count(), User.objects.count())
    call_command("charger_demo")
    apres = (Stage.objects.count(), Photo.objects.count(), EntreeJournal.objects.count(), User.objects.count())
    assert avant == apres


def test_option_zip_ecrit_le_dossier_terrain(db, tmp_path):
    chemin = tmp_path / "demo.zip"
    call_command("charger_demo", "--zip", str(chemin))
    with zipfile.ZipFile(chemin) as z:
        noms = set(z.namelist())
    assert {"config/infos.tex", "figures/organigramme.tex", "figures/gantt.tex", "img/logo_entreprise.png",
            "img/fig_manometre.jpg"} <= noms


def test_rediger_demo_remplace_les_champs_a_completer_des_parties(tmp_path):
    parties = tmp_path / "parties"
    parties.mkdir()
    (parties / "p1.tex").write_text(r"\AC{Nom} & Magasinier \\" + "\n" + r"CA : \AC{montant}.", encoding="utf-8")
    call_command("rediger_demo", str(tmp_path))
    texte = (parties / "p1.tex").read_text(encoding="utf-8")
    assert texte == r"M. STOCK Félix & Magasinier \\" + "\n" + "CA : 450 millions de F CFA (2025)."


def test_rediger_demo_signale_un_champ_inconnu(tmp_path):
    from django.core.management import CommandError

    (tmp_path / "parties").mkdir()
    (tmp_path / "parties" / "p.tex").write_text(r"\AC{inconnu}", encoding="utf-8")
    with pytest.raises(CommandError, match="inconnu"):
        call_command("rediger_demo", str(tmp_path))
