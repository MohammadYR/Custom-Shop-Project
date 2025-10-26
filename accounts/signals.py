from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import User, Profile, Address, OTP
from .tasks import send_otp_email_task, send_otp_sms_task

@receiver(post_save, sender=User, dispatch_uid="accounts.create_profile")
def create_profile(sender, instance: User, created, **kwargs):
    """
    Creates a Profile for a User when the User is created.

    Listens for the post_save signal on User, and creates a Profile
    with the User and their full name if the User is created.
    """
    if created:
        Profile.objects.create(user=instance, full_name=instance.get_full_name())

@receiver(post_save, sender=User, dispatch_uid="accounts.normalize_user_fields")
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


@receiver(pre_save, sender=Address, dispatch_uid="accounts.ensure_single_default_address")
def ensure_single_default_address(sender, instance: Address, **kwargs):
    """
    Enforce a single default address per user at the application level.

    If an Address is being saved with is_default=True, unset is_default on
    all of the user's other addresses. Complements the database constraint
    and improves UX by preventing IntegrityErrors.
    """
    if not instance.user_id:
        return
    if instance.is_default:
        Address.objects.filter(user=instance.user, is_default=True).exclude(pk=instance.pk).update(is_default=False)


@receiver(post_save, sender=OTP, dispatch_uid="accounts.send_otp_on_create")
def send_otp_on_create(sender, instance: OTP, created, **kwargs):
    """
    When an OTP is created, send it via the configured channel.
    Uses Celery tasks if available; falls back to direct call if broker is unavailable.
    """
    if not created:
        return

    message = f"Your verification code is: {instance.code}"
    try:
        if instance.channel == "email":
            send_otp_email_task.delay(instance.target, message)
        else:
            # default to sms
            send_otp_sms_task.delay(instance.target, message)
    except Exception:
        # Fallback to synchronous execution in environments without broker
        if instance.channel == "email":
            send_otp_email_task(instance.target, message)
        else:
            send_otp_sms_task(instance.target, message)
