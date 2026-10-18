import uuid

from django.db import models


class ModeleBase(models.Model):
    """Clé UUID (A21) et horodatage communs à tous les modèles métier."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ModeleDeStage(ModeleBase):
    """Entité propre à un stage : la clé `stage` sert au cloisonnement (A1)."""

    stage = models.ForeignKey("carnet.Stage", on_delete=models.CASCADE, related_name="%(class)s_set")

    class Meta:
        abstract = True
