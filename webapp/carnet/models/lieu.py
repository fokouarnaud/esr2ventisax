import math

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .base import ModeleDeStage

RAYON_TERRE_M = 6_371_000
RAYON_RATTACHEMENT_M = 200


def distance_m(lat1, lon1, lat2, lon2):
    """Distance orthodromique (formule de haversine), en mètres."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * RAYON_TERRE_M * math.asin(math.sqrt(a))


class Lieu(ModeleDeStage):
    class Type(models.TextChoices):
        SIEGE = "siege", "Siège de l'entreprise"
        CHANTIER = "chantier", "Chantier"
        FOURNISSEUR = "fournisseur", "Fournisseur"
        AUTRE = "autre", "Autre"

    nom = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.CHANTIER)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    reperes = models.TextField("repères (ex. face pharmacie…, après le carrefour…)", blank=True)
    ville = models.CharField(max_length=100, blank=True)
    quartier = models.CharField(max_length=150, blank=True)
    niveaux = models.CharField("niveaux du bâtiment", max_length=30, blank=True, help_text="Ex. R+8 (chantier).")

    class Meta:
        verbose_name_plural = "lieux"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    @classmethod
    def le_plus_proche(cls, stage, latitude, longitude):
        """Lieu du stage le plus proche s'il est à moins de 200 m, sinon None."""
        candidats = [(distance_m(latitude, longitude, l.latitude, l.longitude), l) for l in cls.objects.filter(stage=stage)]
        candidats = [c for c in candidats if c[0] <= RAYON_RATTACHEMENT_M]
        return min(candidats, key=lambda c: c[0])[1] if candidats else None
