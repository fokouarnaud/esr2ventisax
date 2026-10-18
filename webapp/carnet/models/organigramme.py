from django.core.exceptions import ValidationError
from django.db import models

from .base import ModeleDeStage


class NoeudOrganigramme(ModeleDeStage):
    """Nœud de l'organigramme (A25) : le nom est facultatif, certaines entreprises refusent sa publication."""

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="enfants")
    poste = models.CharField(max_length=150)
    nom = models.CharField(max_length=150, blank=True)
    est_stagiaire = models.BooleanField("poste du stagiaire", default=False)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "nœud d'organigramme"
        verbose_name_plural = "organigramme"
        ordering = ["ordre", "poste"]

    def __str__(self):
        return self.poste

    def clean(self):
        if self.est_stagiaire:
            autres = NoeudOrganigramme.objects.filter(stage_id=self.stage_id, est_stagiaire=True).exclude(pk=self.pk)
            if autres.exists():
                raise ValidationError({"est_stagiaire": "Un seul poste de stagiaire par organigramme."})
        ancetre = self.parent
        while ancetre is not None:
            if ancetre.pk == self.pk:
                raise ValidationError({"parent": "Ce parent créerait une boucle dans l'organigramme."})
            ancetre = ancetre.parent
