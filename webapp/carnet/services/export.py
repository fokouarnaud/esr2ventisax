"""Zip « dossier terrain » (contrat P4) : sert à la rédaction locale et de sauvegarde restaurable (A4, A16)."""

import hashlib
import io
import json
import zipfile

from django.core import serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.utils import timezone
from PIL import Image

from carnet.models import (
    Abreviation, Absence, DonneeTechnique, EntreeJournal, Equipement, Lieu, NoeudOrganigramme, Personne,
    Photo, Reference, Rubrique, Stage, Tache,
)

from . import generateurs
from .terrain_md import terrain_md

VERSION_FORMAT = 1
CHAMPS_JAMAIS_EXPORTES = {"carnet.personne": {"telephone"}}  # A36


class ExportImpossible(Exception):
    pass


def _objets_du_stage(stage):
    """Ordre compatible avec les clés étrangères pour la restauration."""
    return [
        stage, stage.fiche_entreprise, stage.mission, stage.bilan,
        *Rubrique.objects.filter(stage=stage, parent__isnull=True),
        *Rubrique.objects.filter(stage=stage, parent__isnull=False),
        *Lieu.objects.filter(stage=stage),
        *Tache.objects.filter(stage=stage),
        *Personne.objects.filter(stage=stage),
        *Reference.objects.filter(stage=stage),
        *Abreviation.objects.filter(stage=stage),
        *NoeudOrganigramme.objects.filter(stage=stage).order_by("parent_id"),
        *Absence.objects.filter(stage=stage),
        *EntreeJournal.objects.filter(stage=stage),
        *Photo.objects.filter(stage=stage),
        *Equipement.objects.filter(stage=stage),
        *DonneeTechnique.objects.filter(stage=stage),
    ]


def _serialiser(stage):
    donnees = serializers.serialize("python", _objets_du_stage(stage))
    for objet in donnees:
        for champ in CHAMPS_JAMAIS_EXPORTES.get(objet["model"], ()):
            objet["fields"].pop(champ, None)
    return json.dumps(donnees, cls=DjangoJSONEncoder, ensure_ascii=False, indent=1)


def _problemes(stage):
    return [f"photo « {p} » : {', '.join(p.problemes_export())}"
            for p in Photo.objects.filter(stage=stage) if p.problemes_export()]


def _en_png(contenu):
    """La couverture du modèle attend img/logo_*.png, quel que soit le format envoyé."""
    tampon = io.BytesIO()
    Image.open(io.BytesIO(contenu)).save(tampon, "PNG")
    return tampon.getvalue()


class _FluxSansRetour:
    """Fichier en écriture seule : `zipfile` y écrit sans `seek`, on récupère les octets au fil de l'eau."""

    def __init__(self):
        self._morceaux, self._position = [], 0

    def write(self, donnees):
        self._morceaux.append(bytes(donnees))
        self._position += len(donnees)
        return len(donnees)

    def tell(self):
        return self._position

    def flush(self):
        pass

    def vider(self):
        morceaux, self._morceaux = self._morceaux, []
        return b"".join(morceaux)


def verifier_exportable(stage):
    problemes = _problemes(stage)
    if problemes:
        raise ExportImpossible("Export impossible : " + " ; ".join(problemes))


def iter_zip(stage):
    """Génère le zip morceau par morceau (A33 : rien n'est stocké sur le serveur). Vérifie avant de commencer."""
    verifier_exportable(stage)
    return _generer(stage)


def _generer(stage):
    sommes, flux = {}, _FluxSansRetour()

    with zipfile.ZipFile(flux, "w", zipfile.ZIP_DEFLATED) as z:
        def ajouter(nom, contenu, compresser=True):
            if isinstance(contenu, str):
                contenu = contenu.encode("utf-8")
            sommes[nom] = hashlib.sha256(contenu).hexdigest()
            z.writestr(nom, contenu, zipfile.ZIP_DEFLATED if compresser else zipfile.ZIP_STORED)
            return flux.vider()

        yield ajouter("terrain.json", _serialiser(stage))
        yield ajouter("terrain.md", terrain_md(stage))
        yield ajouter("config/infos.tex", generateurs.infos_tex(stage))
        yield ajouter("bib/references.bib", generateurs.bibtex(stage))
        for nom, contenu in (("figures/organigramme.tex", generateurs.organigramme_tikz(stage)),
                             ("figures/gantt.tex", generateurs.gantt_tikz(stage))):
            if contenu:
                yield ajouter(nom, contenu)
        for categorie, tableau in generateurs.tableaux_equipements(stage).items():
            yield ajouter(f"tableaux/equipements_{categorie}.tex", tableau)

        for photo in Photo.objects.filter(stage=stage):
            contenu = photo.fichier.read()
            photo.fichier.close()
            yield ajouter(f"sauvegarde/{photo.fichier.name}", contenu, compresser=False)
            if photo.destination in (Photo.Destination.CORPS, Photo.Destination.ANNEXE):
                yield ajouter(f"img/fig_{photo.slug}.jpg", contenu, compresser=False)
        for champ in ("logo_entreprise", "logo_cfp"):
            logo = getattr(stage, champ)
            if logo:
                contenu = logo.read()
                logo.close()
                yield ajouter(f"sauvegarde/{logo.name}", contenu, compresser=False)
                yield ajouter(f"img/{champ}.png", _en_png(contenu), compresser=False)

        manifeste = {"format": VERSION_FORMAT, "stage": str(stage.pk), "slug": stage.slug,
                     "exporte_le": timezone.now().isoformat(), "fichiers": sommes}
        z.writestr("manifest.json", json.dumps(manifeste, ensure_ascii=False, indent=1))
    yield flux.vider()

    Stage.objects.filter(pk=stage.pk).update(derniere_sauvegarde=timezone.now())


def ecrire_zip(stage, flux):
    for morceau in iter_zip(stage):
        flux.write(morceau)


@transaction.atomic
def restaurer(zip_ouvert, proprietaire):
    """Restaure un zip produit par `ecrire_zip`. Idempotent : les UUID sont conservés."""
    donnees = json.loads(zip_ouvert.read("terrain.json"))
    for objet in donnees:
        if objet["model"] == "carnet.stage":
            objet["fields"]["proprietaire"] = proprietaire.pk
            objet["fields"]["formateur_referent"] = None
    stage_pk = None
    for objet in serializers.deserialize("python", donnees):
        objet.save()
        if isinstance(objet.object, Stage):
            stage_pk = objet.object.pk

    for nom in zip_ouvert.namelist():
        if nom.startswith("sauvegarde/"):
            chemin = nom.removeprefix("sauvegarde/")
            if default_storage.exists(chemin):
                default_storage.delete(chemin)
            default_storage.save(chemin, ContentFile(zip_ouvert.read(nom)))
    return Stage.objects.get(pk=stage_pk)
