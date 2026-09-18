from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def sync_profile_from_user(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(
            user=instance,
            email=instance.email,
        )
    else:
        Profile.objects.filter(user=instance).update(
            email=instance.email,
        )
