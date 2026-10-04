import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Product list filters: ``?category=&category_slug=&min_price=&max_price=&in_stock=&store=``."""

    category = django_filters.UUIDFilter(field_name="category_id")
    category_slug = django_filters.CharFilter(field_name="category__slug")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    store = django_filters.UUIDFilter(method="filter_store", label="Offered by store (id)")

    class Meta:
        model = Product
        fields = ["category", "category_slug", "is_active", "min_price", "max_price", "in_stock", "store"]

    def filter_in_stock(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(total_stock__gt=0) if value else queryset.filter(total_stock=0)

    def filter_store(self, queryset, name, value):
        return queryset.filter(
            variants__store_items__store_id=value,
            variants__store_items__deleted_at__isnull=True,
        ).distinct()
