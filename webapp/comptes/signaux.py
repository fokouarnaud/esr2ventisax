from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_profil(sender, instance, created, raw=False, **kwargs):
    """Profil créé pour tout compte ; le rôle est déduit sans retoucher les droits déjà posés."""
    if created and not raw:
        from .droits import role_deduit
        from .models import Profil

        if not Profil.objects.filter(user=instance).exists():
            Profil(user=instance, role=role_deduit(instance)).save(synchroniser=False)
