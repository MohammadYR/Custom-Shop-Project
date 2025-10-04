from django.contrib import admin

class SoftDeleteAdminMixin(admin.ModelAdmin):
    actions = ["soft_delete_selected", "restore_selected"]

    @admin.action(description="Soft delete selected")
    def soft_delete_selected(self, request, queryset):
        
        queryset.delete()  # soft

    @admin.action(description="Restore selected")
    def restore_selected(self, request, queryset):
        queryset.restore()

# استفاده:
# @admin.register(YourModel)
# class YourModelAdmin(SoftDeleteAdminMixin): pass