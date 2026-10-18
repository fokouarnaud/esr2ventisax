from django.core.exceptions import ValidationError
from django.db import models

from .base import ModeleBase


class Absence(ModeleBase):
    """Absence ou jour férié (A30). Sans stage : férié fixe commun, répété chaque année (`annuel`)."""

    class Motif(models.TextChoices):
        FERIE = "ferie", "Jour férié"
        MALADIE = "maladie", "Maladie"
        CONGE = "conge", "Congé"
        INTEMPERIE = "intemperie", "Intempérie"
        COURS_CFP = "cours_cfp", "Cours au CFP"

    stage = models.ForeignKey("carnet.Stage", on_delete=models.CASCADE, null=True, blank=True, related_name="absences")
    date_debut = models.DateField("du")
    date_fin = models.DateField("au")
    motif = models.CharField(max_length=12, choices=Motif.choices)
    libelle = models.CharField("libellé", max_length=150, blank=True)
    annuel = models.BooleanField("se répète chaque année", default=False)

    class Meta:
        ordering = ["date_debut"]

    def __str__(self):
        return self.libelle or self.get_motif_display()

    def clean(self):
        if self.date_fin < self.date_debut:
            raise ValidationError({"date_fin": "La fin précède le début."})
