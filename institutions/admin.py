from django.contrib import admin
from institutions.models import Institution



@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Institution model.
    Allows superusers to manage educational institutions through the admin panel.
    """

    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
