from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_profil(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        from .models import Profil

        Profil.objects.get_or_create(user=instance)
