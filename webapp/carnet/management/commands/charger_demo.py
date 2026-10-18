"""Crée (ou recrée) le compte demo.apprenant et un stage fictif complet, prêt à exporter."""

import datetime
import io
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from carnet.acces import GROUPE_APPRENANT
from carnet.demo import donnees as demo
from carnet.demo.images import illustration, logo
from carnet.models import (
    Abreviation, DonneeTechnique, EntreeJournal, Equipement, Lieu, NoeudOrganigramme, Personne, Photo, Reference,
    Rubrique, Stage, Tache,
)
from carnet.services import calendrier
from carnet.services.export import ecrire_zip

SEMAINE = datetime.timedelta(days=7)


class Command(BaseCommand):
    help = "Crée demo.apprenant et un stage de démonstration complet (idempotent : le stage est recréé)."

    def add_arguments(self, parser):
        parser.add_argument("--mot-de-passe", default=demo.MOT_DE_PASSE)
        parser.add_argument("--zip", help="Écrit aussi le dossier terrain de la démo à ce chemin.")

    def handle(self, *args, **opts):
        call_command("creer_groupes", stdout=io.StringIO())
        user = self._compte(opts["mot_de_passe"])
        self._supprimer_stages(user)
        with transaction.atomic():
            stage = self._stage(user)
        if opts["zip"]:
            with open(opts["zip"], "wb") as f:
                ecrire_zip(stage, f)
        self.stdout.write(self.style.SUCCESS(f"Démo prête : {demo.IDENTIFIANT} / stage « {stage} »"))

    # --- Compte ----------------------------------------------------------------------------

    def _compte(self, mot_de_passe):
        user, _ = get_user_model().objects.get_or_create(username=demo.IDENTIFIANT)
        user.first_name, user.last_name = "Apprenant", "DEMO"
        user.is_staff, user.is_superuser, user.is_active = True, False, True
        user.set_password(mot_de_passe)
        user.save()
        user.groups.add(Group.objects.get(name=GROUPE_APPRENANT))
        return user

    @staticmethod
    def _supprimer_stages(user):
        """Supprime aussi les fichiers : relancer la commande ne doit pas remplir le disque (A33)."""
        for stage in Stage.objects.filter(proprietaire=user):
            for photo in Photo.objects.filter(stage=stage):
                photo.fichier.delete(save=False)
            for champ in (stage.logo_entreprise, stage.logo_cfp):
                if champ:
                    champ.delete(save=False)
            stage.delete()

    # --- Stage -----------------------------------------------------------------------------

    def _stage(self, user):
        stage = Stage.objects.create(proprietaire=user, **demo.STAGE)
        stage.logo_entreprise.save("logo_entreprise_demo.png", ContentFile(logo("ED", "DÉMO")), save=False)
        stage.logo_cfp.save("logo_cfp_demo.png", ContentFile(logo("CFP", "DÉMO", (13, 102, 94), (252, 254, 254))),
                            save=False)
        stage.save()
        for formulaire, valeurs in ((stage.fiche_entreprise, demo.FICHE), (stage.mission, demo.MISSION),
                                    (stage.bilan, demo.BILAN)):
            for champ, valeur in valeurs.items():
                setattr(formulaire, champ, valeur)
            formulaire.save()

        lieux = {l["cle"]: Lieu.objects.create(stage=stage, **{k: v for k, v in l.items() if k != "cle"})
                 for l in demo.LIEUX}
        personnes = {cle: Personne.objects.create(stage=stage, nom=nom, fonction=fonction, role=role,
                                                  a_remercier=merci)
                     for cle, nom, fonction, role, merci in demo.PERSONNES}
        for sigle, signification in demo.ABREVIATIONS:
            Abreviation.objects.create(stage=stage, sigle=sigle, signification=signification)
        references = {cle: Reference.objects.create(stage=stage, type=t, auteur=auteur, titre=titre, annee=annee,
                                                    editeur=editeur, url=url)
                      for cle, t, auteur, titre, annee, editeur, url in demo.REFERENCES}
        noeuds = {}
        for ordre, (cle, poste, nom, parent, stagiaire) in enumerate(demo.ORGANIGRAMME):
            noeuds[cle] = NoeudOrganigramme.objects.create(stage=stage, poste=poste, nom=nom, parent=noeuds.get(parent),
                                                          est_stagiaire=stagiaire, ordre=ordre)
        chapitres = {cle: Rubrique.objects.create(stage=stage, code=f"theme.{cle}", libelle=libelle, ordre=i)
                     for i, (cle, libelle) in enumerate(demo.CHAPITRES)}
        cours = {r.code: r for r in Rubrique.objects.filter(stage__isnull=True)}

        photos = self._photos(stage, lieux["chantier"], chapitres)
        equipements = self._equipements(stage, photos)
        self._journal(stage, lieux["chantier"], personnes, equipements, chapitres, cours)
        self._donnees(stage, references)
        return stage

    def _photos(self, stage, chantier, chapitres):
        photos = {}
        for slug, legende, destination, sujet, chapitre in demo.PHOTOS:
            photo = Photo.ajouter(stage, SimpleUploadedFile(f"{slug}.jpg", illustration(sujet, legende)),
                                  latitude=chantier.latitude, longitude=chantier.longitude, lieu=chantier,
                                  slug=slug, legende=legende, destination=destination)
            photo.rubriques.add(chapitres[chapitre])
            photos[slug] = photo
        return photos

    @staticmethod
    def _equipements(stage, photos):
        equipements = []
        for designation, categorie, caracteristiques, role, quantite, slug in demo.EQUIPEMENTS:
            equipements.append(Equipement.objects.create(
                stage=stage, designation=designation, categorie=categorie, caracteristiques=caracteristiques,
                role=role, quantite=quantite, photo=photos.get(slug)))
        return equipements

    def _journal(self, stage, chantier, personnes, equipements, chapitres, cours):
        """Une note complétée par jour travaillé, rédigée à partir de la tâche en cours."""
        jours = calendrier.jours_prevus(stage)
        taches = []
        for t in demo.TACHES:
            debut, fin = t["semaines"]
            tache = Tache.objects.create(
                stage=stage, libelle=t["libelle"], date_debut=demo.DEBUT + debut * SEMAINE,
                date_fin=demo.DEBUT + fin * SEMAINE - datetime.timedelta(days=2), lieu=chantier,
                rubrique=chapitres[t["chapitre"]], description=t["objectifs"])
            taches.append(tache)
            periode = [j for j in jours if tache.date_debut <= j <= tache.date_fin]
            for i, jour in enumerate(periode):
                note = EntreeJournal.objects.create(
                    stage=stage, date=jour, heure=datetime.time(16, 30), lieu=chantier, tache=tache,
                    latitude=chantier.latitude, longitude=chantier.longitude, completee=True,
                    texte=f"{t['libelle']} : {t['activites'][i % len(t['activites'])]}",
                    objectifs=t["objectifs"],
                    moyens_humains="Chef d'équipe plomberie, deux techniciens, un manœuvre et le stagiaire.",
                    moyens_materiels=", ".join(e.designation for e in equipements[i % 4::4][:3]),
                    methodologie=t["methodologie"], activites="\n".join(f"- {a}" for a in t["activites"]),
                    elements_theoriques=t["theorie"], difficultes=t["difficultes"], solutions=t["solutions"],
                    appreciation="Travail réalisé dans les délais et contrôlé par le chef d'équipe.")
                etiquettes = [chapitres[t["chapitre"]]]
                if i == 0:
                    etiquettes += [cours[c] for c in t["rubriques"]]
                note.rubriques.set(etiquettes)
                note.personnes.set([personnes["cep"], personnes["ct"] if i % 3 == 0 else personnes["cdp"]])
                note.equipements.set(equipements[i % 4::4][:3])
        premiere = EntreeJournal.objects.filter(stage=stage).order_by("date").first()
        premiere.intervention_nature = "Reprise d'un assemblage PPR défectueux"
        premiere.intervention_duree_h, premiere.intervention_cout = Decimal("3"), Decimal("15000")
        premiere.intervention_ressources = "Polyfuseur, un raccord de 40 mm, deux techniciens"
        premiere.save()
        return taches

    @staticmethod
    def _donnees(stage, references):
        for grandeur, valeur, unite, nature, cle, date in demo.DONNEES:
            entree = None
            if nature == DonneeTechnique.Nature.RELEVE:
                entree = EntreeJournal.objects.filter(stage=stage, date__gte=date).order_by("date").first()
            DonneeTechnique.objects.create(
                stage=stage, grandeur=grandeur, valeur=Decimal(valeur), unite=unite, nature=nature, date=date,
                entree=entree, reference=references.get(cle))
        Stage.objects.filter(pk=stage.pk).update(derniere_sauvegarde=timezone.now())
