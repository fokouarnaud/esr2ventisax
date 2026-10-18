"""Import local d'un zip « dossier terrain » dans rapports/<slug>-<uuid8>/ (A15, A21, A31)."""

import fnmatch
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from carnet.services.cartes import URL_TUILES_OSM, generer_plan_situation
from carnet.services.catalogue import ecrire_catalogue

RACINE_DEPOT = settings.BASE_DIR.parent
IGNORES = ["*.aux", "*.bbl", "*.bcf", "*.blg", "*.fdb_latexmk", "*.fls", "*.lof", "*.log", "*.lot", "*.out",
           "*.run.xml", "*.synctex.gz", "*.toc", "main.pdf", "presentation.pptx", "_build", "__pycache__"]
VERS_DONNEES = {"terrain.json", "terrain.md", "manifest.json"}
CLE_BIB = re.compile(r"^@\w+\{([^,]+),", re.MULTILINE)


class Command(BaseCommand):
    help = "Copie le modèle tex_export_src/ dans rapports/<slug>-<uuid8>/ et y dépose le dossier terrain."

    def add_arguments(self, parser):
        parser.add_argument("archive")
        parser.add_argument("--modele", default=str(RACINE_DEPOT / "tex_export_src"))
        parser.add_argument("--destination", default=str(RACINE_DEPOT / "rapports"))
        parser.add_argument("--force", action="store_true", help="Écrase un dossier existant.")
        parser.add_argument("--sans-carte", action="store_true", help="Ne génère pas les plans de situation.")
        parser.add_argument("--url-tuiles", default=URL_TUILES_OSM)

    def handle(self, *args, **opts):
        with zipfile.ZipFile(opts["archive"]) as z:
            manifeste = json.loads(z.read("manifest.json"))
            self._verifier(z, manifeste)
            dossier = Path(opts["destination"]) / f"{manifeste['slug']}-{manifeste['stage'][:8]}"
            if dossier.exists():
                if not opts["force"]:
                    raise CommandError(f"{dossier} existe déjà : relancer avec --force pour l'écraser.")
                shutil.rmtree(dossier)
            shutil.copytree(opts["modele"], dossier, ignore=self._ignorer)
            bib_modele = self._lire(dossier / "bib" / "references.bib")
            self._extraire(z, dossier)
            self._fusionner_bib(dossier / "bib" / "references.bib", bib_modele)
            ecrire_catalogue(dossier, json.loads(z.read("terrain.json")))
            if not opts["sans_carte"]:
                self._plans(json.loads(z.read("terrain.json")), dossier, opts["url_tuiles"])
        self.stdout.write(self.style.SUCCESS(f"Rapport prêt : {dossier}"))

    @staticmethod
    def _ignorer(_dossier, noms):
        return {n for n in noms if any(fnmatch.fnmatch(n, motif) for motif in IGNORES)}

    @staticmethod
    def _lire(chemin):
        return chemin.read_text(encoding="utf-8") if chemin.exists() else ""

    @staticmethod
    def _fusionner_bib(chemin, bib_modele):
        """Garde les entrées du modèle (dont le cours, cité par main.tex) et ajoute celles du stage."""
        bib_stage = chemin.read_text(encoding="utf-8") if chemin.exists() else ""
        deja = set(CLE_BIB.findall(bib_modele))
        entrees = [e.strip() + "\n" for e in re.split(r"\n(?=@)", bib_stage.strip())
                   if CLE_BIB.match(e) and CLE_BIB.match(e).group(1) not in deja]
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(bib_modele.rstrip() + "\n\n" + "\n".join(entrees), encoding="utf-8")

    @staticmethod
    def _verifier(z, manifeste):
        for nom, somme in manifeste["fichiers"].items():
            if hashlib.sha256(z.read(nom)).hexdigest() != somme:
                raise CommandError(f"Archive altérée : somme de contrôle invalide pour {nom}.")

    @staticmethod
    def _extraire(z, dossier):
        racine = dossier.resolve()
        for nom in z.namelist():
            if nom.startswith("sauvegarde/") or nom.endswith("/"):
                continue
            relatif = f"donnees_terrain/{nom}" if nom in VERS_DONNEES else nom
            cible = (dossier / relatif).resolve()
            if not cible.is_relative_to(racine):
                raise CommandError(f"Chemin interdit dans l'archive : {nom}")
            cible.parent.mkdir(parents=True, exist_ok=True)
            cible.write_bytes(z.read(nom))
            if nom.startswith("img/fig_") and cible.suffix == ".jpg":
                # Le modèle appelle \includegraphics sans extension : la photo réelle prend la place de la factice
                cible.with_suffix(".png").unlink(missing_ok=True)

    def _plans(self, donnees, dossier, url_tuiles):
        for objet in donnees:
            if objet["model"] != "carnet.lieu":
                continue
            champs = objet["fields"]
            sortie = dossier / "img" / f"plan_situation_{slugify(champs['nom'])}.png"
            try:
                generer_plan_situation(champs["latitude"], champs["longitude"], sortie, url_tuiles=url_tuiles)
            except Exception as exc:  # réseau indisponible : le rapport reste utilisable
                self.stderr.write(f"Plan de situation non généré pour {champs['nom']} : {exc}")
                continue
            if champs["type"] == "siege":  # figure « plan de localisation du siège » de la Partie I
                shutil.copyfile(sortie, dossier / "img" / "fig_localisation.png")
