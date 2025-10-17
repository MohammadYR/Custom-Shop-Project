from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class SoftDeleteAdminMixin(admin.ModelAdmin):
    """Common helpers for models that implement BaseModel soft deletes."""

    actions = ("soft_delete_selected", "restore_selected", "hard_delete_selected")
    soft_delete_filter = ("deleted_at",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if hasattr(self.model, "all_objects"):
            return self.model.all_objects.all()
        return queryset

    def get_list_display(self, request):
        display = list(super().get_list_display(request))
        if hasattr(self.model, "deleted_at") and "deleted_at" not in display:
            display.append("deleted_at")
        return tuple(display)

    def get_list_filter(self, request):
        filters = list(super().get_list_filter(request))
        if hasattr(self.model, "deleted_at") and "deleted_at" not in filters:
            filters.extend(f for f in self.soft_delete_filter if f not in filters)
        return tuple(filters)

    @admin.action(description=_("Soft delete selected"))
    def soft_delete_selected(self, request, queryset):
        queryset.delete()

    @admin.action(description=_("Restore selected"))
    def restore_selected(self, request, queryset):
        queryset.restore()

    @admin.action(description=_("Hard delete selected"))
    def hard_delete_selected(self, request, queryset):
        queryset.hard_delete()


# Example:
# @admin.register(YourModel)
# class YourModelAdmin(SoftDeleteAdminMixin): ...
