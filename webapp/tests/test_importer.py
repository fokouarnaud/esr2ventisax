"""US-29 : import local du zip dans rapports/<slug>-<uuid8>/ (A15, A21, A31)."""

import functools
import http.server
import io
import json
import threading
import zipfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from PIL import Image

from carnet.models import Lieu, Photo
from carnet.services.cartes import generer_plan_situation
from carnet.services.export import ecrire_zip


def jpeg():
    tampon = io.BytesIO()
    Image.new("RGB", (40, 30), (0, 90, 0)).save(tampon, "JPEG")
    return tampon.getvalue()


@pytest.fixture(autouse=True)
def media_temporaire(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def modele(tmp_path):
    racine = tmp_path / "tex_export_src"
    (racine / "config").mkdir(parents=True)
    (racine / "img").mkdir()
    (racine / "outils" / "_build").mkdir(parents=True)
    (racine / "main.tex").write_text(r"\input{config/infos}", encoding="utf-8")
    (racine / "config" / "infos.tex").write_text(r"\newcommand{\InfoCFP}{ANCIEN}", encoding="utf-8")
    (racine / "img" / "fig_factice.png").write_bytes(b"png")
    (racine / "main.aux").write_text("x")
    (racine / "main.pdf").write_bytes(b"%PDF")
    (racine / "outils" / "_build" / "x.pdf").write_bytes(b"%PDF")
    return racine


@pytest.fixture
def archive(stage, tmp_path):
    stage.cfp = "CFP de Bonabéri"
    stage.save()
    Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg()), slug="colonne", legende="Colonne",
                  destination=Photo.Destination.CORPS)
    chemin = tmp_path / "dossier.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    return chemin


def importer(archive, modele, tmp_path, *options):
    call_command("importer_dossier", str(archive), "--modele", str(modele),
                 "--destination", str(tmp_path / "rapports"), "--sans-carte", *options)
    (dossier,) = (tmp_path / "rapports").iterdir()
    return dossier


def test_dossier_nomme_slug_et_debut_d_uuid(archive, modele, tmp_path, stage):
    dossier = importer(archive, modele, tmp_path)
    assert dossier.name == f"{stage.slug}-{str(stage.pk)[:8]}"


def test_copie_le_modele_et_remplace_infos(archive, modele, tmp_path):
    dossier = importer(archive, modele, tmp_path)
    assert (dossier / "main.tex").exists()
    assert "CFP de Bonabéri" in (dossier / "config" / "infos.tex").read_text(encoding="utf-8")


def test_photos_retenues_et_donnees_terrain_deposees(archive, modele, tmp_path):
    dossier = importer(archive, modele, tmp_path)
    assert (dossier / "img" / "fig_colonne.jpg").exists()
    assert (dossier / "donnees_terrain" / "terrain.md").exists()
    assert (dossier / "donnees_terrain" / "terrain.json").exists()
    assert not (dossier / "sauvegarde").exists()


def test_fichiers_de_compilation_du_modele_non_copies(archive, modele, tmp_path):
    dossier = importer(archive, modele, tmp_path)
    assert not (dossier / "main.aux").exists()
    assert not (dossier / "main.pdf").exists()
    assert not (dossier / "outils" / "_build").exists()


def test_refuse_d_ecraser_sans_force(archive, modele, tmp_path):
    importer(archive, modele, tmp_path)
    with pytest.raises(CommandError):
        importer(archive, modele, tmp_path)


def test_force_ecrase_le_dossier(archive, modele, tmp_path):
    dossier = importer(archive, modele, tmp_path)
    (dossier / "brouillon.tex").write_text("x")
    dossier = importer(archive, modele, tmp_path, "--force")
    assert not (dossier / "brouillon.tex").exists()


def test_archive_alteree_refusee(archive, modele, tmp_path):
    alteree = tmp_path / "alteree.zip"
    with zipfile.ZipFile(archive) as src, zipfile.ZipFile(alteree, "w") as dst:
        for nom in src.namelist():
            contenu = src.read(nom)
            dst.writestr(nom, b"% falsifie\n" + contenu if nom == "config/infos.tex" else contenu)
    with pytest.raises(CommandError, match="infos.tex"):
        importer(alteree, modele, tmp_path)


# --- Plan de situation (A31), contre un serveur de tuiles local -------------------------

