"""Business logic for sellers and stores."""
from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Seller, Store


@transaction.atomic
def register_as_seller(*, user, display_name: str | None = None, store_data: dict | None = None):
    """Turn ``user`` into a seller and optionally create their first store.

    Runs in a single transaction: if the store cannot be created the seller
    profile and the ``is_seller`` flag are rolled back too.
    """
    existing = Seller.all_objects.select_for_update().filter(user=user).first()
    if existing is not None and not existing.is_deleted:
        raise ValidationError({"detail": "You already are a seller."})

    display_name = display_name or user.username
    if existing is not None:  # previously soft-deleted seller profile
        existing.display_name = display_name
        existing.deleted_at = None
        existing.save(update_fields=["display_name", "deleted_at", "updated_at"])
        seller = existing
    else:
        seller = Seller.objects.create(user=user, display_name=display_name)

    if not user.is_seller:
        user.is_seller = True
        user.save(update_fields=["is_seller"])

    store = None
    if store_data and store_data.get("name"):
        store = Store.objects.create(
            owner=seller,
            name=store_data["name"],
            description=store_data.get("description", ""),
        )
    return seller, store
