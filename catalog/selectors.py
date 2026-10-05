"""Read-side helpers for the catalog (HackSoft "selectors")."""

from django.db.models import (
    Avg,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    IntegerField,
    Min,
    OuterRef,
    Prefetch,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from .models import Product, ProductImage


def _live_store_items():
    from marketplace.models import StoreItem

    return StoreItem.objects.filter(variant__deleted_at__isnull=True, is_active=True, store__is_active=True)


def _store_items_of_product():
    return _live_store_items().filter(variant__product=OuterRef("pk"))


# Same formula as StoreItem.final_price, evaluated in SQL.
FINAL_PRICE = ExpressionWrapper(
    F("price") * (Value(100) - F("discount_percent")) / Value(100),
    output_field=DecimalField(max_digits=12, decimal_places=2),
)


def product_offers(product):
    """Active, in-stock store offers for one product, cheapest first."""
    return (
        _live_store_items()
        .filter(variant__product=product, stock__gt=0)
        .select_related("store", "variant")
        .annotate(final_price_db=FINAL_PRICE)
        .order_by("final_price_db", "created_at")
    )


def product_list_queryset():
    """Products annotated with stock, best price and rating.

    Subqueries are used instead of joins so the aggregates do not multiply
    each other (store items x reviews).
    """
    from reviews.models import ProductReview

    items = _store_items_of_product()
    stock = items.order_by().values("variant__product").annotate(s=Sum("stock")).values("s")
    # Cheapest price a buyer actually pays, i.e. after each store's discount.
    best_price = (
        items.filter(stock__gt=0).order_by().values("variant__product").annotate(p=Min(FINAL_PRICE)).values("p")
    )
    reviews = ProductReview.objects.filter(product=OuterRef("pk")).order_by().values("product")
    rating = reviews.annotate(a=Avg("rating")).values("a")
    reviews_count = reviews.annotate(c=Count("id")).values("c")

    return (
        Product.objects.select_related("category")
        .prefetch_related(Prefetch("images", queryset=ProductImage.objects.order_by("sort_order", "created_at")))
        .annotate(
            total_stock=Coalesce(Subquery(stock, output_field=IntegerField()), Value(0)),
            best_price=Subquery(best_price, output_field=DecimalField(max_digits=12, decimal_places=2)),
            rating=Subquery(rating, output_field=DecimalField(max_digits=3, decimal_places=2)),
            reviews_count=Coalesce(Subquery(reviews_count, output_field=IntegerField()), Value(0)),
        )
    )