@pytest.fixture
def serveur_tuiles(tmp_path):
    tuiles = tmp_path / "tuiles"
    tuiles.mkdir()
    tampon = io.BytesIO()
    Image.new("RGB", (256, 256), (220, 230, 240)).save(tampon, "PNG")
    (tuiles / "tuile.png").write_bytes(tampon.getvalue())

    class Gestionnaire(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            return str(tuiles / "tuile.png")

        def log_message(self, *args):
            pass

    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Gestionnaire))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{serveur.server_port}/{{z}}/{{x}}/{{y}}.png"
    serveur.shutdown()
    serveur.server_close()


def test_plan_de_situation_png_avec_repere(tmp_path, serveur_tuiles):
    sortie = tmp_path / "plan.png"
    generer_plan_situation(4.05, 9.70, sortie, url_tuiles=serveur_tuiles)
    image = Image.open(sortie).convert("RGB")
    assert image.size == (800, 500)
    assert image.getpixel((400, 250)) != (220, 230, 240)  # le repère est au centre


def test_import_genere_un_plan_par_lieu(stage, modele, tmp_path, serveur_tuiles):
    Lieu.objects.create(stage=stage, nom="Siège Akwa", type=Lieu.Type.SIEGE, latitude=4.05, longitude=9.70)
    chemin = tmp_path / "d.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    call_command("importer_dossier", str(chemin), "--modele", str(modele),
                 "--destination", str(tmp_path / "rapports"), "--url-tuiles", serveur_tuiles)
    (dossier,) = (tmp_path / "rapports").iterdir()
    assert (dossier / "img" / "plan_situation_siege-akwa.png").exists()


def test_bibliographie_du_modele_conservee_et_completee(stage, modele, tmp_path):
    from carnet.models import Reference

    (modele / "bib").mkdir()
    (modele / "bib" / "references.bib").write_text("@misc{coursModule2,\n  title = {Cours}\n}\n", encoding="utf-8")
    Reference.objects.create(stage=stage, auteur="AFNOR", titre="DTU", annee=2013)
    chemin = tmp_path / "d.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    dossier = importer(chemin, modele, tmp_path)
    bib = (dossier / "bib" / "references.bib").read_text(encoding="utf-8")
    assert "@misc{coursModule2," in bib
    assert "@book{afnor2013," in bib  # type « ouvrage » par défaut


def test_catalogue_de_verification_inclut_tous_les_fragments(stage, modele, tmp_path):
    from carnet.models import Equipement

    Equipement.objects.create(stage=stage, designation="Casque", categorie="epi")
    Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg()), slug="pose", legende="Pose",
                  destination=Photo.Destination.ANNEXE)
    chemin = tmp_path / "d.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    catalogue = (importer(chemin, modele, tmp_path) / "donnees_terrain" / "catalogue.tex").read_text(encoding="utf-8")
    assert r"\input{tableaux/equipements_epi}" in catalogue
    assert r"\includegraphics[width=0.6\linewidth]{img/fig_pose.jpg}" in catalogue
    assert r"\caption{Pose}" in catalogue


def test_photo_reelle_remplace_l_image_factice_de_meme_nom(stage, modele, tmp_path):
    (modele / "img" / "fig_colonne.png").write_bytes(b"png factice")
    Photo.ajouter(stage, SimpleUploadedFile("a.jpg", jpeg()), slug="colonne", legende="Colonne",
                  destination=Photo.Destination.CORPS)
    chemin = tmp_path / "d.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    dossier = importer(chemin, modele, tmp_path)
    assert (dossier / "img" / "fig_colonne.jpg").exists()
    assert not (dossier / "img" / "fig_colonne.png").exists()  # \includegraphics sans extension prend la photo
    assert (dossier / "img" / "fig_factice.png").exists()


def test_plan_du_siege_remplace_la_figure_de_localisation(stage, modele, tmp_path, serveur_tuiles):
    (modele / "img" / "fig_localisation.png").write_bytes(b"png factice")
    Lieu.objects.create(stage=stage, nom="Siège Akwa", type=Lieu.Type.SIEGE, latitude=4.05, longitude=9.70)
    chemin = tmp_path / "d.zip"
    with open(chemin, "wb") as f:
        ecrire_zip(stage, f)
    call_command("importer_dossier", str(chemin), "--modele", str(modele),
                 "--destination", str(tmp_path / "rapports"), "--url-tuiles", serveur_tuiles)
    (dossier,) = (tmp_path / "rapports").iterdir()
    assert Image.open(dossier / "img" / "fig_localisation.png").size == (800, 500)
