from django.core.exceptions import ValidationError
from django.db import models

from .base import ModeleDeStage
from .rubrique import Rubrique

AIDE_MARKDOWN = "Paragraphes séparés par une ligne vide ; listes « - » ou « 1. » ; **gras**."


def champ_texte(libelle):
    return models.TextField(libelle, blank=True, help_text=AIDE_MARKDOWN)


class Tache(ModeleDeStage):
    """Tâche réelle du stage, base du diagramme de Gantt (A26)."""

    libelle = models.CharField("libellé", max_length=200)
    date_debut = models.DateField("début")
    date_fin = models.DateField("fin", null=True, blank=True, help_text="Vide tant que la tâche est en cours.")
    lieu = models.ForeignKey("carnet.Lieu", on_delete=models.SET_NULL, null=True, blank=True)
    rubrique = models.ForeignKey(Rubrique, on_delete=models.SET_NULL, null=True, blank=True)
    description = champ_texte("description")

    class Meta:
        verbose_name = "tâche"
        ordering = ["date_debut"]

    def __str__(self):
        return self.libelle

    @property
    def fin_effective(self):
        return self.date_fin or self.stage.date_fin

    def clean(self):
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError({"date_fin": "La fin précède le début."})


class Equipement(ModeleDeStage):
    """Outillage, matériel, EPI ou appareil de mesure, saisi une fois et réutilisé (A27)."""

    class Categorie(models.TextChoices):
        OUTILLAGE = "outillage", "Outillage"
        MATERIEL = "materiel", "Matériel et matériaux"
        EPI = "epi", "Équipements de protection individuelle"
        MESURE = "mesure", "Appareils de mesure"

    designation = models.CharField("désignation", max_length=200)
    categorie = models.CharField("catégorie", max_length=20, choices=Categorie.choices)
    caracteristiques = models.CharField("caractéristiques", max_length=250, blank=True)
    role = models.CharField("rôle", max_length=250, blank=True)
    quantite = models.CharField("quantité", max_length=50, blank=True)
    photo = models.ForeignKey("carnet.Photo", on_delete=models.SET_NULL, null=True, blank=True)
    rubriques = models.ManyToManyField(Rubrique, blank=True)

    class Meta:
        verbose_name = "équipement"
        ordering = ["categorie", "designation"]

    def __str__(self):
        return self.designation


class Personne(ModeleDeStage):
    class Role(models.TextChoices):
        ENCADREUR_PRO = "encadreur_pro", "Encadreur professionnel"
        ENCADREUR_ACAD = "encadreur_acad", "Encadreur académique"
        COLLEGUE = "collegue", "Collègue"
        CLIENT = "client", "Client"
        AUTRE = "autre", "Autre"

    nom = models.CharField(max_length=150)
    fonction = models.CharField(max_length=150)
    role = models.CharField("rôle", max_length=20, choices=Role.choices, default=Role.COLLEGUE)
    telephone = models.CharField("téléphone (jamais exporté)", max_length=30, blank=True)
    a_remercier = models.BooleanField("à remercier", default=False)
    nom_publiable = models.BooleanField("nom publiable", default=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} ({self.fonction})"

    @property
    def nom_exporte(self):
        return self.nom if self.nom_publiable else f"le {self.fonction}"


class EntreeJournal(ModeleDeStage):
    """Note du journal : saisie rapide sur le terrain, complétée ensuite (A29, rapport d'activité p. 23)."""

    date = models.DateField()
    heure = models.TimeField(null=True, blank=True)
    texte = champ_texte("note")
    completee = models.BooleanField("complétée", default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    lieu = models.ForeignKey("carnet.Lieu", on_delete=models.SET_NULL, null=True, blank=True)
    tache = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="tâche")
    rubriques = models.ManyToManyField(Rubrique, blank=True, verbose_name="étiquettes")
    equipements = models.ManyToManyField(Equipement, blank=True, verbose_name="équipements")
    personnes = models.ManyToManyField(Personne, blank=True)

    objectifs = champ_texte("objectifs visés")
    moyens_humains = champ_texte("moyens humains")
    moyens_materiels = champ_texte("moyens matériels")
    methodologie = champ_texte("méthodologie")
    activites = champ_texte("activités développées")
    elements_theoriques = champ_texte("éléments théoriques et pratiques mis en exergue")
    difficultes = champ_texte("difficultés rencontrées")
    solutions = champ_texte("solutions préconisées")
    appreciation = champ_texte("éléments d'appréciation")

    intervention_nature = models.CharField("nature de l'intervention", max_length=200, blank=True)
    intervention_duree_h = models.DecimalField("durée d'immobilisation (h)", max_digits=6, decimal_places=2,
                                               null=True, blank=True)
    intervention_cout = models.DecimalField("coût (F CFA)", max_digits=12, decimal_places=0, null=True, blank=True)
    intervention_ressources = models.CharField("ressources mobilisées", max_length=250, blank=True)

    remarque_formateur = models.TextField("remarque du formateur", blank=True)

    class Meta:
        verbose_name = "note de journal"
        verbose_name_plural = "journal"
        ordering = ["-date", "-heure"]

    def __str__(self):
        return f"{self.date:%d/%m/%Y} : {self.texte[:60]}"

    def etiqueter(self, rubriques):
        """Remplace les étiquettes ; refuse un chapitre d'un autre stage."""
        autorisees = set(Rubrique.pour_stage(self.stage).values_list("pk", flat=True))
        if any(r.pk not in autorisees for r in rubriques):
            raise ValidationError("Une étiquette appartient à un autre stage.")
        self.rubriques.set(rubriques)
