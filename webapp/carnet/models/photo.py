import uuid

from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import Q

from .base import ModeleDeStage
from .rubrique import Rubrique


def chemin_photo(instance, _nom_origine):
    return f"photos/{instance.stage_id}/{instance.pk}.jpg"


class Photo(ModeleDeStage):
    class Destination(models.TextChoices):
        A_TRIER = "a_trier", "À trier"
        CORPS = "corps", "Corps du rapport"
        ANNEXE = "annexe", "Annexe"
        PREUVE = "preuve", "Preuve seulement"

    fichier = models.ImageField(upload_to=chemin_photo)
    taille_octets = models.PositiveIntegerField(default=0, editable=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    prise_le = models.DateTimeField("prise le", null=True, blank=True)
    legende = models.CharField("légende", max_length=250, blank=True)
    slug = models.SlugField(max_length=60, blank=True, help_text="Nom du fichier dans le rapport : img/fig_<slug>.jpg")
    destination = models.CharField(max_length=10, choices=Destination.choices, default=Destination.A_TRIER)
    entree = models.ForeignKey("carnet.EntreeJournal", on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="photos", verbose_name="note de journal")
    lieu = models.ForeignKey("carnet.Lieu", on_delete=models.SET_NULL, null=True, blank=True)
    rubriques = models.ManyToManyField(Rubrique, blank=True, verbose_name="étiquettes")

    class Meta:
        ordering = ["-prise_le", "-cree_le"]
        constraints = [
            models.UniqueConstraint(fields=["stage", "slug"], condition=~Q(slug=""), name="slug_photo_unique_par_stage")
        ]

    def __str__(self):
        return self.legende or self.slug or str(self.pk)

    @classmethod
    def ajouter(cls, stage, fichier, latitude=None, longitude=None, **champs):
        """Compresse, vérifie le quota puis enregistre (A5, A33). Le GPS EXIF prime sur celui du navigateur."""
        from carnet.services.images import traiter_image
        from carnet.services.quota import verifier_quota

        image = traiter_image(fichier)
        verifier_quota(stage, len(image.contenu))
        photo = cls(
            id=uuid.uuid4(),
            stage=stage,
            latitude=image.latitude if image.latitude is not None else latitude,
            longitude=image.longitude if image.longitude is not None else longitude,
            prise_le=image.prise_le,
            taille_octets=len(image.contenu),
            **champs,
        )
        with transaction.atomic():
            photo.fichier.save(f"{photo.pk}.jpg", ContentFile(image.contenu), save=False)
            photo.save()
        return photo

    def problemes_export(self):
        if self.destination not in (self.Destination.CORPS, self.Destination.ANNEXE):
            return []
        problemes = []
        if not self.slug:
            problemes.append("slug manquant")
        if not self.legende:
            problemes.append("légende manquante")
        return problemes
