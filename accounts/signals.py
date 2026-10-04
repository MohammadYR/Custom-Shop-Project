from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Address, Profile, User


@receiver(post_save, sender=User, dispatch_uid="accounts.create_profile")
def create_profile(sender, instance: User, created, **kwargs):
    """Create a Profile for every new User."""
    if created:
        Profile.objects.create(user=instance, full_name=instance.get_full_name())


@receiver(pre_save, sender=User, dispatch_uid="accounts.normalize_user_fields")
def normalize_user_fields(sender, instance: User, **kwargs):
    """Lower-case username/email *before* saving.

    Doing it after save (as before) meant "Ali" and "ali" could both pass the
    unique check and then collide with an IntegrityError on the second update.
    An empty phone number is stored as NULL so several users may omit it.
    """
    if instance.email:
        instance.email = instance.email.strip().lower()
    if instance.username:
        instance.username = instance.username.strip().lower()
    if instance.phone_number is not None and not instance.phone_number.strip():
        instance.phone_number = None


@receiver(pre_save, sender=Address, dispatch_uid="accounts.ensure_single_default_address")
def ensure_single_default_address(sender, instance: Address, **kwargs):
    """Saving an address with is_default=True un-sets the user's previous default."""
    if instance.user_id and instance.is_default:
        Address.objects.filter(user_id=instance.user_id, is_default=True).exclude(pk=instance.pk).update(
            is_default=False
        )
