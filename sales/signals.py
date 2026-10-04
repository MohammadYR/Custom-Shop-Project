from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Cart


@receiver(post_save, sender=get_user_model(), dispatch_uid="sales.ensure_cart_for_new_user")
def ensure_cart_for_new_user(sender, instance, created, **kwargs):
    """Create a Cart for each newly-created user (idempotent)."""
    if created:
        Cart.objects.get_or_create(user=instance)


# Order status side effects (restock, payment status, emails) used to live in a
# pre_save signal that fired on *every* transition into CANCELLED, so
# CANCELLED -> PENDING -> CANCELLED restocked twice. They now live in
# sales.services (mark_order_paid / cancel_order), which enforce the state machine.
