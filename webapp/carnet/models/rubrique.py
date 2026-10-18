from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .base import ModeleBase


class Rubrique(ModeleBase):
    """Deux niveaux (A24) : rubriques du cours (stage vide, figées) et chapitres du thème d'un stage."""

    class Partie(models.TextChoices):
        INTRODUCTION = "introduction", "Introduction"
        ENTREPRISE = "entreprise", "Partie I : Entreprise"
        MISSION = "mission", "Partie II : Mission"
        THEME = "theme", "Partie III : Thème"
        CRITIQUES = "critiques", "Partie IV : Critiques et suggestions"
        CONCLUSION = "conclusion", "Conclusion"
        BILAN = "bilan", "Bilan personnel"
        ANNEXES = "annexes", "Annexes"

    stage = models.ForeignKey(
        "carnet.Stage", on_delete=models.CASCADE, null=True, blank=True, related_name="chapitres"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="sous_rubriques"
    )
    code = models.CharField(max_length=80, blank=True)
    libelle = models.CharField("libellé", max_length=200)
    partie = models.CharField(max_length=20, choices=Partie.choices, default=Partie.THEME)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["partie", "ordre", "libelle"]

    def __str__(self):
        return f"{self.parent.libelle} › {self.libelle}" if self.parent_id else self.libelle

    @property
    def est_du_cours(self):
        return self.stage_id is None

    @classmethod
    def pour_stage(cls, stage):
        return cls.objects.filter(Q(stage__isnull=True) | Q(stage=stage))

    def clean(self):
        if self.est_du_cours:
            return
        if self.partie != self.Partie.THEME:
            raise ValidationError({"partie": "Un chapitre créé pour un stage appartient au thème (Partie III)."})
        if self.parent_id:
            if self.parent.stage_id != self.stage_id:
                raise ValidationError({"parent": "Le chapitre parent appartient à un autre stage."})
            if self.parent.parent_id:
                raise ValidationError({"parent": "Un seul niveau de sous-chapitres est permis."})
