import re
import unicodedata

from django.core.exceptions import ValidationError
from django.db import models

from .base import ModeleDeStage


def _ascii_minuscule(mot):
    mot = unicodedata.normalize("NFKD", mot).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", mot.lower())


class Reference(ModeleDeStage):
    class Type(models.TextChoices):
        NORME = "norme", "Norme / DTU"
        OUVRAGE = "ouvrage", "Ouvrage"
        NOTICE = "notice", "Notice fabricant"
        WEB = "web", "Site web"
        ORAL = "oral", "Communication orale"

    type = models.CharField(max_length=10, choices=Type.choices, default=Type.OUVRAGE)
    auteur = models.CharField(max_length=250, blank=True, help_text="« Nom, Prénom » ou organisme.")
    titre = models.CharField(max_length=300)
    annee = models.PositiveIntegerField("année", null=True, blank=True)
    editeur = models.CharField("éditeur", max_length=200, blank=True)
    url = models.URLField(blank=True)
    cle_bibtex = models.CharField("clé BibTeX", max_length=80, blank=True, editable=False)

    class Meta:
        verbose_name = "référence"
        ordering = ["auteur", "annee"]
        constraints = [models.UniqueConstraint(fields=["stage", "cle_bibtex"], name="cle_bibtex_unique_par_stage")]

    def __str__(self):
        return f"{self.auteur or self.titre} ({self.annee or 's.d.'})"

    def save(self, *args, **kwargs):
        if not self.cle_bibtex:
            self.cle_bibtex = self._cle_libre()
        super().save(*args, **kwargs)

    def _cle_libre(self):
        source = self.auteur.split(",")[0] if self.auteur else self.titre
        mots = [_ascii_minuscule(m) for m in source.split()]
        base = next((m for m in mots if m), "ref") + (str(self.annee) if self.annee else "")
        prises = set(Reference.objects.filter(stage_id=self.stage_id).values_list("cle_bibtex", flat=True))
        if base not in prises:
            return base
        suffixe = "b"
        while base + suffixe in prises:
            suffixe = chr(ord(suffixe) + 1)
        return base + suffixe


class DonneeTechnique(ModeleDeStage):
    """Chiffre traçable (A28) : un relevé prouvé par une note, ou une valeur de référence sourcée."""

    class Nature(models.TextChoices):
        RELEVE = "releve", "Relevé sur le terrain"
        REFERENCE = "reference", "Valeur de référence"

    grandeur = models.CharField(max_length=200)
    valeur = models.DecimalField(max_digits=14, decimal_places=4)
    unite = models.CharField("unité", max_length=30)
    nature = models.CharField(max_length=10, choices=Nature.choices)
    date = models.DateField()
    rubrique = models.ForeignKey("carnet.Rubrique", on_delete=models.SET_NULL, null=True, blank=True)
    entree = models.ForeignKey("carnet.EntreeJournal", on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="note de journal")
    reference = models.ForeignKey(Reference, on_delete=models.RESTRICT, null=True, blank=True,
                                  verbose_name="source")

    class Meta:
        verbose_name = "donnée technique"
        verbose_name_plural = "données techniques"
        ordering = ["grandeur"]

    def __str__(self):
        return f"{self.grandeur} = {self.valeur.normalize()} {self.unite}"

    def clean(self):
        if self.nature == self.Nature.REFERENCE and not self.reference_id:
            raise ValidationError({"reference": "Une valeur de référence exige sa source."})
        if self.nature == self.Nature.RELEVE and not self.entree_id:
            raise ValidationError({"entree": "Un relevé doit être rattaché à la note qui le prouve."})


class Abreviation(ModeleDeStage):
    sigle = models.CharField(max_length=30)
    signification = models.CharField(max_length=250)

    class Meta:
        verbose_name = "abréviation"
        ordering = ["sigle"]
        constraints = [models.UniqueConstraint(fields=["stage", "sigle"], name="sigle_unique_par_stage")]

    def __str__(self):
        return self.sigle
