from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Q

from core.models import BaseModel
from core.utils import unique_slugify


class Seller(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seller_profile")
    display_name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name or str(self.user)


class Store(BaseModel):
    owner = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="stores")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True, allow_unicode=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="stores/", blank=True, null=True)
    # Public contact / profile details
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_live_store_name",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, fallback="store")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StoreAddress(BaseModel):
    """Physical address of a store (a store can have several, one primary)."""

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=80, blank=True, help_text="e.g. Main shop, Warehouse")
    line1 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["store"],
                condition=Q(is_primary=True, deleted_at__isnull=True),
                name="uniq_primary_address_per_store",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.is_primary:
            StoreAddress.objects.filter(store_id=self.store_id, is_primary=True).exclude(pk=self.pk).update(
                is_primary=False
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.store_id}: {self.city}, {self.line1}"


class StoreItem(BaseModel):
    """A product variant offered by a store, with the store's own price and stock."""

    store = models.ForeignKey("marketplace.Store", on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.PROTECT, related_name="store_items")
    sku = models.CharField(max_length=64, help_text="A unique identifier for this product in the store")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    # Simple per-offer discount: the buyer pays price * (100 - discount_percent) / 100.
    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(discount_percent__lte=100), name="storeitem_discount_0_100"),
            # Soft-deleted items must not block re-listing the same variant/SKU.
            models.UniqueConstraint(
                fields=["store", "variant"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_store_variant",
            ),
            models.UniqueConstraint(
                fields=["sku"],
                condition=Q(deleted_at__isnull=True),
                name="uniq_live_storeitem_sku",
            ),
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.store.name} · {self.variant} · {self.sku}"

    @property
    def final_price(self) -> Decimal:
        """Price after the store's discount, rounded to 2 decimals."""
        price = Decimal(self.price)
        if not self.discount_percent:
            return price
        discounted = price * (Decimal(100) - Decimal(self.discount_percent)) / Decimal(100)
        return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
