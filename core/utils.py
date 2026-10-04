from django.utils.text import slugify


def unique_slugify(instance, value, *, slug_field: str = "slug", fallback: str = "item") -> str:
    """Return a slug for ``value`` that is unique for ``instance``'s model.

    - Keeps non-ASCII letters (``allow_unicode=True``), so Persian names do not
      collapse into an empty slug.
    - Appends ``-2``, ``-3``... on collisions. Soft-deleted rows are included in
      the check because the slug column is unique at the database level.
    """
    model = type(instance)
    max_length = model._meta.get_field(slug_field).max_length
    base = slugify(value or "", allow_unicode=True)[:max_length].strip("-") or fallback

    manager = getattr(model, "all_objects", model._default_manager)
    queryset = manager.all()
    if instance.pk and not instance._state.adding:
        queryset = queryset.exclude(pk=instance.pk)

    candidate = base
    counter = 2
    while queryset.filter(**{slug_field: candidate}).exists():
        suffix = f"-{counter}"
        candidate = f"{base[: max_length - len(suffix)]}{suffix}"
        counter += 1
    return candidate
