from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import User, Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created, **kwargs):
    """
    Creates a Profile for a User when the User is created.

    Listens for the post_save signal on User, and creates a Profile
    with the User and their full name if the User is created.
    """
    if created:
        Profile.objects.create(user=instance, full_name=instance.get_full_name())

@receiver(post_save, sender=User)
def normalize_user_fields(sender, instance: User, **kwargs):

    """
    Normalizes the username and email fields of a User to lowercase
    after the User is saved.

    Listens for the post_save signal on User, and normalizes the
    username and email fields to lowercase if they are set and not
    already in lowercase. If the fields are normalized, the User
    instance is updated with the normalized fields.

    This is done to ensure that usernames and email addresses are
    case-insensitive, since they are used to identify users for
    authentication and other purposes.
    """
    changed = False
    if instance.email and instance.email != instance.email.lower():
        instance.email = instance.email.lower(); changed = True
    if instance.username and instance.username != instance.username.lower():
        instance.username = instance.username.lower(); changed = True
    if changed:
        User.objects.filter(pk=instance.pk).update(email=instance.email, username=instance.username)
